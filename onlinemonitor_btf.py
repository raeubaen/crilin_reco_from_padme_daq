import os
import argparse
import time
import glob

from subprocess import Popen, PIPE, STDOUT

from multiprocessing import Process

parser = argparse.ArgumentParser(description='Online monitor and reconstruction for crilin')
parser.add_argument('nrun', type=int, help='nrun - please unambigous')
parser.add_argument('conf', type=str, help='name of the config in {reco_dir}/confs/<conf>.json')
parser.add_argument('--startn', type=int, help='skip n fragments', default=0)
parser.add_argument('--sleep', type=float, help='sleep between fragments', default=1)

args = parser.parse_args()
v = vars(args)
print(v)
vars().update(v)

work_dir = "/home/crilin/crilinDAQ"
script_dir = "/home/crilin/crilinRECO/default_crilin_reco_from_padme_daq"
n = startn

infile_dir = glob.glob(f"{work_dir}/local/rawdata/run_{nrun:07d}_*")[0]
infile_name_base = infile_dir.split(f"{work_dir}/local/rawdata/")[1]

while True:
    try:
      print(f"trying to reconstruct fragment {n}")
      next_file = f"{work_dir}/local/rawdata/{infile_name_base}/{infile_name_base}_lvl1_00_{n+1:03d}.root"
      current_file = f"{work_dir}/local/rawdata/{infile_name_base}/{infile_name_base}_lvl1_00_{n:03d}.root"
      if os.path.isfile(next_file):
        code = os.system(f"source {script_dir}/process_single_fragment.sh {current_file} {conf} 2>&1 | tee /tmp/onlinelogs_{nrun}_{n}.txt")
        if code!=0: break
      else:
        print(f"fragment {n+1} not yet present, so {n}th not closed - skipping and sleeping for {sleep}s")
        time.sleep(sleep)
        continue

      print(f"you have {sleep}s to kill me with Ctrl-C")
      time.sleep(sleep)

      print("\n\n")

      n+=1
    except KeyboardInterrupt:
      break
