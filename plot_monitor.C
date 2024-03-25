#include <TStyle.h>
#include <TFile.h>
#include <TCanvas.h>
#include <TTree.h>
#include <TROOT.h>
// do not try to understand - just trust me or if you want check it
int x(int cry) {return 2 - (cry/2)/3;}
int y(int cry) {return (cry/2)%3;}

void plot_monitor(TString all_files, TString lastfile){

  gROOT->LoadMacro("/home/mu2e/rootlogon.C");
  TChain *intree[2];
  for (int i=0; i<2; i++) intree[i] = new TChain("NTU");

  intree[0]->Add(all_files);
  intree[1]->Add(lastfile);

  auto *c = new TCanvas("c", "Crilin BTF Spring 2024 - crystal charge online monitor - cyan=allrecofragments", 1700, 900);
  c->Divide(2);

  gStyle->SetLabelSize(0.05, "X");
  gStyle->SetLabelSize(0.05, "Y");
  gStyle->SetTitleFontSize(0.06);
  gStyle->SetTitleY(1.1);
  gStyle->SetStatX(0.6);
  gStyle->SetStatY(0.6);

  for(int j=0; j<2; j++){
    auto *p = c->cd(j+1);
    p->Divide(3, 3);
    if (j==0) p->SetFillColor(kCyan);
    for(int i=0; i<9; i++){
      int _x = x(i*2);
      int _y = y(i*2);
      p->cd((3*_x+_y + 1));
      intree[j]->Draw(Form("(QCh[0][%i]+QCh[0][%i])/2>>h_%i(50, 5, 105)", i*2, i*2+1, 9*j+i),Form("QCh[0][%i]>5 && QCh[0][%i]>5",i*2, i*2+1));
    }
  }
  c->SaveAs("../outonline/onlinemonitorbtf_last_summary.root");
  c->RaiseWindow();
}
