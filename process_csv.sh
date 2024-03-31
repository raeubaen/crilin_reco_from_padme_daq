#removes 5th run (175) - very poor agreement - suspect mislabelling of true position

cat ../plots_trk/reco_trk_values.csv | grep x > ../plots_trk/x_reco_trk_values.csv
cat ../plots_trk/reco_trk_values.csv | grep y > ../plots_trk/y_reco_trk_values.csv

sed -i -e 's/x //g' ../plots_trk/x_reco_trk_values.csv
sed -i -e 's/y //g' ../plots_trk/y_reco_trk_values.csv

sed -i -e 's/ /,/g' ../plots_trk/x_reco_trk_values.csv
sed -i -e 's/ /./g' ../plots_trk/y_reco_trk_values.csv

echo "true,reco,errreco,sigma,errsigma" > header

cat header ../plots_trk/x_reco_trk_values.csv | head -n 5 > ../plots_trk/x_reco_trk_values.csv_temp
cat header ../plots_trk/y_reco_trk_values.csv | head -n 5 > ../plots_trk/y_reco_trk_values.csv_temp

mv ../plots_trk/x_reco_trk_values.csv_temp ../plots_trk/x_reco_trk_values.csv
mv ../plots_trk/y_reco_trk_values.csv_temp ../plots_trk/y_reco_trk_values.csv

rm header

