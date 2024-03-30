import glob
import os

folders = glob.glob("../output/*trk*")

for folder in folders:
  fname = folder.split("/")[-1]
  nrun, _, x, y = fname.split("_")
  if "plus" in x: x = float(x.split("plus")[1].split("X")[0])
  elif "minus" in x: x = -float(x.split("minus")[1].split("X")[0])
  if "plus" in y: y = float(y.split("plus")[1].split("Y")[0])
  elif "minus" in y: y = -float(y.split("minus".split("Y")[0])[1].split("Y")[0])
  os.system(f"./trk_reco.sh {nrun} {x:.2f} {y:.2f} {folder}")

