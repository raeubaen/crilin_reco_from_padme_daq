#!/bin/bash

nrun=$1
x=$2
y=$3
folder=$4

root -l << EOF
  gROOT->LoadMacro("root_logon.C");
  gStyle->SetOptStat(0100);
  gStyle->SetOptFit(1111);
  gStyle->SetStatX(0.75);
  gStyle->SetStatY(0.77);
  gStyle->SetStatH(.1);
  gStyle->SetStatW(.15);
  gStyle->SetStatFontSize(0.02);

  new TChain("tree");
  tree->Add("../output/$4/out*.root");

  new TCanvas("yreco_${nrun}");
  tree->Draw("(1.15*charge[0][13]+0.85*charge[0][12]+1.15*charge[0][15]+0.85*charge[0][14]+1.15*charge[0][17]+0.85*charge[0][16]+0.15*charge[0][7]-0.15*charge[0][6]+0.15*charge[0][9]-0.15*charge[0][8]+0.15*charge[0][11]-0.15*charge[0][10]-1.15*charge[0][0]-0.85*charge[0][1]-1.15*charge[0][2]-0.85*charge[0][3]-1.15*charge[0][4]-0.85*charge[0][5])/(charge[0][13]+charge[0][12]+charge[0][15]+charge[0][14]+charge[0][17]+charge[0][16]+charge[0][7]+charge[0][6]+charge[0][9]+charge[0][8]+charge[0][11]+charge[0][10]+charge[0][0]+charge[0][1]+charge[0][2]+charge[0][3]+charge[0][4]+charge[0][5])>>yhist_${nrun}(300, -1.5, 1.5)", "charge[0][22] > 30 && charge[0][22] < 70 && Min\$(charge[0]) > 0");
  yhist_${nrun}->Fit("gaus", "Q", "", -0.5, 0.5);
  TF1 *f = yhist_${nrun}->GetFunction("gaus");
  auto mean_temp = f->GetParameter(1);
  auto sigma_temp = f->GetParameter(2);
  yhist_${nrun}->Fit("gaus", "Q", "", mean_temp-2*sigma_temp, mean_temp+2*sigma_temp);
  TF1 *f = yhist_${nrun}->GetFunction("gaus");
  auto mean_temp = f->GetParameter(1);
  auto sigma_temp = f->GetParameter(2);
  yhist_${nrun}->Fit("gaus", "Q", "", mean_temp-2*sigma_temp, mean_temp+2*sigma_temp);
  TF1 *f = yhist_${nrun}->GetFunction("gaus");
  cout << "y" << " " << $y << " " << f->GetParameter(1) << " " << f->GetParError(1) << " " << f->GetParameter(2) << " " << f->GetParError(2) << endl;
  yreco_${nrun}->SaveAs("../plots_trk/yreco_${nrun}_x${x}_y${y}.root");
  yreco_${nrun}->SaveAs("../plots_trk/yreco_${nrun}_x${x}_y${y}.pdf");

  new TCanvas("xreco_${nrun}");
  tree->Draw("(-1*charge[0][13]-1*charge[0][12]+1*charge[0][17]+1*charge[0][16]-1*charge[0][7]-1*charge[0][6]+1*charge[0][11]+1*charge[0][10]-1*charge[0][0]-1*charge[0][1]+1*charge[0][4]+1*charge[0][5])/(charge[0][13]+charge[0][12]+charge[0][15]+charge[0][14]+charge[0][17]+charge[0][16]+charge[0][7]+charge[0][6]+charge[0][9]+charge[0][8]+charge[0][11]+charge[0][10]+charge[0][0]+charge[0][1]+charge[0][2]+charge[0][3]+charge[0][4]+charge[0][5])>>xhist_${nrun}(300, -1.5, 1.5)", "charge[0][22] > 30 && charge[0][22] < 70 && Min\$(charge[0]) > 0");
  xhist_${nrun}->Fit("gaus", "Q", "", -0.5, 0.5);
  TF1 *f = xhist_${nrun}->GetFunction("gaus");
  auto mean_temp = f->GetParameter(1);
  auto sigma_temp = f->GetParameter(2);
  xhist_${nrun}->Fit("gaus", "Q", "", mean_temp-2*sigma_temp, mean_temp+2*sigma_temp);
  TF1 *f = xhist_${nrun}->GetFunction("gaus");
  auto mean_temp = f->GetParameter(1);
  auto sigma_temp = f->GetParameter(2);
  xhist_${nrun}->Fit("gaus", "Q", "", mean_temp-2*sigma_temp, mean_temp+2*sigma_temp);
  TF1 *f = xhist_${nrun}->GetFunction("gaus");
  cout << "x" << " " << $x << " " << f->GetParameter(1) << " " << f->GetParError(1) << " " << f->GetParameter(2) << " " << f->GetParError(2) << endl;
  xreco_${nrun}->SaveAs("../plots_trk/xreco_${nrun}_x${x}_y${y}.root");
  xreco_${nrun}->SaveAs("../plots_trk/xreco_${nrun}_x${x}_y${y}.pdf");

EOF
