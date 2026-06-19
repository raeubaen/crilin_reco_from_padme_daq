filename=$1

python3 -m ferrari_core.reco -ro ${RECO_FOLDER}/crilin_prova_reco.root -i $filename \
  -po ${PLOT_MAIN_FOLDER}/prova/ -j ${JSON_CONF} \
  -opt electrons -r 0 -s 0
