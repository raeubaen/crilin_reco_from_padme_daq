#!/bin/bash

echo 'Usage: raw_filename (absolute) as \$1, setup (example: electrons) as \$2'

filename=$1
setup=$2

run_name=$(echo $filename | awk -F '/' '{print $(NF-1)}')
n_fragment=$(echo $filename | awk -F '/' '{print $NF}' | awk -F '_' '{print $7}' | awk -F '.' '{print $1}')

echo "$run_name, $n_fragment"

xrdfs ${XROOTD_SERVER} mkdir -p ${RECO_UNPACKED_OUTDIR}/run_${run_name}

unpacked_path=$(printf "$REMOTE_UNPACKED_FILENAME_FMT" "$run_name" "$run_name" "$n_fragment")

unpacked_xrd="${XROOTD_SERVER}/${unpacked_path}"

xrdcp $filename $unpacked_xrd &

echo $run_name $n_fragment $unpacked_xrd $setup > /tmp/last_file.txt

xrdcp -f /tmp/last_file.txt "${XROOTD_SERVER}/${REMOTE_LOCK_FILE}/last_file.txt"

