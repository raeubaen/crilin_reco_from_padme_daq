
# Reconstruction for crilin July ("Elisa" output of Padme DAQ)
import json
import sys
import ROOT
import numpy as np
import argparse
import time
from scipy.signal import filtfilt, butter

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

def zero_all_vars(vars):
  for key in vars:
    var = vars[key]
    var *= 0

def tree_var(tree, name, shape, npvartype, rootvartype):
  dtype = npvartype
  var = np.zeros(shape, dtype=dtype)
  shape_str = "".join(["[%i]"%i for i in shape])
  tree.Branch(name, var, "%s%s/%s"%(name,shape_str,rootvartype))
  return var

ROOT.gErrorIgnoreLevel = ROOT.kFatal

parser = argparse.ArgumentParser(description='Online monitor and reconstruction for crilin July')

parser.add_argument('infile', type=str, help='Input file name .root')
parser.add_argument('outfile', type=str, help='outfile', default="")
parser.add_argument('label', type=str, help='label', default="")
parser.add_argument('--frontboard', type=int, help='Board. in front', default=0)
parser.add_argument('--timeoffset', type=float, help='time offset (ns)', default=0)
parser.add_argument('--offset', type=int, help='Start event number', default=0)
parser.add_argument('--maxevents', type=int, help='Number of events', default=100000)
parser.add_argument('--crilinnsamples', type=int, help='Nsamples per waveform', default=1024)
parser.add_argument('--triggernsamples', type=int, help='Nsamples per waveform', default=1000)
parser.add_argument('--globalnsamples', type=int, help='Nsamples per waveform', default=1000)
parser.add_argument('--samplingrate', type=float, help='GHz sampling rate', default=5)
parser.add_argument('--boardsnum', type=int, help='Number of boards', default=1)
parser.add_argument('--chsnum', type=int, help='Number of channels per board', default=18)
parser.add_argument('--series_board', type=int, help='board in series (1 if only parallel) - then set boardsnum=1', default=0)
parser.add_argument('--seriessignalstart', type=float, help='Series Signal start (ns)', default=24)
parser.add_argument('--seriessignalend', type=float, help='Series Signal end (ns)', default=160)
parser.add_argument('--lgsignalstart', type=float, help='lead glass Signal start (ns)', default=250)
parser.add_argument('--lgsignalend', type=float, help='lead glass Signal end (ns)', default=315)
parser.add_argument('--parallelsignalstart', type=float, help='Series Signal start (ns)', default=145)
parser.add_argument('--parallelsignalend', type=float, help='Series Signal end (ns)', default=250)
parser.add_argument('--triggersignalstart', type=int, help='Series Signal start (ns)', default=60)
parser.add_argument('--triggersignalend', type=int, help='Series Signal end (ns)', default=190)
parser.add_argument('--parallel_lowedge_fromtpeak', type=float, help="parallel charge integration low bound from tpeak", default=-35)
parser.add_argument('--parallel_highedge_fromtpeak', type=float, help="parallel charge integration high bound from tpeak", default=150)
parser.add_argument('--series_lowedge_fromtpeak', type=float, help="series charge integration low bound from tpeak", default=-5)
parser.add_argument('--series_highedge_fromtpeak', type=float, help="series charge integration high bound from tpeak", default=80)
parser.add_argument('--lg_lowedge_fromtpeak', type=float, help="lead glass charge integration low bound from tpeak", default=-25)
parser.add_argument('--lg_highedge_fromtpeak', type=float, help="lead glass charge integration high bound from tpeak", default=40)
parser.add_argument('--trigger_lowedge_fromtpeak', type=float, help="trigger charge integration low bound from tpeak", default=-20)
parser.add_argument('--trigger_highedge_fromtpeak', type=float, help="trigger charge integration high bound from tpeak", default=50)
parser.add_argument('--debug', type=int, help='Plot all check plots', default=0)
parser.add_argument('--chs', type=str, help='reco only ch list es. "[1, 2, 3, 4]"', default=0)
parser.add_argument('--zerocr_thr', type=float, help='Zerocr threshold for fit start', default=80)
parser.add_argument('--zerocr_cf', type=float, help='Zerocr CF for fit end', default=0.75)
parser.add_argument('--trigger_thr_start', type=float, help='Fixed threshold for trigger timing (start) mV', default=50)
parser.add_argument('--trigger_thr_end', type=float, help='Fixed threshold for trigger timing (end) mV', default=250)
parser.add_argument('--check_timing', type=int, help='Plot if timing fails', default=0)
parser.add_argument('--lpfilter', type=int, help='2-order Butterworth active', default=1)
parser.add_argument('--charge_thr_for_series', type=float, help='Charge thr on crilin series channels', default=5)
parser.add_argument('--charge_thr_for_lg', type=float, help='Charge thr on lead glass channels', default=15)
parser.add_argument('--charge_thr_for_parallel', type=float, help='Charge thr on crilin parallel channels', default=0)
parser.add_argument('--charge_thr_for_trigger', type=float, help='Charge thr on crilin series channels', default=0)
parser.add_argument('--crilin_rise_window_end', type=float, help='End of window where signal rise is accepted', default=80)
parser.add_argument('--crilin_rise_window_start', type=float, help='Start of window where signal rise is accepted', default=24)
parser.add_argument('--lg_rise_window_end', type=float, help='End of window where signal rise is accepted', default=300)
parser.add_argument('--lg_rise_window_start', type=float, help='Start of window where signal rise is accepted', default=250)
parser.add_argument('--trigger_rise_window_end', type=float, help='End of window where signal rise is accepted', default=90)
parser.add_argument('--trigger_rise_window_start', type=float, help='Start of window where signal rise is accepted', default=50)
parser.add_argument('--rise_min_points', type=int, help='Minimium number of points in the monotonic rise to accept the event', default=8)
parser.add_argument('--timingwithoutfilter', type=float, help='timingwithoutfilter', default=0)
parser.add_argument('--serieslpfreq', type=float, help='Series Low pass filter cut frequency (GHz)', default=0.25)
parser.add_argument('--parallellpfreq', type=float, help='Parallel Low pass filter cut frequency (GHz)', default=0.25)
parser.add_argument('--lglpfreq', type=float, help='Parallel Low pass filter cut frequency (GHz)', default=0.5)
parser.add_argument('--triggerlpfreq', type=float, help='Trigger Low pass filter cut frequency (GHz)', default=0.5)
parser.add_argument('--seriespseudotime_cf', type=float, help='Pseudotime CF', default=0.11)
parser.add_argument('--lgpseudotime_cf', type=float, help='Pseudotime CF', default=0.11)
parser.add_argument('--parallelpseudotime_cf', type=float, help='Pseudotime CF', default=0.11)
parser.add_argument('--zerocr', type=int, help='Evaluate Zerocrossing time', default=1)
parser.add_argument('--centroid_square_cut_thr', type=float, help='Threshold in mm on abs centroid x and y', default=2.5)
parser.add_argument('--rmscut', type=float, help='cut on pre signal rms (mV)', default=10)
parser.add_argument('--saveallwave', type=int, help='save ala waves', default=0)


