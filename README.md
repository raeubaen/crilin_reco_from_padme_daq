analastfile.sh daqlogger.sh sono file per la cartella del DAQ

Overview of the code:
  - **reco.py & reco_functions.py**\
    python script for the reconstruction, where all the useful variables for DQM plots are saved in a tree + plotting (...)

  - **plot_functions_....py**\
    python script for plotting, very general with one single function for the different plots

  - **plot_list.csv**\
    csv file with the list of the plots and the settings for each one

To launch:
   python3 onlinemonitor_nogpu.py <nrun> <conf>  (conf w/o extension or path)
   Optional arguments --> restart from fragment or change the sleep time between reconstructions steps
   

```
#example dev check
python3 reco_dev.py -ro /tmp/out.root -i ../../crilinDAQ/unpacked_files/run_0000218_20260328_113632/unpacked_run_0000218_20260328_113632_001.root -po /var/www/html/online_monitor/runs/$run_name/current_fragment/ -dj /home/crilin/crilinRECO/default_crilin_reco_from_padme_daq/confs/tb_btf_slayer_2026_dev.json
merge dev files in production ones only when OK
(this REALLY should be done with dedicated branches in same git repo, but in different folders...)
```
