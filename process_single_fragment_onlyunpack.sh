#!/bin/bash

#folder=$(ls -1 local/rawdata | sort -V | tail -n 1)

#lastfile=$(ls -1 local/rawdata/$folder | sort -V | tail -n 2 | head -n 1)

orig=$(pwd)

echo 'Usage: raw_filename (including path, absolute or from /home/crilin/crilinDAQ/) as \$1'

cd /home/crilin/crilinDAQ

filename=$1

run_name=$(echo $filename | awk -F '/' '{print $(NF-1)}')
n_fragment=$(echo $filename | awk -F '/' '{print $NF}' | awk -F '_' '{print $7}' | awk -F '.' '{print $1}')

cd /home/crilin/crilinDAQ

echo "$run_name, $n_fragment"

unpacked_xrd="root://eospublic.cern.ch//eos/experiment/muoncollider/data/crilin/h2-2025/unpacked_files/unpacked_${run_name}_${n_fragment}.root"
unpacked="/home/crilin/crilinDAQ/unpacked_files/${run_name}/unpacked_${run_name}_${n_fragment}.root"

mkdir -p /home/crilin/crilinDAQ/unpacked_files/${run_name}/

echo "sourcing padme (prova version)"
source padme-fw/Configure/padme_init_cvmfs_alma9_prova.sh

echo "raw2root"
./Raw2Root -i $filename -o $unpacked
xrdcp $unpacked $unpacked_xrd &


cd $orig
