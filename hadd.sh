run_name=$1
conf=$2
n_fragment=$3

echo "conf: $conf"

mkdir -p /var/www/html/online_monitor/runs/$run_name/all_fragments/

plotlist="/home/crilin/crilinRECO/default_crilin_reco_from_padme_daq/$(cat /home/crilin/crilinRECO/default_crilin_reco_from_padme_daq/confs/$conf.json | grep plotlist | awk -F '"' '{print $4}')"

echo "hadding (output in /dev/null - to debug open the code...)"
for folder in $(ls -1d /var/www/html/online_monitor/runs/$run_name/current_fragment/*/); do
  for file in $(ls -1 $folder/*.root); do
    source="/var/www/html/online_monitor/runs/$run_name/current_fragment/$(basename $folder)/$(basename $file)"
    dest="/var/www/html/online_monitor/runs/$run_name/all_fragments/$(basename $folder)/$(basename $file)"
    mkdir -p /var/www/html/online_monitor/runs/$run_name/all_fragments/$(basename $folder)
    filename=$(basename $file)
    plot="${filename::-5}"
    echo $plot
    if [[ -n $(cat $plotlist | grep -v '#' | grep $plot) ]]; then
      if [[ $n_fragment == "000" ]]; then
        cp $source $dest;
      else
	hadd -a $dest $source > /dev/null 2>&1;
      fi
    fi
  done
done

echo "python re-plot hadded"
python3 plot_hadded.py -po /var/www/html/online_monitor/runs/$run_name/all_fragments/ -dj /home/crilin/crilinRECO/default_crilin_reco_from_padme_daq/confs/$conf.json

echo "-------------------- hadd and plot hadded done -----------------"
