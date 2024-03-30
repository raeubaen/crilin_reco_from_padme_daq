#!/bin/bash
python3 $7/step3_fromttree.py $5/run_$3/out_temp_$2.root $6/$3_$4/out_reco_$2.root $4 \
--series_board 1 --rmscut 100 --triggersignalstart 150 --triggersignalend 300 --trigger_rise_window_end 200 --trigger_rise_window_start 150
