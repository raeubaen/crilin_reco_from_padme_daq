import glob
import ROOT

folders = glob.glob("/eos/user/e/edimeco/BTF/crilin/output/*")

for folder in folders:
  print(folder)
  try:
    ncry = int(folder.split("cry")[1])
  except IndexError:
    continue
  c = ROOT.TChain("tree")
  c.Add(f"{folder}/*.root")
  h = ROOT.TH1F(f"h_{ncry}", f"charge_cry{ncry}", 100, 5, 105)
  cnv = ROOT.TCanvas()
  c.Draw(f"(charge[0][{ncry*2}]+charge[0][{ncry*2+1}])/2>>h_{ncry}")
  print(h.Integral(), h.GetMean())
  f = ROOT.TF1("func", "gaus(0)+gaus(3)", 10, 65);
  f.SetParameters(500, 25, 10, 50, 50, 7);
  h.Fit(f, "R")
  h.SetTitle(f"Cry: {ncry} - Mean Charge: {f.GetParameter(1)} +/- {f.GetParError(1)} pC")
  cnv.SaveAs(f"../plots/cnv_{ncry}.root")
  cnv.SaveAs(f"../plots/cnv_{ncry}.pdf")
