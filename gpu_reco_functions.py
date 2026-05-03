from multiprocessing import Pool

from scipy.signal import filtfilt, butter

import cupy as cp
import numpy as np

from cupyx.scipy import ndimage

def split(waveforms, pre=5, post=10, baseline_samples=20):

    # Assume waveforms is shape (E, C, S)
    E, C, S = waveforms.shape

    # Step 1: Find argmax along sample axis (shape: E x C)
    argmax_idx = cp.argmax(waveforms, axis=2)  # shape (E, C)

    # Step 2: Build offsets
    window_offsets = cp.arange(-pre, post).reshape(1, 1, -1)
    baseline_offsets = cp.arange(-pre - baseline_samples, -pre).reshape(1, 1, -1)

    # Expand argmax index for broadcasting
    argmax_exp = argmax_idx[:, :, cp.newaxis]  # shape (E, C, 1)

    # Add offsets and wrap with modulo S to stay in bounds
    window_indices   = (argmax_exp + window_offsets) % S
    baseline_indices = (argmax_exp + baseline_offsets) % S

    # Build broadcasted event/channel indices
    event_idx = cp.arange(E)[:, None, None]
    chan_idx  = cp.arange(C)[None, :, None]

    return argmax_idx, event_idx, chan_idx, window_indices, baseline_indices


