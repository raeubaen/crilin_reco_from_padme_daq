export USE_CUDA=1

export TOTAL_FRAGMENTS_IN_PERIOD=1
export PROCESS_FRAGMENTS_IN_PERIOD=1

export DAQ_MACHINE_DAQ_FOLDER="/home/crilin/crilinDAQ"
export DAQ_MACHINE_ONLINE_FOLDER="/home/crilin/crilinRECO/default_crilin_reco_from_padme_daq"
export DAQ_MACHINE_UNPACKED_FOLDER="${DAQ_MACHINE_DAQ_FOLDER}/local/rawdata/"

export SINGLE_FRAGMENT_PROCESS_TIMEOUT_SECONDS=25
export HOME_DIR="/root/"

export PLOT_MAIN_FOLDER="/eos/user/r/rgargiul/www/h2dqm/CRILIN_TB_2026-dev/"
export RECO_UNPACKED_OUTDIR="/eos/experiment/muoncollider/data/crilin/h2-2026/"
export UNPACKED_FOLDER="${RECO_UNPACKED_OUTDIR}/DataTree_dqm"
export REMOTE_UNPACKED_FILENAME_FMT="${RECO_UNPACKED_OUTDIR}/run_{%s}/unpacked_{%s}_{%s}.root"

export RECO_FOLDER="${RECO_UNPACKED_OUTDIR}/reco_dqm"
export RE_RECO_FOLDER="${RECO_UNPACKED_OUTDIR}/re-reco_dqm"

export LOGS_DIR="eos/user/r/rgargiul/www/h2dqm/CRILIN_TB_2026-dev/logs/"

export WORKING_DIR="${HOME_DIR}/crilin_reco_from_padme_daq"
export JSON_CONF="${HOME_DIR}/crilin_reco_from_padme_daq/confs/tb_2026.json"
export PHP_FILES_DIR="${HOME_DIR}/crilin_reco_from_padme_daq/ferrari_core/php/"
export PLOTS_PLUGINS_FOLDER="${HOME_DIR}/crilin_reco_from_padme_daq/custom_plot_functions/"

export HADD_NOW_DIRS="${PLOT_MAIN_FOLDER}/to_hadd_now.txt"
export HADD_GLOB_BUFFER="${PLOT_MAIN_FOLDER}/to_hadd_buffer.txt"

export REMOTE_LOCK_FILE="${RECO_UNPACKED_OUTDIR}/lock_file.txt"

export XROOTD_SERVER="root://eospublic.cern.ch/"

