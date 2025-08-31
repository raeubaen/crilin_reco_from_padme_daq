import numpy as np
from scipy import ndimage
from scipy.signal import filtfilt, butter

def split(waveforms, pre=5, post=10):

    # Assume waveforms is shape (E, C, S)
    E, C, S = waveforms.shape

    # Step 1: Find argmax along sample axis (shape: E x C)
    argmax_idx = np.argmax(waveforms, axis=2)  # shape (E, C)

    # Step 2: Build offsets
    window_offsets = np.arange(-pre, post).reshape(1, 1, -1)
    baseline_offsets = np.arange(-50, -pre - 10).reshape(1, 1, -1)

    # Expand argmax index for broadcasting
    argmax_exp = argmax_idx[:, :, np.newaxis]  # shape (E, C, 1)

    # Add offsets and wrap with modulo S to stay in bounds
    window_indices   = (argmax_exp + window_offsets) % S
    baseline_indices = (argmax_exp + baseline_offsets) % S

    # Build broadcasted event/channel indices
    event_idx = np.arange(E)[:, None, None]
    chan_idx  = np.arange(C)[None, :, None]

    return argmax_idx, event_idx, chan_idx, window_indices, baseline_indices


def generic_reco(
  waves, detector_name, chid_dict, x_y_z_tuple,
  signal_samples_pre_peak=5, signal_samples_post_peak=10,
  charge_zerosup_peak_threshold=10, seed_charge_threshold=50,
  do_centroid=True,
  do_timing=True, rise_samples_pre_peak=5, rise_samples_post_peak=2, sampling_rate=5,
  timing_method="cf", cf=0.12, timing_thr=None, interpolation_factor=20, lp_freq=None
):

  argmax_idx, event_idx, chan_idx, signal_indices, baseline_indices = split(waves, pre=signal_samples_pre_peak, post=signal_samples_post_peak)

  baseline_waveforms = waves[event_idx, chan_idx, baseline_indices]
  baseline_means = baseline_waveforms.mean(axis=2)

  waves = waves - np.repeat(baseline_means[:, :, np.newaxis], waves.shape[2], axis=2)  # baseline subtraction

  signal_waveforms = waves[event_idx, chan_idx, signal_indices]

  if lp_freq is not None:
    B_coeff, A_coeff = butter(2, [lp_freq/(sampling_rate/2.)])
    signal_waveforms = filtfilt(B_coeff, A_coeff, signal_waveforms)


  event_idx_2d = np.arange(waves.shape[0])[:, None]        # shape (E, 1)
  chan_idx_2d  = np.arange(waves.shape[1])[None, :]        # shape (1, C)

  values_max = waves[event_idx_2d, chan_idx_2d, argmax_idx]  # shape (Event, Channels)

  mask_under_thr = values_max < charge_zerosup_peak_threshold #shape (Event, Channels)

  charge = np.sum(signal_waveforms, axis=2)
  charge[mask_under_thr] = 0

  tWave = np.repeat(np.arange(0, waves.shape[2])[np.newaxis, :], waves.shape[1], axis=0)
  tWave = np.repeat(tWave[np.newaxis, :], waves.shape[0], axis=0).astype(float)
  tWave /= sampling_rate



  return_dict = {}
  mask_selected_events = np.ones((charge.shape[0],), dtype=bool)
  det = detector_name

  for var in chid_dict:
    return_dict.update({f"{det}_{var}": np.repeat(chid_dict[var][np.newaxis, :], waves.shape[0], axis=0)})


  if do_centroid:
    x, y, z = x_y_z_tuple
    # amplitude_map of the 5x5 matrix
    charge_ratios = charge/np.repeat(np.sum(charge, axis=1)[:, np.newaxis], charge.shape[1], axis=1)
    print(charge_ratios.shape, x.shape)
    x_centroid = charge_ratios @ x #shape: (Events, Channel) * (Channel) -> (Events)
    y_centroid = charge_ratios @ y #shape: (Events, Channel) * (Channel) -> (Events)

    z = np.repeat(z[np.newaxis, :], charge.shape[0], axis=0)
    y = np.repeat(y[np.newaxis, :], charge.shape[0], axis=0)
    x = np.repeat(x[np.newaxis, :], charge.shape[0], axis=0)

    return_dict.update({
      f"{det}_y": y, f"{det}_x": x, f"{det}_z": z,
      f"{det}_y_centroid": y_centroid, f"{det}_x_centroid": x_centroid
    })

  if do_timing:
    rise = signal_waveforms[:, :, (signal_samples_pre_peak - rise_samples_pre_peak):(signal_samples_pre_peak + rise_samples_post_peak)]
    rise_interp = ndimage.zoom(rise, [1, 1, interpolation_factor])


    if timing_method == "cf":
      peak_interp = rise_interp.max(axis=2) #shape: (Events, Channel) - on y axis
      thresholds = peak_interp*cf #values_max*cf
      return_dict.update({f"{det}_peak_interp": peak_interp})

    elif timing_method == "fixed_thr":
      thresholds = np.ones((rise.shape[0], rise.shape[1]))*timing_thr

    else:
      raise NotImplemented(f"method: {timing_method} not implemented")


    pseudo_t = np.argmax(rise_interp > np.repeat((thresholds)[:, :, np.newaxis], rise_interp.shape[2], axis=2), axis=2).astype(float)

    pseudo_t += np.random.uniform(low=-0.5, high=0.5, size=pseudo_t.shape)

    pseudo_t /= float(sampling_rate*interpolation_factor)

    pseudo_t += ((argmax_idx - rise_samples_pre_peak)/ sampling_rate)
    return_dict.update({f"{det}_cf_time": pseudo_t})

  save_waves_mask = np.random.uniform(size=(waves.shape[0],)) > 0.01
  waves[save_waves_mask, ...] = 0
  tWave[save_waves_mask, ...] = 0

  return_dict.update({
    f"{det}_peak_pos": argmax_idx,
    f"{det}_peak": values_max, f"{det}_charge": charge,
    f"{det}_wave": waves, f"{det}_t_wave": tWave
  })


  return mask_selected_events, return_dict
