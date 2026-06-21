cd ${WORKING_DIR}
echo "Inside: ${WORKING_DIR}"

timeout ${SINGLE_FRAGMENT_PROCESS_TIMEOUT_SECONDS}s ./process_single_fragment.sh "$@" 2>&1 | tee ${LOGS_DIR}/log_run${1}_fragment${2}_typeis${3}.log