def generic_reco(
  cpu_waves, detector_name, chid_dict, x_y_z_tuple,
  signal_samples_pre_peak=5, signal_samples_post_peak=10,
  charge_zerosup_peak_threshold=10,
  do_centroid=True,
  do_timing=True, rise_samples_pre_peak=5, rise_samples_post_peak=2, sampling_rate=5,
  timing_methods=["cf"], cf=0.12, timing_thr=None, interpolation_factor=20, lp_freq=None,
  rise_interp_left_samples=5, rise_interp_right_samples=5, clone_crilin_25=False,
  baseline_samples=20
):

  print("waves[0]", cpu_waves[0])

  if detector_name == "crilin" and clone_crilin_25:
    print("processing crilin, going from 9 to 225 channels by cloning waves by 25x: WIP")
    print("original shape: ", cpu_waves.shape)
    cpu_waves = np.repeat(cpu_waves, 25, axis=1)
    print("new shape: ", cpu_waves.shape)

  mempool = cp.get_default_memory_pool()

  print("Before transfers, using in GPU:, ", int(mempool.used_bytes()/(1024**2)), "MB")              # 0

  print("starting to transfer to VRAM")
  waves = cp.asarray(cpu_waves).astype(cp.float32)
  waves *= 1000./4096.

  print("transferred - starting processing")

  print("Before processing, using in GPU:, ", int(mempool.used_bytes()/(1024**2)), "MB")              # 0

  argmax_idx, event_idx, chan_idx, signal_indices, baseline_indices = split(waves, pre=signal_samples_pre_peak, post=signal_samples_post_peak)
  print("split done")

  baseline_waveforms = waves[event_idx, chan_idx, baseline_indices]
  baseline_means = baseline_waveforms.mean(axis=2)

  print("waves befroe sub: ", waves[0])
  waves = waves - cp.repeat(baseline_means[:, :, cp.newaxis], waves.shape[2], axis=2)  # baseline subtraction

  print("waves after sub: ", waves[0])

  print("baseline sub done")
  signal_waveforms = waves[event_idx, chan_idx, signal_indices]

  print("signal waves[0]: ", signal_waveforms[0])
  print("signal extr done")

  #if lp_freq is not None:
  #  B_coeff, A_coeff = butter(2, [lp_freq/(sampling_rate/2.)])
  #  signal_waveforms = filtfilt(B_coeff, A_coeff, signal_waveforms)

  event_idx_2d = cp.arange(waves.shape[0])[:, None]        # shape (E, 1)
  chan_idx_2d  = cp.arange(waves.shape[1])[None, :]        # shape (1, C)

  values_max = waves[event_idx_2d, chan_idx_2d, argmax_idx]  # shape (Event, Channels)

  mask_under_thr = values_max < charge_zerosup_peak_threshold #shape (Event, Channels)

  charge = cp.sum(signal_waveforms, axis=2)

  charge[mask_under_thr] = 0
  charge /= (50 * sampling_rate)

  charge_sum = cp.sum(charge, axis=1)

  print("charges done")

  tWave = cp.repeat(cp.arange(0, waves.shape[2])[cp.newaxis, :], waves.shape[1], axis=0)
  tWave = cp.repeat(tWave[cp.newaxis, :], waves.shape[0], axis=0).astype(float)
  tWave /= sampling_rate

  print("tWave created")

  return_dict = {}
  mask_selected_events = cp.ones((charge.shape[0],), dtype=bool)
  det = detector_name

  for var in chid_dict:
    return_dict.update({f"{det}_{var}": cp.repeat(chid_dict[var][cp.newaxis, :], waves.shape[0], axis=0)})
  print("chid in dict (all cpu) - done")

  if do_centroid:
    cpu_x, cpu_y, cpu_z = x_y_z_tuple
    x, y, z = cp.asarray(cpu_x), cp.asarray(cpu_y), cp.asarray(cpu_z)

    charge_ratios = charge/cp.repeat(cp.sum(charge, axis=1)[:, cp.newaxis], charge.shape[1], axis=1)
    x_centroid = charge_ratios @ x #shape: (Events, Channel) * (Channel) -> (Events)
    y_centroid = charge_ratios @ y #shape: (Events, Channel) * (Channel) -> (Events)

    print(type(x))
    z = cp.repeat(z[cp.newaxis, :], charge.shape[0], axis=0)
    y = cp.repeat(y[cp.newaxis, :], charge.shape[0], axis=0)
    x = cp.repeat(x[cp.newaxis, :], charge.shape[0], axis=0)
    print("centroid and geom vars done")
    print(type(x))

    return_dict.update({
      f"{det}_y": cp.asnumpy(y), f"{det}_x": cp.asnumpy(x), f"{det}_z": cp.asnumpy(z),
      f"{det}_y_centroid": cp.asnumpy(y_centroid), f"{det}_x_centroid": cp.asnumpy(x_centroid)
    })
    print("centroid and geom vars to cpu and in dict - done")

  if do_timing:

    valid = ~mask_under_thr                      # (E, C)

    rise = signal_waveforms[:, :,
        (signal_samples_pre_peak - rise_samples_pre_peak):
        (signal_samples_pre_peak + rise_samples_post_peak)
    ]

    print("rise:", rise[0][0])

    for timing_method in timing_methods:

        if timing_method == "cf":
            thresholds = values_max * cf

        elif timing_method == "fixed_thr":
            thresholds = cp.full((rise.shape[0], rise.shape[1]), timing_thr)

        else:
            raise NotImplementedError(f"method: {timing_method}")

        print("thresholds: ", thresholds[0][0])

        # ---------------------------------------------------------
        # SELECT ONLY VALID CHANNELS (NEW, key change)
        # ---------------------------------------------------------
        idx_valid = cp.where(valid)

        rise_valid = rise[idx_valid]              # (N_valid, T)
        thr_valid  = thresholds[idx_valid]        # (N_valid,)

        print("thr_valid: ", thr_valid[0])
        # ---------------------------------------------------------
        # FIRST CROSSING (UNCHANGED LOGIC, just 2D → 1D)
        # ---------------------------------------------------------
        prelim_pseudo_t = cp.argmax(
            rise_valid > thr_valid[:, None],
            axis=1
        )

        print("prelim_pseudo_t: ", prelim_pseudo_t[0])

        # ---------------------------------------------------------
        # BUILD WINDOW (UNCHANGED)
        # ---------------------------------------------------------
        offsets = cp.arange(
            -rise_interp_left_samples,
             rise_interp_right_samples + 1
        )

        idx = prelim_pseudo_t[:, None] + offsets[None, :]
        idx = cp.clip(idx, 0, rise_valid.shape[1] - 1)

        print("idx: ", idx[0])

        # ---------------------------------------------------------
        # EXTRACT SEGMENTS
        # ---------------------------------------------------------
        rise_segment = cp.take_along_axis(
            rise_valid,
            idx.astype(cp.int32),
            axis=1
        )

        print("rise_segment: ", rise_segment[0])

        # ---------------------------------------------------------
        # INTERPOLATION (ONLY VALID CHANNELS NOW)
        # ---------------------------------------------------------
        print("rise_segment.shape: ", rise_segment.shape)
        rise_segment_3d = rise_segment[:, None, :]   # restore fake channel axis

        rise_interp = ndimage.zoom(
            rise_segment_3d,
            [1, 1, interpolation_factor],
            order=3,
            prefilter=False
        )

        rise_interp = rise_interp[:, 0, :]  # remove dummy axis

        print("rise_interp.shape: ", rise_interp.shape)
        print("rise_interp: ", rise_interp[0])

        # ---------------------------------------------------------
        # SECOND CROSSING
        # ---------------------------------------------------------
        pseudo_t_valid = cp.argmax(
            rise_interp > thr_valid[:, None],
            axis=1
        ).astype(cp.float32)

        print("pseudot (1st step): ", pseudo_t_valid[0])

        # ---------------------------------------------------------
        # FINAL TIMING (UNCHANGED FORMULA)
        # ---------------------------------------------------------
        pseudo_t_valid += cp.random.uniform(
            low=-0.5,
            high=0.5,
            size=pseudo_t_valid.shape
        )

        pseudo_t_valid = (
            pseudo_t_valid / interpolation_factor
            + prelim_pseudo_t
            - rise_interp_left_samples
            + argmax_idx[idx_valid]   # IMPORTANT: match indexing
            - rise_samples_pre_peak
        )

        print("pseudot (final valid): ", pseudo_t_valid[0])

        print("peak pos,rise_samples_pre_peak,rise_interp_left_samples,prelim_pseudo_t,pseudo_t_valid / interpolation_factor", argmax_idx[idx_valid][0],rise_samples_pre_peak,rise_interp_left_samples,prelim_pseudo_t[0],pseudo_t_valid[0] / interpolation_factor)
        pseudo_t_valid /= sampling_rate

        # ---------------------------------------------------------
        # SCATTER BACK (restore original shape)
        # ---------------------------------------------------------
        pseudo_t = cp.zeros(mask_under_thr.shape, dtype=cp.float32)

        pseudo_t[idx_valid] = pseudo_t_valid
        print("pseudot, filled", pseudo_t[0])

        print("timing done")
        return_dict.update({f"{det}_{timing_method}_time": cp.asnumpy(pseudo_t)})
        print("timing to cpu and in dict - done")

  return_dict.update({
    f"{det}_peak_pos": cp.asnumpy(argmax_idx),
    f"{det}_peak": cp.asnumpy(values_max), f"{det}_charge": cp.asnumpy(charge), f"{det}_charge_sum": cp.asnumpy(charge_sum),
  })
  print("to cpu: done")

  return cp.asnumpy(mask_selected_events), return_dict

