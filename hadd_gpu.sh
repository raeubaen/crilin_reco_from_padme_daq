run_name=$1
conf=$2
n_fragment=$3

echo "conf: $conf"

mkdir -p /root/plot_files/$run_name/all_fragments/

plotlist="/root/crilin_reco_from_padme_daq/$(cat /root/crilin_reco_from_padme_daq/confs/$conf.json | grep plotlist | awk -F '"' '{print $4}')"

echo "hadding (output in /dev/null - to debug open the code...)"
for folder in $(ls -1d /root/plot_files/$run_name/current_fragment/*/); do
  for file in $(ls -1 $folder/*.root); do
    source="/root/plot_files/$run_name/current_fragment/$(basename $folder)/$(basename $file)"
    dest="/root/plot_files/$run_name/all_fragments/$(basename $folder)/$(basename $file)"
    mkdir -p /root/plot_files/$run_name/all_fragments/$(basename $folder)
    filename=$(basename $file)
    plot="${filename::-5}"
    echo $plot
    if [[ -n $(cat $plotlist | grep -v '#' | grep $plot) ]]; then
      if [ ! -f $dest ]; then
        cp $source $dest;
      else
        hadd -a $dest $source > /dev/null 2>&1;
      fi
    fi
  done
done

/bin/cp /root/plot_files/*.php /root/plot_files/$run_name/all_fragments/

echo "python re-plot hadded"
python3 plot_hadded.py -po /root/plot_files/$run_name/all_fragments/ -dj /root/crilin_reco_from_padme_daq/confs/$conf.json

echo "rm -rf /root/plot_files/$run_name crilin@pcrwellgif:/var/www/html/online_monitor/runs/gpu_$run_name"

sshpass -p crilin ssh crilin@pcrwellgif "rm -rf /var/www/html/online_monitor/runs/gpu_$run_name"
sshpass -p crilin scp -r /root/plot_files/$run_name crilin@pcrwellgif:/var/www/html/online_monitor/runs/gpu_$run_name

echo "-------------------- hadd and plot hadded done -----------------"
