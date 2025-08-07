int x(int ch) {return 2 - (ch/2)/3;}
int y(int ch) {return (ch/2)%3;}

void plot_client_btf(){

  TFile *f = new TFile("/home/crilin/Documents/OnlineMonitor/onlinemonitorbtf_last_summary.root");
  TCanvas *c = (TCanvas*)f->Get("c");
  c->Draw();
  c->RaiseWindow();
}
