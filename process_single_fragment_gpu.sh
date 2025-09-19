#!/bin/bash

#folder=$(ls -1 local/rawdata | sort -V | tail -n 1)

#lastfile=$(ls -1 local/rawdata/$folder | sort -V | tail -n 2 | head -n 1)

echo "conf: $2"

orig=$(pwd)

echo 'Usage: raw_filename (including path, absolute or from /home/crilin/crilinDAQ/) as \$1, name of config as \$2 (/home/crilin/crilinRECO/default_crilin_reco_from_padme_daq/confs/$2.json)'

cd /home/crilin/crilinDAQ

filename=$1

run_name=$(echo $filename | awk -F '/' '{print $(NF-1)}')
n_fragment=$(echo $filename | awk -F '/' '{print $NF}' | awk -F '_' '{print $7}' | awk -F '.' '{print $1}')

source /home/crilin/crilinRECO/default_crilin_reco_from_padme_daq/raw2root_reco_gpu.sh $run_name $2 $n_fragment &

cd $orig
