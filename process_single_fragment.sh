#!/bin/bash

#folder=$(ls -1 local/rawdata | sort -V | tail -n 1)

#lastfile=$(ls -1 local/rawdata/$folder | sort -V | tail -n 2 | head -n 1)

orig=$(pwd)

echo 'Usage: raw_filename (including path, absolute or from /home/crilin/crilinDAQ/) as \$1, name of config as \$2 (/home/crilin/crilinRECO/default_crilin_reco_from_padme_daq/confs/$2.json)'

cd /home/crilin/crilinDAQ

filename=$1

run_name=$(echo $filename | awk -F '/' '{print $(NF-1)}')
n_fragment=$(echo $filename | awk -F '/' '{print $NF}' | awk -F '_' '{print $7}' | awk -F '.' '{print $1}')

echo "$run_name, $n_fragment"

unpacked_xrd="root://eospublic.cern.ch//eos/experiment/muoncollider/data/crilin/h2-2025/unpacked_files/unpacked_${run_name}_${n_fragment}.root"
unpacked="/home/crilin/crilinDAQ/unpacked_files/${run_name}/unpacked_${run_name}_${n_fragment}.root"

mkdir -p /home/crilin/crilinDAQ/unpacked_files/${run_name}/

echo "sourcing padme (prova version)"
source padme-fw/Configure/padme_init_cvmfs_alma9_prova.sh

echo "raw2root"
./Raw2Root -i $filename -o $unpacked
xrdcp $unpacked $unpacked_xrd &

cd /home/crilin/crilinRECO/default_crilin_reco_from_padme_daq

reco_xrd="root://eospublic.cern.ch//eos/experiment/muoncollider/data/crilin/h2-2025/reco_files/reco_${run_name}_${n_fragment}.root"
reco="/home/crilin/crilinRECO/reco_files/${run_name}/reco_${run_name}_${n_fragment}.root"

mkdir -p /home/crilin/crilinRECO/reco_files/${run_name}

echo "raw2root fatto - prima del source"

#echo "sourcing lcg107"
#source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc11-opt/setup.sh

echo "dopo il source, sta per iniziare reco"

mkdir -p /var/www/html/online_monitor/runs/$run_name/current_fragment/

python3 reco.py -ro $reco -i $unpacked -po /var/www/html/online_monitor/runs/$run_name/current_fragment/ -dj /home/crilin/crilinRECO/default_crilin_reco_from_padme_daq/confs/$2.json

xrdcp $reco $reco_xrd &

mkdir -p /var/www/html/online_monitor/runs/$run_name/all_fragments/


echo "hadding (output in /dev/null - to debug open the code...)"
for folder in $(ls -1d /var/www/html/online_monitor/runs/$run_name/current_fragment/*); do
  for file in $(ls -1 $folder/*.root); do
    source="/var/www/html/online_monitor/runs/$run_name/current_fragment/$(basename $folder)/$(basename $file)"
    dest="/var/www/html/online_monitor/runs/$run_name/all_fragments/$(basename $folder)/$(basename $file)"
    mkdir -p /var/www/html/online_monitor/runs/$run_name/all_fragments/$(basename $folder)
    if (( $((n_fragment)) == 0 )); then
      cp $source $dest;
    else
      hadd -a $dest $source > /dev/null 2>&1;
    fi
  done
done

python3 plot_hadded.py -po /var/www/html/online_monitor/runs/$run_name/all_fragments/ -dj /home/crilin/crilinRECO/default_crilin_reco_from_padme_daq/confs/$2.json

cd $orig
