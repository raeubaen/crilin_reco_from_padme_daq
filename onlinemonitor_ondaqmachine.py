import os, sys
import argparse
import time
import glob

from subprocess import Popen, PIPE, STDOUT

from multiprocessing import Process

parser = argparse.ArgumentParser(description='Online monitor and reconstruction for crilin')
parser.add_argument('nrun', type=int, help='nrun - please unambigous')
parser.add_argument('setup', type=str, help='name of the setup in json config (default: electrons)')
parser.add_argument('--startn', type=int, help='skip n fragments', default=0)
parser.add_argument('--sleep', type=float, help='sleep between fragments', default=1)

args = parser.parse_args()
v = vars(args)
print(v)
vars().update(v)

'''
in define_envs.sh (example!)

export TOTAL_FRAGMENTS_IN_PERIOD=1
export PROCESS_FRAGMENTS_IN_PERIOD=1
export DAQ_MACHINE_DAQ_FOLDER="/home/crilin/crilinDAQ"
export DAQ_MACHINE_ONLINE_FOLDER="/home/crilin/crilinRECO/default_crilin_reco_from_padme_daq"
export DAQ_MACHINE_UNPACKED_FOLDER="${DAQ_MACHINE_DAQ_FOLDER}/local/rawdata/"
'''

unpacked_dir = os.getenv("DAQ_MACHINE_UNPACKED_FOLDER")
script_dir = os.getenv("DAQ_MACHINE_ONLINE_FOLDER")

total_fragments_in_period = os.getenv("TOTAL_FRAGMENTS_IN_PERIOD")
process_fragments_in_period = os.getenv("PROCESS_FRAGMENTS_IN_PERIOD")

if any(x is None for x in (unpacked_dir, script_dir, total_fragments_in_period, process_fragments_in_period)):
  print(f"Define env sourcing needed!")
  sys.exit(1)
  
n = startn

try:
  infile_dir = glob.glob(f"{unpacked_dir}/run_{nrun:07d}_*")[0]
except IndexError:
  print(f"Run not initialized!, path {unpacked_dir}/run_{nrun:07d}_* not found")
  sys.exit(1)
infile_name_base = infile_dir.split(f"{unpacked_dir}/")[1]

while True:
    try:
      print(f"trying to reconstruct fragment {n}")

      next_file = f"{unpacked_dir}/{infile_name_base}/{infile_name_base}_lvl1_00_{n+1:03d}.root"
      current_file = f"{unpacked_dir}/{infile_name_base}/{infile_name_base}_lvl1_00_{n:03d}.root"
      if os.path.isfile(next_file):
        print(f"Found fragment {n}, with TOTAL_FRAGMENTS_IN_PERIOD={total_fragments_in_period}, PROCESS_FRAGMENTS_IN_PERIOD={process_fragments_in_period}")
        if (n % int(total_fragments_in_period)) < int(process_fragments_in_period):
          pass
        else: continue
        print("Going on, processing")
        code = os.system(f"{script_dir}/copy_to_eos_and_create_lock_file.sh {current_file} {setup} 2>&1 | tee /tmp/onlinelogs_{nrun}_{n}.txt")
        print("------------------------- reco done ----------------------------")
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
