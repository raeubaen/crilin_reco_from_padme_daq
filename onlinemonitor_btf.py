import os
import argparse
import time
import glob
import sys
import signal

from subprocess import Popen, PIPE, STDOUT

from multiprocessing import Process

parser = argparse.ArgumentParser(description='Online monitor and reconstruction for crilin')
parser.add_argument('nrun', type=int, help='nrun - please unambigous')
parser.add_argument('--outfolder', type=str, help='outfolder', default="/home/mu2e/onlinemonitor/outonline")
parser.add_argument('--startn', type=int, help='skip n fragments', default=0)
parser.add_argument('--cat', type=int, help='concatenate last .cat file when startn!=0', default=1)
parser.add_argument('--sleep', type=float, help='sleep between fragments', default=4)

args = parser.parse_args()
v = vars(args)
print(v)
vars().update(v)

work_dir = "/home/mu2e"

n = startn

infile_dir = glob.glob(f"{work_dir}/DAQ/rawdata/run_{nrun:07d}_*")[0]
infile_name_base = infile_dir.split(f"{work_dir}/DAQ/rawdata/")[1]
run_outfolder = f"{outfolder}/run_{nrun}"
os.system(f"mkdir -p {run_outfolder}")

while True:
    try:
      print(f"trying to reconstruct fragment {n}")
      next_file = f"{work_dir}/DAQ/rawdata/{infile_name_base}/{infile_name_base}_lvl1_00_{n+1:03d}.root"
      current_file = f"{work_dir}/DAQ/rawdata/{infile_name_base}/{infile_name_base}_lvl1_00_{n:03d}.root"
      if os.path.isfile(next_file):
        code = os.system(f"{work_dir}/DAQ/CopyReadRoot.exe -i {current_file} -o {run_outfolder}/out_temp_{n}.root")
        if code!=0: break
      else:
        print(f"fragment {n+1} not yet present, so {n}th not closed - skipping")
        time.sleep(sleep)
        continue

      code = os.system(f"sshpass -p Evale2.71828 scp {run_outfolder}/out_temp_{n}.root rgargiul@lxplus.cern.ch:/eos/user/e/edimeco/BTF/crilin/onlinemonitor_btf_output/run_{nrun}/out_temp_{n}.root")
      if code!=0: break

      print(f"{sleep} seconds to kill with ctrl-c")
      time.sleep(sleep)

      print(f"plot-ing fragment {n}")
      code = os.system(f"root -q -l -b -x \"plot_monitor.C(\\\"{run_outfolder}/*.root\\\", \\\"{run_outfolder}/out_temp_{n}.root\\\")\"")
      if code!=0: break

      print("\n\n")

      n+=1
    except KeyboardInterrupt:
      break
