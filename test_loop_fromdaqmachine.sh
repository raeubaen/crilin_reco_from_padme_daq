mkdir ${DAQ_MACHINE_UNPACKED_FOLDER}/run_0000342_20260618_151946

for i in $(seq 0 100); do
  echo "writing $i"
  touch ${DAQ_MACHINE_UNPACKED_FOLDER}/run_0000342_20260618_151946/run_0000342_20260618_151946_lvl1_00_$(printf "%03d" $i).root
  sleep 14;
done
