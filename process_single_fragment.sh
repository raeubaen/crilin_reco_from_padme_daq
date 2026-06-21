#!/bin/bash

# --- launch settings with beam|laser as input parameter ---
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <run_number> <fragment_number> <setup> [noplots]"
    return
fi


RUN=$1
FRAGMENT=$2
setup=$3

if [ "$4" == "noplots" ]; then
  doplots="0"
else
  doplots="1"
fi

UNPACKED_FILE=$(printf "$REMOTE_UNPACKED_FILENAME_FMT" "$run_name" "$run_name" "$n_fragment")

echo "plot? yes=1, no=0: " $doplots

echo "fragment type is: " $setup

FRAGMENT_STR="${FRAGMENT}_${setup}"

# --- Start global timer ---
start_time=$(date +%s)


if [ "$dounpack" -ne 0 ]; then

cd ${WORKING_DIR}

mkdir -p ${RECO_FOLDER}/run_$RUN/

PLOT_CURRENT_FOLDER=$PLOT_MAIN_FOLDER/run_$RUN/fragment_$FRAGMENT_STR/

if [ "$doplots" == "1" ]; then

  echo ${PLOT_MAIN_FOLDER}
  mkdir ${PLOT_MAIN_FOLDER}/run_${RUN}/
  mkdir ${PLOT_CURRENT_FOLDER}

  /bin/cp ${PHP_FILES_DIR}/*.php $PLOT_MAIN_FOLDER
  /bin/cp ${PHP_FILES_DIR}/*.php $PLOT_MAIN_FOLDER/run_$RUN/
  /bin/cp ${PHP_FILES_DIR}/*.php $PLOT_CURRENT_FOLDER
  echo "plotting in: $PLOT_CURRENT_FOLDER"

  plots_options="-po $PLOT_CURRENT_FOLDER"
else
  plots_options=""
fi

echo "Starting reconstruction..."

echo "doplots: " $doplots

cd ${WORKING_DIR}

cmd="python3 -m ferrari_core.reco -i ${UNPACKED_FILE} \
    -r "$RUN" \
    -s "$FRAGMENT" \
    -ro ${RECO_FOLDER}/run_$RUN/ \
    -j ${JSON_CONF} \
    -opt $setup \
    --do-plots $doplots $plots_options"

echo $cmd

eval $cmd

end_time=$(date +%s)
total_time=$((end_time - start_time))
echo "Total elapsed time: $total_time seconds."

if [ "$doplots" == "1" ]; then
  cp -rT "$PLOT_MAIN_FOLDER/run_$RUN/fragment_$FRAGMENT_STR" "$PLOT_MAIN_FOLDER/run_$RUN/${setup}_current_fragment"

  if [ "$setup" != "laser" ]; then
    echo "writing folder path to hadd buffer: $PLOT_MAIN_FOLDER/to_hadd_buffer.txt"
    echo $PLOT_CURRENT_FOLDER >> ${HADD_GLOB_BUFFER}
  fi

  if [ $((FRAGMENT_NO % FRAGMENT_HADD_INTERVAL)) -eq $((FRAGMENT_HADD_INTERVAL - 1)) ]; then
    cp ${HADD_GLOB_BUFFER} ${HADD_NOW_DIRS}
     echo "copying to hadd-now buffer"
  fi
fi
