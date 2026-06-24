mkdir ${DAQ_MACHINE_UNPACKED_FOLDER}/run_${TEST_RUN}

for i in $(seq 1 100); do
  echo "writing $i"
  touch ${DAQ_MACHINE_UNPACKED_FOLDER}/run_${TEST_RUN}/run_${TEST_RUN}_lvl1_00_$(printf "%03d" $i).root
  sleep 14;
done
