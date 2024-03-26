import glob
import ROOT
import os

folders = glob.glob("/eos/user/e/edimeco/BTF/crilin/output/*")

print("run volt ncry q_1e q_1e_err chi2 ndf prob")

ROOT.gROOT.LoadMacro("root_logon.C")

for folder in folders:
  try:
    ncry = int(folder.split("cry")[1])
    label = folder.split("/")[-1].split("cry")[0].split("_")[1].replace("V", "")
    run = folder.split("/")[-1].split("cry")[0].split("_")[0]
  except IndexError:
    continue
  c = ROOT.TChain("tree")
  c.Add(f"{folder}/*.root")
  h = ROOT.TH1F(f"h_{ncry}_{label}", f"charge_cry{ncry}_{label}", 100, 5, 105)
  cnv = ROOT.TCanvas()
  c.Draw(f"(charge[0][{ncry*2}]+charge[0][{ncry*2+1}])/2>>h_{ncry}_{label}")
  if label=="91":
    f = ROOT.TF1("func", "gaus(0)+gaus(3)", 12, 60);
    f.SetParameters(500, 25, 10, 50, 50, 7);
  if label=="87":
    f = ROOT.TF1("func", "gaus(0)+gaus(3)", 10, 37);
    f.SetParameters(350, 14, 4, 220, 28, 5);
  f.SetParNames("N (1e)", "Q (1e)", "#sigma_{Q} (1e)", "N (2e)", "Q (2e)", "#sigma_{Q} (2e)")
  h.Fit(f, "RQ")
  h.GetXaxis().SetTitle("Crystal mean charge [pC]")
  h.GetYaxis().SetTitle("Entries / 1 pC")
  print(run, label, ncry, f.GetParameter(1), f.GetParError(1), f.GetChisquare(), f.GetNDF(), f.GetProb())
  h.SetTitle(f"{label}V - Cry: {ncry} - Mean Charge: {f.GetParameter(1):.2f} +/- {f.GetParError(1):.2f} pC")
  cnv.SaveAs(f"../plots/cnv_{label}_{ncry}.root")
  cnv.SaveAs(f"../plots/cnv_{label}_{ncry}.pdf")

os.system("pdfunite ../plots/*.pdf ../plots/all.pdf")
