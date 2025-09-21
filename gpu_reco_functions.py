from multiprocessing import Pool

from scipy.signal import filtfilt, butter

import cupy as cp

from cupyx.scipy import ndimage

def split(waveforms, pre=5, post=10):

    # Assume waveforms is shape (E, C, S)
    E, C, S = waveforms.shape

    # Step 1: Find argmax along sample axis (shape: E x C)
    argmax_idx = cp.argmax(waveforms, axis=2)  # shape (E, C)

    # Step 2: Build offsets
    window_offsets = cp.arange(-pre, post).reshape(1, 1, -1)
    baseline_offsets = cp.arange(-50, -pre - 10).reshape(1, 1, -1)

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
  timing_method="cf", cf=0.12, timing_thr=None, interpolation_factor=20, lp_freq=None
):



  mempool = cp.get_default_memory_pool()
  pinned_mempool = cp.get_default_pinned_memory_pool()

  # You can access statistics of these memory pools.
  print(mempool.used_bytes())              # 0
  print(mempool.total_bytes())             # 0
  print(pinned_mempool.n_free_blocks())    # 0


  print("starting to transfer to VRAM")
  waves = cp.asarray(cpu_waves)
  waves *= 1000./4096

  print("transferred - starting split")

  print(mempool.used_bytes())              # 0
  print(mempool.total_bytes())             # 0
  print(pinned_mempool.n_free_blocks())    # 0

  argmax_idx, event_idx, chan_idx, signal_indices, baseline_indices = split(waves, pre=signal_samples_pre_peak, post=signal_samples_post_peak)
  print("split done")

  baseline_waveforms = waves[event_idx, chan_idx, baseline_indices]
  baseline_means = baseline_waveforms.mean(axis=2)

  waves = waves - cp.repeat(baseline_means[:, :, cp.newaxis], waves.shape[2], axis=2)  # baseline subtraction

  print("baseline sub done")
  signal_waveforms = waves[event_idx, chan_idx, signal_indices]

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

    # amplitude_map of the 5x5 matrix
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
    rise = signal_waveforms[:, :, (signal_samples_pre_peak - rise_samples_pre_peak):(signal_samples_pre_peak + rise_samples_post_peak)]
    rise_interp = ndimage.zoom(rise, [1, 1, interpolation_factor])


    if timing_method == "cf":
      peak_interp = rise_interp.max(axis=2) #shape: (Events, Channel) - on y axis
      thresholds = peak_interp*cf #values_max*cf
      return_dict.update({f"{det}_peak_interp": cp.asnumpy(peak_interp)})

    elif timing_method == "fixed_thr":
      thresholds = cp.ones((rise.shape[0], rise.shape[1]))*timing_thr

    else:
      raise NotImplemented(f"method: {timing_method} not implemented")


    pseudo_t = cp.argmax(rise_interp > cp.repeat((thresholds)[:, :, cp.newaxis], rise_interp.shape[2], axis=2), axis=2).astype(float)

    pseudo_t += cp.random.uniform(low=-0.5, high=0.5, size=pseudo_t.shape)

    pseudo_t /= float(sampling_rate*interpolation_factor)

    pseudo_t += ((argmax_idx - rise_samples_pre_peak)/ sampling_rate)
    print("timing done")
    return_dict.update({f"{det}_cf_time": cp.asnumpy(pseudo_t)})
    print("timing to cpu and in dict - done")

  save_waves_mask = cp.random.uniform(size=(waves.shape[0],)) > 0.01
  waves[save_waves_mask, ...] = 0
  tWave[save_waves_mask, ...] = 0
  print("masking waves done")

  return_dict.update({
    f"{det}_peak_pos": cp.asnumpy(argmax_idx),
    f"{det}_peak": cp.asnumpy(values_max), f"{det}_charge": cp.asnumpy(charge), f"{det}_charge_sum": cp.asnumpy(charge_sum),
    f"{det}_wave": cp.asnumpy(waves), f"{det}_t_wave": cp.asnumpy(tWave)
  })
  print("to cpu: done")

  return cp.asnumpy(mask_selected_events), return_dict
