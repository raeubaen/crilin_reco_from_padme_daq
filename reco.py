import os, json, uproot, argparse, sys, time, ROOT
import awkward as ak
import numpy as np
import reco_functions
import pandas as pd
import plot_functions_in_memory as plot_functions


def retrieve_conf(filename):
  with open(filename, 'r') as f:
    json_dict = json.load(f)
    for detector in json_dict["detectors"]:
      if json_dict["detectors"][detector]["active_ch_list"] == None: json_dict["detectors"][detector]["active_ch_list"] = slice(None)
  return json_dict["tree_name"], json_dict["detectors"]


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
    parser.add_argument("-ct", f"--compression-type", type=str, required=False, help="mcp reco configuration", default="lz4")
    parser.add_argument("-d", f"--data", type=str, required=True, help="csv file with data to plot")
    parser.add_argument("-p", f"--plot-list", type=str, required=True, help="csv file with plot list (mcp and ecal)")
    parser.add_argument("-po", f"--plot-output-folder", type=str, required=True, help="output folder for plots")

    args = parser.parse_args(arguments)

    tree_name, detectors_dict = retrieve_conf(args.detectors_json)

    # open input file
    file = uproot.open(args.input)
    tree = file[tree_name]

    for detector in detectors_dict:
      dd = detectors_dict[detector]
      waves = tree[dd["waves_branch_name"]].array(library="np")
      if len(waves.shape) == 4: waves = waves.reshape(waves.shape[0], waves.shape[1]*waves.shape[2], waves.shape[3])
      map_df = pd.read_csv(dd["map_filename"])
      active_ch_list = (map_df["type"] == detector).tolist()
      waves = waves[:, active_ch_list, :]
      chid_dict = (map_df[coord].to_numpy()[active_ch_list] for coord in ["digi_ch", "global_ch", "board", "chip"])
      if dd["to_be_inverted"]:
        waves = 4096 - waves #must be inverted if the signal are with negative rising slope
      if dd["reco_conf"]["do_centroid"]:
        x_y_z_tuple = (map_df[coord].to_numpy()[active_ch_list] for coord in ["x", "y", "z"])
      else:
        x_y_z_tuple = None

      dd["mask"], dd["reco_dict"] = reco_functions.generic_reco(waves, detector, chid_dict, x_y_z_tuple, **dd["reco_conf"])

    time_merge = time.time()
    mask_global = np.logical_and.reduce((detectors_dict[detector]["mask"] for detector in detectors_dict)) #to be generic
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
    compression_map = {"zlib": uproot.compression.ZLIB(level=1), "lz4": uproot.compression.LZ4(level=1), "none": None}
    with uproot.recreate(f"{args.reco_output_dir}/{args.run}_{args.fragment}_reco.root", compression=compression_map[args.compression_type]) as f:
        tree = f.mktree("tree", branch_types)
        tree.extend(reco_dict)

    print(f"writing reco output took {-time_write + time.time():.1f} s")

if __name__ == '__main__':
    main(sys.argv[1:])
