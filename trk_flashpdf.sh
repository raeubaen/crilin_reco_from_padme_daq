nrun=$1
root ../plot_trk/${nrun}_vmax_leadglass.root << EOF
  new TCanvas("c");
  v_${nrun}->Draw();
  c->SetLogy();
  c->SaveAs("../plot_trk/${nrun}_vmax_leadglass.pdf");
EOF

root ../plot_trk/${nrun}_waves_leadglass.root << EOF
  new TCanvas("c");
  h_${nrun}->Draw("zcol");
  h_${nrun}->GetYaxis()->SetRangeUser(-600, 50);
  h_${nrun}->GetXaxis()->SetRangeUser(500, 750);
  c->SetLogz();
  c->SaveAs("../plot_trk/${nrun}_waves_leadglass.pdf");
EOF

