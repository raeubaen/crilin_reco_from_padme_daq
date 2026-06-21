#!/bin/bash

echo "init"

pkill -f "wrapper_with_timeout_for_process_single_fragment.sh" 2>/dev/null || true

echo "killed old workers  (if any)"

rm -f ${REMOTE_LOCK_FILE}
echo > ${REMOTE_LOCK_FILE}

rm -f /tmp/last_file.txt
rm -f "$LAST_LAUNCH_FILE"
rm -f /tmp/current_file.txt

orig=$(pwd)

declare -a PIDS=()

while true; do

  #echo "new iteration"
  sleep 0.5

  /bin/cp ${REMOTE_LOCK_FILE} /tmp/remote_lock.txt

  if [ ! -f /tmp/current_lock.txt ]; then
      /bin/cp /tmp/remote_lock.txt /tmp/current_lock.txt
      # trigger
  elif ! cmp -s /tmp/remote_lock.txt /tmp/current_lock.txt; then
      /bin/cp /tmp/remote_lock.txt /tmp/current_lock.txt
      # trigger
  else
      #echo "lock file unchanged"
      continue
  fi


  /bin/cp "${REMOTE_LAST_FILE}" /tmp/last_file.txt

  echo "last: $(cat /tmp/last_file.txt), current: $(cat /tmp/current_file.txt 2>/dev/null)"

  if [ ! -e /tmp/current_file.txt ]; then
    /bin/cp /tmp/last_file.txt /tmp/current_file.txt
  elif ! cmp -s /tmp/last_file.txt /tmp/current_file.txt; then
    echo ""
    echo ""
    echo "Last file changed, starting processing"
    /bin/cp /tmp/last_file.txt /tmp/current_file.txt
  else
    echo "Last file UNCHANGED! continuing"
    continue
  fi

  echo reco starting

  run=$(awk '{print $1}' /tmp/current_file.txt)
  fragment=$(awk '{print $2}' /tmp/current_file.txt)
  filename=$(awk '{print $3}' /tmp/current_file.txt)
  mode=$(awk '{print $4}' /tmp/current_file.txt)

  echo "run: $run"
  echo "fragment: $fragment"
  echo "setup: $mode"
  echo "about to run: ./wrapper_with_timeout_for_process_single_fragment.sh ${run} ${fragment} ${mode}"
  echo "unpacked file in: $filename"

  #
  # Cleanup dead workers
  #
  alive_pids=()
  for pid in "${PIDS[@]}"; do
      if kill -0 "$pid" 2>/dev/null; then
          alive_pids+=("$pid")
      fi
  done
  PIDS=("${alive_pids[@]}")


  while [ "${#PIDS[@]}" -ge 2 ]; do
      echo "Maximum workers reached (${#PIDS[@]}/2), waiting..."

      sleep 1

      alive_pids=()
      for pid in "${PIDS[@]}"; do
          if kill -0 "$pid" 2>/dev/null; then
              alive_pids+=("$pid")
          fi
      done
      PIDS=("${alive_pids[@]}")
  done

  while true; do
      now=$(date +%s)

      if [ -f "$LAST_LAUNCH_FILE" ]; then
          last=$(cat "$LAST_LAUNCH_FILE")
      else
          last=0
      fi

      delta=$((now - last))

      if [ "$delta" -ge "$PARALLEL_GAP" ]; then
          break
      fi

      wait_time=$((PARALLEL_GAP - delta))
      echo "Waiting ${wait_time}s before launching next worker..."
      sleep 1
  done


  echo "$now" > "$LAST_LAUNCH_FILE"

  echo "doing: ./wrapper_with_timeout_for_process_single_fragment.sh $run $fragment $mode > $LOGS_DIR/${fragment}.log 2>&1 &"

  ./wrapper_with_timeout_for_process_single_fragment.sh \
      "$run" "$fragment" "$mode" > $LOGS_DIR/${fragment}.log 2>&1 &


  worker_pid=$!
  PIDS+=("$worker_pid")


  echo "Started worker PID=$worker_pid"

done

cd "$orig"
