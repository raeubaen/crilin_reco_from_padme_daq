#!/usr/bin/env python3

import os
import glob
import csv
import argparse
import subprocess
from pathlib import Path

DEFAULT_RUNS = {
    #386: 100,
    #395: 20,
    #401: 34,
    #403: 52,
    #404: 74,
    413: 120,
    429: 65,
#    435: 10,
}

BASE = "/eos/experiment/muoncollider/data/crilin/h2-2026/DataTree_dqm"
OUT_BASE = Path(os.environ["RE_RECO_FOLDER"])


def sh(cmd, dry):
    print(cmd)
    if not dry:
        subprocess.run(["bash", "-lc", cmd], check=True)


def read_runs(csvfile):
    if csvfile is None:
        return DEFAULT_RUNS

    runs = {}
    with open(csvfile) as f:
        for row in csv.DictReader(f):
            runs[int(row["run"])] = int(row["energy"])

    return runs


parser = argparse.ArgumentParser()
parser.add_argument(
    "--dry",
    action="store_true",
    help="stampa i comandi senza eseguirli"
)
parser.add_argument(
    "--csv",
    help="file CSV con colonne run,energy"
)

args = parser.parse_args()

RUNS = read_runs(args.csv)


for run, energy in RUNS.items():

    matches = glob.glob(f"{BASE}/run_{run:07d}_*")

    if len(matches) != 1:
        raise RuntimeError(
            f"Run {run}: trovati {len(matches)} match {matches}"
        )

    runname = os.path.basename(matches[0]).replace("run_", "", 1)
    outdir = OUT_BASE / f"run_{runname}"

    print(f"\n=== {runname} ({energy} GeV) ===")

    for tag in ("pedestals", "electrons"):

        sh(f"source re-reco.sh {runname} {tag}", args.dry)

        outfile = f"cat_{runname}_{energy}GeV_{tag}.root"

        sh(
            f"cd {outdir} && hadd -f {outfile} 0*.root",
            args.dry
        )

        if not args.dry:
            out = outdir / outfile
            if not out.exists() or out.stat().st_size == 0:
                raise RuntimeError(f"hadd fallita: {out}")

        sh(f"cd {outdir} && rm 0*.root", args.dry)


print("\nDone.")
