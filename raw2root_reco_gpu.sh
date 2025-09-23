run_name=$1
conf=$2
n_fragment=$3

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

echo $unpacked_xrd $conf > /tmp/last_file.txt

xrdcp -f /tmp/last_file.txt "root://eospublic.cern.ch//eos/experiment/muoncollider/data/crilin/h2-2025/last_file.txt"



cd /home/crilin/crilinRECO/default_crilin_reco_from_padme_daq

reco_xrd="root://eospublic.cern.ch//eos/experiment/muoncollider/data/crilin/h2-2025/reco_files/reco_${run_name}_${n_fragment}.root"
reco="/home/crilin/crilinRECO/reco_files/${run_name}/reco_${run_name}_${n_fragment}.root"

mkdir -p /home/crilin/crilinRECO/reco_files/${run_name}

echo "raw2root fatto - prima del source"

#echo "sourcing lcg107"
#source /cvmfs/sft.cern.ch/lcg/views/LCG_107/x86_64-el9-gcc11-opt/setup.sh

echo "dopo il source, sta per iniziare reco"

mkdir -p /var/www/html/online_monitor/runs/$run_name/current_fragment/

python3 reco.py -ro $reco -i $unpacked -po /var/www/html/online_monitor/runs/$run_name/current_fragment/ -dj /home/crilin/crilinRECO/default_crilin_reco_from_padme_daq/confs/$conf.json -hd "source /home/crilin/crilinRECO/default_crilin_reco_from_padme_daq/hadd.sh $run_name $conf $n_fragment &"

xrdcp $reco $reco_xrd &
