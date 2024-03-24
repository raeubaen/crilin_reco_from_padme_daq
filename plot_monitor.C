#include <TStyle.h>
#include <TFile.h>
#include <TCanvas.h>
#include <TTree.h>
#include <TROOT.h>
// do not try to understand - just trust me or if you want check it
int x(int cry) {return 2 - (cry/2)/3;}
int y(int cry) {return (cry/2)%3;}

void plot_monitor(TString filebig, TString filesmall){

  gROOT->LoadMacro("/home/mu2e/rootlogon.C");
  TFile *f[2];
  f[0] = new TFile(filesmall);
  f[1] = new TFile(filebig);
  TTree *intree[2];
  intree[0] = (TTree*)f[0]->Get("NTU");
  intree[1] = (TTree*)f[1]->Get("NTU");

  auto *c = new TCanvas("c", "Crilin H2 August 2023 - crystal charge online monitor - cyan=allrecofragments", 1700, 900);
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
    if (j==1) p->SetFillColor(kCyan);
    for(int i=0; i<9; i++){
      int _x = x(i*2);
      int _y = y(i*2);
      p->cd((3*_x+_y + 1));
      cout << i << endl;
      intree[j]->Draw(Form("(QCh[0][%i]+QCh[0][%i])/2>>h_%i(200, 0, 1000)", i*2, i*2+1, 9*j+i),Form("QCh[0][%i]>5 && QCh[0][%i]>5",i*2, i*2+1));
      cout << "finito" << endl;
    }
  }
  c->SaveAs("onlinemonitorbtf_last_summary.root");
  c->RaiseWindow();
}
