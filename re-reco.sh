RUN=$1
MODE=$2

if [ "$USE_CUDA" = "1" ]; then
    echo "Using CUDA"
    N_PARALLEL=1
else
    echo "Using CPU"
    N_PARALLEL=6

fi

echo "parallel processes: $N_PARALLEL"

export RECO_FOLDER_ORIGINAL="${RECO_FOLDER}"

echo Run: $RUN

LOGS_FOLDER="${RECO_UNPACKED_OUTDIR}/re-reco/re-reco-logs/"

DONE_FILE="/tmp/done_files.txt"

mkdir -p $LOGS_FOLDER

echo "LOGS in " ${LOGS_FOLDER}

echo > $DONE_FILE

fragment_list="$(ls -1 "$UNPACKED_FOLDER/run_$RUN/unpacked_${RUN}"*.root | awk -F "_" '{print $NF}' | awk -F "."  '{print $1}')"

export RECO_FOLDER="${RE_RECO_FOLDER}"

for fragment_str in ${fragment_list}; do

    # Convert fragment number safely (leading zeros → decimal)
    fragment=$fragment_str

    echo ${RE_RECO_FOLDER}/run_$RUN/${RUN}_${fragment}_reco.root >> $DONE_FILE

    echo "Processing fragment $fragment"

    mkdir -p $LOGS_FOLDER/log_${RUN}

    cd $WORKING_DIR

    # Launch background job for this actual fragment
    echo "./process_single_fragment.sh $RUN $fragment $MODE noplots >  $LOGS_FOLDER/log_${RUN}/log_${RUN}_${fragment}.log 2>&1 &"

    bash -c "./process_single_fragment.sh $RUN $fragment $MODE noplots >  $LOGS_FOLDER/log_${RUN}/log_${RUN}_${fragment}.log 2>&1 &"

    sleep 1
    while true; do
        running=$(ps aux | grep "python3 -m ferrari_core.reco" | grep -v grep | wc -l)
        if (( running < 1 )); then
            break
        fi
        sleep 1
    done

done

echo list of files re-recoed in $DONE_FILE

export RECO_FOLDER="${RECO_FOLDER_ORIGINAL}"
