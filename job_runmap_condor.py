import os
import sys
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Run submit for condor')

parser.add_argument('mapfile', type=str, help='File with the map')

args = parser.parse_args()
v = vars(args)
print(v)
vars().update(v)

def reco(row):
  cmd = f"python3 submit_condor_btf_2024.py {row.nrun} {row.label}"
  print(cmd)
  os.system(cmd)

df = pd.read_csv(mapfile, sep=" ", header=None)
df.columns = ["nrun", "label"]

print(df)

df.apply(lambda row: reco(row), axis=1)
