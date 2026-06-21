#!/bin/bash

rm -f /tmp/current_file.txt

orig=$(pwd)

while true; do

  sleep 0.1
  xrdcp -f "${REMOTE_LOCK_FILE}" /tmp/last_file.txt

  echo "last: $(cat /tmp/last_file.txt), current: $(cat /tmp/current_file.txt)"

	if [ ! -e /tmp/current_file.txt ]; then
    /bin/cp /tmp/last_file.txt /tmp/current_file.txt;
	elif ! cmp -s /tmp/last_file.txt /tmp/current_file.txt; then
    echo "Lock file changed, starting processing"
    /bin/cp /tmp/last_file.txt /tmp/current_file.txt;
	else
    echo "Lock file UNCHANGED! continuing"
	  continue
  fi

  echo reco starting

	run=$(cat /tmp/last_file.txt | awk '{print $1}')
	fragment=$(cat /tmp/last_file.txt | awk '{print $2}')
	filename=$(cat /tmp/last_file.txt | awk '{print $3}')
	mode=$(cat /tmp/last_file.txt | awk '{print $4}')

	echo $run
	echo $fragment
	echo $mode
	echo './wrapper_with_timeout_for_process_single_fragment.sh ${run} $fragment $mode'
	echo "unpacked file in: $filename"
	./wrapper_with_timeout_for_process_single_fragment.sh $run $fragment $mode

done

cd $orig
