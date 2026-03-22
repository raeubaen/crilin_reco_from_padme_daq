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
   