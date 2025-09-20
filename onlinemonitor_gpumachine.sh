#!/bin/bash

#folder=$(ls -1 local/rawdata | sort -V | tail -n 1)

#lastfile=$(ls -1 local/rawdata/$folder | sort -V | tail -n 2 | head -n 1)

#xrdcp "root://eospublic.cern.ch//eos/experiment/muoncollider/data/crilin/h2-2025/last_file.txt" /tmp/last_file.txt

orig=$(pwd)

while true; do

	if [ ! -e /tmp/current_file.txt ]; then
	    cp -n /tmp/last_file.txt /tmp/current_file.txt;
	elif ! cmp -s /tmp/last_file.txt /tmp/current_file.txt; then
	    cp -n /tmp/last_file.txt /tmp/current_file.txt;
	else
	    continue
        fi

        echo reco starting

	filename=$(cat /tmp/last_file.txt | awk '{print $1}')
	conf=$(cat /tmp/last_file.txt | awk '{print $2}')

	run_name=$(echo $filename | awk -F '_' '{print $(NF-3)}')
	n_fragment=$(echo $filename | awk -F '/' '{print $NF}' | awk -F '_' '{print $NF}' | awk -F '.' '{print $1}')

	echo "--------------- runname,fragment: $run_name, $n_fragment"

	unpacked_xrd="root://eospublic.cern.ch/$filename"
	reco_xrd="root://eospublic.cern.ch//eos/experiment/muoncollider/data/crilin/h2-2025/gpu_reco_files/reco_${run_name}_${n_fragment}.root"

	mkdir -p /root/reco_files/${run_name}

	#source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc11-opt/setup.sh

	mkdir -p /root/plot_files/$run_name/current_fragment/

	python3 reco_gpu.py -ro /root/reco_files/$run_name/reco_$n_fragment.root -i $filename -po /root/plot_files/$run_name/current_fragment/ -dj /root/crilin_reco_from_padme_daq/confs/$conf.json -hd "source /root/crilin_reco_from_padme_daq/hadd_gpu.sh $run_name $conf $n_fragment &"

	xrdcp /root/reco_files/$run_name/reco_$n_fragment.root $reco_xrd &

        break
done

cd $orig