args = parser.parse_args()
v = vars(args)
print(v)
vars().update(v)

outf = ROOT.TFile(outfile, "RECREATE")
outf.cd()
tree = ROOT.TTree("tree", "tree")
tree.SetAutoSave(1000)

with open("%s"%outfile.replace('.root', '.json'), 'w') as fp:
    json.dump(vars(args), fp)

std_shape = (boardsnum, chsnum+5)

tree_vars = AttrDict()
tree_vars.update({
  "pre_signal_bline": tree_var(tree, "pre_signal_bline", std_shape, np.float32, "F"),
  "pre_signal_rms": tree_var(tree, "pre_signal_rms", std_shape, np.float32, "F"),
  "pedestal": tree_var(tree, "pedestal", std_shape, np.float32, "F"),
  "evnum": tree_var(tree, "evnum", (1,), np.int32, "I"),
  "charge": tree_var(tree, "charge", std_shape, np.float32, "F"),
  "ampPeak": tree_var(tree, "ampPeak", std_shape, np.float32, "F"),
  "timePeak": tree_var(tree, "timePeak", std_shape, np.float32, "F"),
  "timeAve": tree_var(tree, "timeAve", std_shape, np.float32, "F"),
  "savewave": tree_var(tree, "savewave", (1,), np.int32, "I"),
  "wave": tree_var(tree, "wave", (std_shape[0], std_shape[1], globalnsamples), np.float32, "F"),
  "unfiltered_wave": tree_var(tree, "unfiltered_wave", (std_shape[0], std_shape[1], globalnsamples), np.float32, "F"),
  "tWave": tree_var(tree, "tWave", (globalnsamples,), np.float32, "F"),
  "chi2_zerocr": tree_var(tree, "chi2_zerocr", std_shape, np.float32, "F"),
  "time_zerocr": tree_var(tree, "time_zerocr", std_shape, np.float32, "F"),
  "sumcharge": tree_var(tree, "sumcharge", (boardsnum,), np.float32, "F"),
  "single_e_flag": tree_var(tree, "single_e_flag", (1,), np.int32, "I"),
  "time_pseudotime": tree_var(tree, "time_pseudotime", std_shape, np.float32, "F"),
  "time_pseudotime_corr": tree_var(tree, "time_pseudotime_corr", std_shape, np.float32, "F"),
  "time_trig": tree_var(tree, "time_trig", (boardsnum, 4), np.float32, "F"),
  "centroid_x": tree_var(tree, "centroid_x", (2,), np.float32, "F"),
  "centroid_y": tree_var(tree, "centroid_y", (2,), np.float32, "F"),
  "centroid_x_all_layers": tree_var(tree, "centroid_x_all_layers", (1,), np.float32, "F"),
  "centroid_y_all_layers": tree_var(tree, "centroid_y_all_layers", (1,), np.float32, "F"),
  "centroid_cut_flag": tree_var(tree, "centroid_cut_flag", (1,), np.int32, "I"),
  "front_board": tree_var(tree, "front_board", (1,), np.int32, "I"),
})

