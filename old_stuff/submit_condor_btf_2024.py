import os
import sys
import argparse
import glob

parser = argparse.ArgumentParser(description='Online monitor and reconstruction for crilin July')

parser.add_argument('nrun', type=str, help='nrun')
parser.add_argument('label', type=str, help='label', default="")
parser.add_argument('--lyso', type=str, help="Lyso with series", default=0)
parser.add_argument('--lysoparallel', type=str, help="Lyso with parallel", default=0)
parser.add_argument('--scintsipmparallel', type=str, help="scint with parallel sipms", default=0)
parser.add_argument('--rootinputfolder', type=str, help="Root input folder", default='/eos/user/e/edimeco/BTF/crilin/onlinemonitor_btf_output')
parser.add_argument('--condorfolder', type=str, help="Folder where logs etc. are saved", default='../jobs')
parser.add_argument('--rootoutfolder', type=str, help="Root/json out folder", default='/eos/user/e/edimeco/BTF/crilin/output/')

args = parser.parse_args()
v = vars(args)
print(v)
vars().update(v)

v["njobs"] = len(glob.glob(f"{rootinputfolder}/run_{nrun}/out_temp_*.root"))
v["codedir"] = os.getcwd()
for key in ["rootinputfolder", "condorfolder", "rootoutfolder"]:
  v[key] = os.path.abspath(v[key])

v["script"] = "condorjob_lyso.sh" if lyso else "condorjob.sh"
if lysoparallel: v["script"] = "condorjob_lyso_parallel.sh"
if scintsipmparallel: v["script"] = "condorjob_scint_sipmparallel.sh"

os.system(f"mkdir {condorfolder}/{nrun}_{label}")
os.system(f"mkdir {condorfolder}/{nrun}_{label}/output")
os.system(f"mkdir {condorfolder}/{nrun}_{label}/error")
os.system(f"mkdir {condorfolder}/{nrun}_{label}/log")
os.system(f"mkdir {rootoutfolder}/{nrun}_{label}")

sub = open("jobsub.condor", "r").read()

for key in v:
  sub = sub.replace(f"${key}", str(v[key]))

f = open(f"{condorfolder}/{nrun}_{label}/jobsub{nrun}.condor", "w")
f.write(sub)
f.close()

os.system(f"condor_submit {condorfolder}/{nrun}_{label}/jobsub{nrun}.condor")
