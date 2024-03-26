import glob
import ROOT
import os

folders = glob.glob("/eos/user/e/edimeco/BTF/crilin/output/*")

for folder in folders:
  try:
    ncry = int(folder.split("cry")[1])
    label = folder.split("/")[-1].split("cry")[0].split("_")[1]
  except IndexError:
    continue
  print(ncry, label)
  c = ROOT.TChain("tree")
  c.Add(f"{folder}/*.root")
  h = ROOT.TH1F(f"h_{ncry}_{label}", f"charge_cry{ncry}_{label}", 100, 5, 105)
  cnv = ROOT.TCanvas()
  c.Draw(f"(charge[0][{ncry*2}]+charge[0][{ncry*2+1}])/2>>h_{ncry}_{label}")
  print(h.Integral(), h.GetMean())
  f = ROOT.TF1("func", "gaus(0)+gaus(3)", 10, 65);
  f.SetParameters(500, 25, 10, 50, 50, 7);
  if label=="87V": f.SetParameters(500, 17, 10, 30, 50, 7);
  h.Fit(f, "R")
  h.SetTitle(f"{label} - Cry: {ncry} - Mean Charge: {f.GetParameter(1)} +/- {f.GetParError(1)} pC")
  cnv.SaveAs(f"../plots/cnv_{label}_{ncry}.root")
  cnv.SaveAs(f"../plots/cnv_{label}_{ncry}.pdf")

os.system("pdfunite ../plots/*.pdf all.pdf")