if args.chs != 0:
  chlist = [int(i) for i in args.chs.strip('][').split(', ')]
  if 19 not in chlist: chlist.append(19)
  if 20 not in chlist: chlist.append(20)
  chiter = chlist
else: chiter = list(range(chsnum))
chiter.insert(0, chsnum+4)
for i in [3, 2, 1, 0]: chiter.insert(0, chsnum+i) #expects ntuple with chsnum+4 channels (last 4 are trigger)

#gestire canali trigger, vanno analizzati prima degli altri per sottrarre timing

f = ROOT.TFile(infile)
intree = f.Get("NTU")

t = np.arange(globalnsamples)/samplingrate

novalidrise = 0
failed = 0
no_zerocr = 0

maxevents = min(maxevents, intree.GetEntries())

tree_vars.front_board[0] = frontboard

for ev in range(maxevents):
  if intree.GetEntry(ev-offset) <= 0:
    continue

  to_discard = 1
  zero_all_vars(tree_vars)

  period = int(maxevents/100)
  if period==0: period=5

  if ev%period==0:
    print("Event: %i"%ev)
    if np.random.uniform() < 0.1:
      tree_vars.savewave[0] = 1

  tree_vars.evnum[0] = ev+offset

  for board in range(boardsnum):
    for ch in chiter: # makes trigger channels before

      if ch>=chsnum+4: continue #NO LEAD GLASS FOR NOW
      elif ch==chsnum+4:
        B_pb, A_pb = butter(2, [lglpfreq/(samplingrate/2.)])
        signalstart = lgsignalstart + timeoffset
        signalend = lgsignalend + timeoffset
        rise_window_start = lg_rise_window_start + timeoffset
        rise_window_end = lg_rise_window_end + timeoffset
        amp = -1 * np.asarray(intree.Waves)[crilinnsamples*chsnum*board + 30*crilinnsamples : crilinnsamples*chsnum*board + (30+1)*crilinnsamples][:globalnsamples]
        thr, cf = zerocr_thr, zerocr_cf
        pseudotime_cf = lgpseudotime_cf
        charge_thr = charge_thr_for_lg
        lowedge_fromtpeak = lg_lowedge_fromtpeak
        highedge_fromtpeak = lg_highedge_fromtpeak
      elif ch >= chsnum:
        B_pb, A_pb = butter(2, [triggerlpfreq/(samplingrate/2.)])
        signalstart = triggersignalstart + timeoffset
        signalend = triggersignalend + timeoffset
        rise_window_start = trigger_rise_window_start + timeoffset
        rise_window_end = trigger_rise_window_end + timeoffset
        thr = trigger_thr_start
        amp = np.asarray(intree.WavesTrig)[triggernsamples*4*board + (ch-chsnum)*triggernsamples : triggernsamples*4*board + (ch-chsnum+1)*triggernsamples][:globalnsamples]
        charge_thr = charge_thr_for_trigger
        lowedge_fromtpeak = trigger_lowedge_fromtpeak
        highedge_fromtpeak = trigger_highedge_fromtpeak
      else:
        amp = np.asarray(intree.Waves)[crilinnsamples*chsnum*board + ch*crilinnsamples:crilinnsamples*chsnum*board + (ch+1)*crilinnsamples][:globalnsamples]

        if board==series_board:
          B_pb, A_pb = butter(2, [serieslpfreq/(samplingrate/2.)])
          signalstart = seriessignalstart + timeoffset
          signalend = seriessignalend + timeoffset
          pseudotime_cf = seriespseudotime_cf
          rise_window_start = crilin_rise_window_start + timeoffset
          rise_window_end = crilin_rise_window_end + timeoffset
          thr, cf = zerocr_thr, zerocr_cf
          charge_thr = charge_thr_for_series
          lowedge_fromtpeak = series_lowedge_fromtpeak
          highedge_fromtpeak = series_highedge_fromtpeak
        else:
          B_pb, A_pb = butter(2, [parallellpfreq/(samplingrate/2.)])
          signalstart = parallelsignalstart + timeoffset
          signalend = parallelsignalend + timeoffset
          pseudotime_cf = parallelpseudotime_cf
          rise_window_start = crilin_rise_window_start + timeoffset
          rise_window_end = crilin_rise_window_end + timeoffset
          rise_ind = np.logical_and(t>rise_window_start, t<rise_window_end)
          thr, cf = zerocr_thr, zerocr_cf
          charge_thr = charge_thr_for_parallel
          lowedge_fromtpeak = parallel_lowedge_fromtpeak
          highedge_fromtpeak = parallel_highedge_fromtpeak

      virgin_amp = amp.copy()

      if lpfilter:
        amp = filtfilt(B_pb, A_pb, amp)

      bline_t_start = 0; bline_t_end = signalstart

      pre_signal_index = np.logical_and(t > bline_t_start, t < bline_t_end)
      if np.sum(pre_signal_index) == 0: #for safety
        continue
      pre_signal_amp = amp[pre_signal_index]
      temp_pre_signal_bline = pre_signal_amp.mean()
      temp_pre_signal_rms = pre_signal_amp.std()

      amp -= temp_pre_signal_bline
      pre_signal_amp = amp[pre_signal_index]

      temp_pedestal = pre_signal_amp[:-1].sum()  / (50 * samplingrate) / (signalstart-1) * (signalend - signalstart)

      signal_index = np.logical_and(t > signalstart, t < signalend)
      signal_amp = amp[signal_index]
      signal_t = t[signal_index]

      temp_charge = signal_amp.sum()  / (50 * samplingrate) # V * ns * 1e3 / ohm = pC

      if temp_charge < charge_thr or temp_pre_signal_rms > rmscut:
        if debug:
          print(
          "Rejected for tempCharge or BaslineRMS - Event: ", ev,
          ", Board: ", board,
          ", Channel: ", ch,
          ", Charge: ", temp_charge,
          ", Baseline RMS: ", temp_pre_signal_rms,
          )
          c = ROOT.TCanvas("c")
          g = ROOT.TGraphErrors(globalnsamples, t.astype(np.float64), amp.astype(np.float64), np.zeros(globalnsamples,), np.ones(globalnsamples,)*temp_pre_signal_rms)
          g.SetMarkerStyle(20)
          g.SetMarkerSize(.7)
          g.Draw("AP")

          input()

        continue
      else:
        if ch<18:
          to_discard = 0

      tree_vars.pre_signal_bline[board][ch] = temp_pre_signal_bline
      tree_vars.pre_signal_rms[board][ch] = temp_pre_signal_rms
      tree_vars.pedestal[board][ch] = temp_pedestal
      tree_vars.charge[board][ch] = temp_charge

      tree_vars.timeAve[board][ch] = (signal_amp*signal_t).sum() / signal_amp.sum()

      if saveallwave or tree_vars.savewave[0]:
        tree_vars.wave[board, ch, :] = amp
        tree_vars.tWave[:] = t
        if lpfilter: tree_vars.unfiltered_wave[board, ch, :] = virgin_amp


      novalidrise = 0

      rise_ind = np.logical_and(t>rise_window_start, t<rise_window_end)
      rise_t = t[rise_ind]
      rise_amp = amp[rise_ind]
      overthr_ind = rise_amp > thr
      rise_t = rise_t[overthr_ind]
      rise_amp = rise_amp[overthr_ind]

      monotone_rise_ind_groups = np.split(np.arange(len(rise_amp)), np.where(np.diff(rise_amp) < 0)[0]+1)
      monotone_rise_ind = []
      for group in monotone_rise_ind_groups:
        if len(group) > rise_min_points:
          monotone_rise_ind = group
          break

      if len(monotone_rise_ind)==0:
        novalidrise = 1
        tree_vars.ampPeak[board][ch] = -99
        tree_vars.timePeak[board][ch] = -99
        tree_vars.time_zerocr[board][ch] = -99
        tree_vars.time_pseudotime[board][ch] = -99
      else:
        firstind = monotone_rise_ind[0]
        lastind = monotone_rise_ind[-1]
        monotone_rise_t = rise_t[firstind:lastind+4]
        monotone_rise_amp = rise_amp[firstind:lastind+4]
        tree_vars.ampPeak[board][ch] = monotone_rise_amp.max()
        tree_vars.timePeak[board][ch] = monotone_rise_t[monotone_rise_amp.argmax()]

        signal_index = np.logical_and(t > tree_vars.timePeak[board][ch] + lowedge_fromtpeak, t < tree_vars.timePeak[board][ch] + highedge_fromtpeak)
        signal_amp = amp[signal_index]

        tree_vars.charge[board][ch] = signal_amp.sum()  / (50 * samplingrate) # V * ns * 1e3 / ohm = pC

        no_zerocr = 0
        failed = 0
        zerocr_func = "pol2" #### MUST ME POL1, FIX ME

        try:
          if ch >= chsnum and ch != chsnum+4:
            zerocr_func = "pol2"
            tstart_zerocr = monotone_rise_t[monotone_rise_amp>trigger_thr_start][0]
            tend_zerocr = monotone_rise_t[monotone_rise_amp>trigger_thr_end][0]
          else:
            tstart_zerocr = monotone_rise_t[0]
            tend_zerocr = monotone_rise_t[monotone_rise_amp>cf*tree_vars.ampPeak[board][ch]][0]
        except IndexError:
          if check_timing: no_zerocr = 1
        else:
          if not args.timingwithoutfilter:
            g = ROOT.TGraphErrors(globalnsamples, t.astype(np.float64), amp.astype(np.float64), np.zeros(globalnsamples,), np.ones(globalnsamples,)*temp_pre_signal_rms)
          else:
            g = ROOT.TGraphErrors(globalnsamples, t.astype(np.float64), virgin_amp.astype(np.float64), np.zeros(globalnsamples,), np.ones(globalnsamples,)*temp_pre_signal_rms)
          if zerocr:
            func = ROOT.TF1("func", zerocr_func, tstart_zerocr, tend_zerocr)
            g.Fit(func, "RQ")
            tree_vars.chi2_zerocr[board][ch] = func.GetChisquare()
            f_recovery = ROOT.TF1("f_recovery", zerocr_func, tstart_zerocr-15, tend_zerocr)
            f_recovery.SetParameters(func.GetParameters())
            x_zerocr = f_recovery.GetX(0)
            if ROOT.TMath.IsNaN(x_zerocr):
              x_zerocr = -99
              if check_timing: failed = 1
            tree_vars.time_zerocr[board][ch] = x_zerocr


          wsp = ROOT.TSpline5("wsp", g)

          spf = lambda x, par: wsp.Eval(x[0])
          sptf1 = ROOT.TF1("spf", spf, tstart_zerocr-5, tend_zerocr);

          try:
            if ch >= chsnum and ch != chsnum+4: x_pseudot = sptf1.GetX(thr)
            else: x_pseudot = sptf1.GetX(pseudotime_cf*tree_vars.ampPeak[board][ch])

            if ROOT.TMath.IsNaN(x_pseudot):
              x_pseudot = -99
              if check_timing: failed = 1
          except:
              x_pseudot = -99
              if check_timing: failed = 1

          tree_vars.time_pseudotime[board][ch] = x_pseudot
          if ch == chsnum+4: tree_vars.time_pseudotime_corr[board][ch] = x_pseudot - tree_vars.time_trig[board][int(30/8)]
          elif ch >= chsnum: tree_vars.time_trig[board][ch-chsnum] = x_pseudot
          else: tree_vars.time_pseudotime_corr[board][ch] = x_pseudot - tree_vars.time_trig[board][int(ch/8)]

      if check_timing or (debug and (failed or no_zerocr or novalidrise)):
        print(
          "Event: ", ev,
          ", Board: ", board,
          ", Channel: ", ch,
          ", Tstart: ", 0 if novalidrise else tstart_zerocr,
          ", Tend: ", 0 if novalidrise else tend_zerocr,
          ", Timepeak: ", tree_vars.timePeak[board][ch],
          ", Amppeak: ", tree_vars.ampPeak[board][ch],
          ", ZerocrTime: ", tree_vars.time_zerocr[board][ch],
          ", ZerocrChi2: ", tree_vars.chi2_zerocr[board][ch],
          ", Pseudotime: ", tree_vars.time_pseudotime[board][ch],
          ", Charge: ", tree_vars.charge[board][ch],
          ", Failed GetX: ", failed,
          ", No_zerocr: ", no_zerocr,
          ", Novalidrise: ", novalidrise
        )
        c = ROOT.TCanvas("c")
        if novalidrise or no_zerocr:
          g = ROOT.TGraphErrors(globalnsamples, t.astype(np.float64), amp.astype(np.float64), np.zeros(globalnsamples,), np.ones(globalnsamples,)*temp_pre_signal_rms)
          g.SetMarkerStyle(20)
          g.SetMarkerSize(.7)
          g.Draw("AP")
        else:
          g.SetMarkerStyle(20)
          g.SetMarkerSize(.7)
          g.Draw("AP")
          if not no_zerocr:
            wsp.Draw("same")
            sptf1.Draw("same")
            sptf1.SetLineColor(ROOT.kGreen)

        input()

    crilin_charges = tree_vars.charge[board][0:18]
    tree_vars.sumcharge[board] = crilin_charges.sum()

  if not to_discard:
    x = np.asarray([int(i/2)%3-1 for i in range(18)])
    y = np.asarray([int(int(i/2)/3)-1 for i in range(18)])
    temp_centroid_x, temp_centroid_y = 0, 0
    for board in range(boardsnum):
      temp_charge = tree_vars.charge[board][0:18]
      temp_centroid_x += (x*temp_charge).sum()
      temp_centroid_y += (y*temp_charge).sum()
      if temp_charge.sum() == 0:
        tree_vars.centroid_x[board] = -99
        tree_vars.centroid_y[board] = -99
      else:
        tree_vars.centroid_x[board] = (x*temp_charge).sum()/(temp_charge.sum())*10
        tree_vars.centroid_y[board] = (y*temp_charge).sum()/(temp_charge.sum())*10

    tree_vars.centroid_x_all_layers[0] = temp_centroid_x/(tree_vars.sumcharge[:].sum())*10
    tree_vars.centroid_y_all_layers[0] = temp_centroid_y/(tree_vars.sumcharge[:].sum())*10
    tree_vars.centroid_cut_flag[0] = int( abs(tree_vars.centroid_x[0])<centroid_square_cut_thr and abs(tree_vars.centroid_y[0])<centroid_square_cut_thr )
    tree.Fill()

outf.cd()
tree.Write()
outf.Close()
f.Close()
