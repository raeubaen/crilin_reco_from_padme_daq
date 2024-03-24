#!/bin/bash
python3 $7/step3_fromttree.py $5/run_$3/out_temp_$2.root $6/$3_$4/out_reco_$2.root $4 \
 --samplingrate 2.5 --seriessignalend 380 --crilin_rise_window_end 300 --charge_thr_for_series 20 --trigger_rise_window_end 300 --series_board 1
