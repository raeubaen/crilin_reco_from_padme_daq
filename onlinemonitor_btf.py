import os
import argparse
import time
import glob
from subprocess import Popen, PIPE, STDOUT

parser = argparse.ArgumentParser(description='Online monitor and reconstruction for crilin')

parser.add_argument('nrun', type=int, help='nrun - please unambigous')
parser.add_argument('--outfolder', type=str, help='outfolder', default="/home/mu2e/onlinemonitor/outonline")
parser.add_argument('--startn', type=int, help='skip n fragments', default=0)
parser.add_argument('--cat', type=int, help='concatenate last .cat file when startn!=0', default=1)
parser.add_argument('--sleep', type=int, help='sleep between fragments', default=4)

args = parser.parse_args()
v = vars(args)
print(v)
vars().update(v)

work_dir = "/home/mu2e"

process = 0

n = startn

infile_dir = glob.glob(f"{work_dir}/DAQ/rawdata/run_{nrun:07d}_*")[0]
infile_name_base = infile_dir.split(f"{work_dir}/DAQ/rawdata/")[1]

run_outfolder = f"{outfolder}/run_{nrun}"
os.system(f"mkdir -p {run_outfolder}")

while True:
    print(f"trying to reconstruct fragment {n}")
    next_file = f"{work_dir}/DAQ/rawdata/{infile_name_base}/{infile_name_base}_lvl1_00_{n+1:03d}.root"
    current_file = f"{work_dir}/DAQ/rawdata/{infile_name_base}/{infile_name_base}_lvl1_00_{n:03d}.root"
    if os.path.isfile(next_file):
      os.system(f"{work_dir}/DAQ/CopyReadRoot.exe -i {current_file} -o {run_outfolder}/out_temp_{n}.root")
    else:
      print(f"fragment {n+1} not yet present, so {n}th not closed - skipping")
      time.sleep(sleep)
      continue

    print(f"hadd-ing fragment {n}")
    if n==startn:
      if cat and startn>0:
        os.system(f"cp {run_outfolder}/out_cat.root {run_outfolder}/out_cat_old.root")
        os.system(f"cp {run_outfolder}/out_cat.root {run_outfolder}/out_temp.root")
        os.system(f"hadd -f {run_outfolder}/out_cat.root {run_outfolder}/out_temp_{n}.root {run_outfolder}/out_temp.root")
        try:
          print(f"from now yo have {sleep} seconds to kill me")
          time.sleep(sleep)
        except KeyboardInterrupt:
          print("Exiting")
          break
      else:
        os.system(f"cp {run_outfolder}/out_temp_{n}.root {run_outfolder}/out_temp.root")
        os.system(f"cp {run_outfolder}/out_temp_{n}.root {run_outfolder}/out_cat.root")
    else:
      os.system(f"cp {run_outfolder}/out_cat.root {run_outfolder}/out_temp.root")
      os.system(f"hadd -f {run_outfolder}/out_cat.root {run_outfolder}/out_temp_{n}.root {run_outfolder}/out_temp.root")
      try:
        print(f"from now yo have {sleep} seconds to kill me")
        time.sleep(sleep)
      except KeyboardInterrupt:
        print("Exiting")
        break

    print(f"plot-ing fragment {n}")
    Popen(["root", "-q", "-l", "-b", "-x", f"plot_monitor.C(\"{run_outfolder}/out_cat.root\", \"{run_outfolder}/out_temp_{n}.root\")"])

    print("\n\n")

    n+=1
