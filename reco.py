import os, json, uproot, argparse, sys, time, ROOT
import awkward as ak
import numpy as np
import reco_functions
import pandas as pd
import plot_functions_in_memory as plot_functions
import concurrent.futures

def retrieve_conf(filename):
  with open(filename, 'r') as f:
    json_dict = json.load(f)
  return json_dict["global"], json_dict["detectors"]


def main(arguments):
    # start time
    time_start = time.time()

    # input parameters
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-i", f"--input", type=str, required=True, help="input ROOT file with unpacked tree")
    parser.add_argument("-r", f"--run", type=str, required=True, help="run number")
    parser.add_argument("-s", f"--fragment", type=str, required=True, help="fragment number")
    parser.add_argument("-ro", f"--reco-output-dir", type=str, required=True, help="directory for reco output")
    parser.add_argument("-dj", f"--detectors-json", type=str, required=False, help="detectors reco configuration", default="detectors_conf.json")
    parser.add_argument("-ct", f"--compression-type", type=str, required=False, help="compression type", default="zlib")
    parser.add_argument("-d", f"--data", type=str, required=True, help="csv file with data to plot")
    parser.add_argument("-p", f"--plot-list", type=str, required=True, help="csv file with plot list (mcp and ecal)")
    parser.add_argument("-po", f"--plot-output-folder", type=str, required=True, help="output folder for plots")

    args = parser.parse_args(arguments)

    global_dict, detectors_dict = retrieve_conf(args.detectors_json)

    print(f"time to read args and json: {time_start - time.time():.2f}")
    time_open_file = time.time()

    # open input file
    file = uproot.open(args.input, num_workers=10)
    tree = file[global_dict["tree_name"]]

    map_df = pd.read_csv(global_dict["map_filename"])

    print(f"time to open root file and csv: {time_open_file - time.time():.2f}")
    for detector in detectors_dict:
      print(detector)
      dd = detectors_dict[detector]
      time_read_waves = time.time()


      active_row_list = (map_df["type"] == detector).tolist()
      active_branch_ch_list = (map_df["branch_ch"][map_df["type"] == detector]).tolist()


      with concurrent.futures.ThreadPoolExecutor(max_workers=8) as decompr_exec, \
         concurrent.futures.ThreadPoolExecutor(max_workers=8) as interpret_exec:

        waves = tree[dd["waves_branch_name"]].array(
            library="np",
            decompression_executor=decompr_exec,
            interpretation_executor=interpret_exec,
        )

      if len(waves.shape) == 4: waves = waves.reshape(waves.shape[0], waves.shape[1]*waves.shape[2], waves.shape[3])
      waves = waves[:, active_branch_ch_list, :]

      chid_dict = {var: map_df[var].to_numpy()[active_row_list] for var in dd["chid_vars_list"]}
      print(chid_dict)
      if dd["to_be_inverted"]:
        waves = 4096 - waves #must be inverted if the signal are with negative rising slope
      if dd["reco_conf"]["do_centroid"]:
        x_y_z_tuple = (map_df[coord].to_numpy()[active_row_list] for coord in ["x", "y", "z"])
      else:
        x_y_z_tuple = None

      print(f"time to read and pre-process waves: {time_read_waves - time.time():.2f}")
      time_reco = time.time()
      dd["mask"], dd["reco_dict"] = reco_functions.generic_reco(waves, detector, chid_dict, x_y_z_tuple, **dd["reco_conf"])
      print(f"time to reco: {time_reco - time.time():.2f}")

    time_merge = time.time()
    mask_global = np.logical_and.reduce([detectors_dict[detector]["mask"] for detector in detectors_dict]) #to be generic
    reco_dict = {}
    for detector in detectors_dict: reco_dict.update(detectors_dict[detector]["reco_dict"])

    for branch in reco_dict: reco_dict[branch] = reco_dict[branch][mask_global, ...]

    print(f"merging took {-time_merge + time.time():.1f} s")
    print(f"Total time elapsed for reco: {time.time() - time_start:.4f} s")

    '''
    time_plot = time.time()
    plotconf_df = pd.read_csv(args.plot_list, sep=",")
    plotconf_df = plotconf_df.fillna("")

    # os.system(f"cp index.php {outputfolder}")

    ROOT.gROOT.LoadMacro("root_logon.C")

    os.system(f"mkdir {args.plot_output_folder}/prova")
    plotconf_df.apply(lambda row: plot_functions.plot(row, reco_dict, f"{args.plot_output_folder}/prova"), axis=1)

    time_end = time.time()
    print(f"Time elapsed for plotting: {time_end - time_plot:.4f} s")
    '''

    time_write = time.time()

    branch_types = {k: (v.dtype, v.shape[1:]) for k, v in reco_dict.items()}
    compression_map = {"zlib": uproot.compression.ZLIB(level=4), "lz4": uproot.compression.LZ4(level=1), "none": None}
    print(compression_map[args.compression_type])
    with uproot.recreate(f"{args.reco_output_dir}/{args.run}_{args.fragment}_reco.root", compression=compression_map[args.compression_type]) as f:
        tree = f.mktree("tree", branch_types)
        tree.extend(reco_dict)

    print(f"writing reco output took {-time_write + time.time():.1f} s")

if __name__ == '__main__':
    main(sys.argv[1:])
