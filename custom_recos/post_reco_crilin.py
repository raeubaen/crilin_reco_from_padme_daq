from ferrari_core.registry import register_routine
import numpy as np


def centroid(fractions, w0_log_centroid, x_or_y):
    w = np.maximum(0.0, w0_log_centroid + np.log(np.clip(fractions, 1e-8, None)))

    w /= (np.sum(w, axis=1, keepdims=True))

    return w @ x_or_y



@register_routine("post_reco_crilin")
def post_reco_crilin(mask, reco, **kwargs):

  globals().update(kwargs)

  peak_noise_flag = reco["crilin_peak"] > charge_zerosup_peak_threshold/reco["crilin_gain"]

  peak = reco["crilin_peak"] * peak_noise_flag

  peak_sum = np.sum(peak, axis=1)

  peak_fraction = np.zeros_like(peak)
  peak_fraction[peak_sum>0] = peak[peak_sum>0] / peak_sum[peak_sum>0][:, None]

  ix_centroid = centroid(peak_fraction, w0_log_centroid, reco["crilin_ix"][0])
  iy_centroid = centroid(peak_fraction, w0_log_centroid, reco["crilin_iy"][0])

  reco.update({
    f"crilin_peak_thr_yes": peak,
    f"crilin_peak_thr_yes_sum": peak_sum,
    f"crilin_peak_thr_yes_fraction": peak_fraction}
  )
  reco.update({f"crilin_ix_centroid": ix_centroid, f"crilin_iy_centroid": iy_centroid})

  for layer in range(5):

    peak_current_layer = peak * (reco["crilin_layer"] == layer)

    peak_current_layer_sum = np.sum(peak_current_layer, axis=1)

    peak_current_layer_fraction = np.zeros_like(peak_current_layer)
    peak_current_layer_fraction[peak_current_layer_sum>0] = peak[peak_current_layer_sum>0] / peak_sum[peak_current_layer_sum>0][:, None]

    ix_centroid_current_layer = centroid(peak_fraction, w0_log_centroid, reco["crilin_ix"][0])
    iy_centroid_current_layer = centroid(peak_fraction, w0_log_centroid, reco["crilin_iy"][0])

    reco.update({f"crilin_ix_centroid_layer_{layer}": ix_centroid_current_layer, f"crilin_iy_centroid_layer_{layer}": iy_centroid_current_layer})

    reco.update({
      f"crilin_peak_thr_yes_sum_layer_{layer}": peak_current_layer_sum,
      f"crilin_peak_thr_yes_central_layer_{layer}": np.sum(peak_current_layer*(reco["crilin_ix"]==0)*(reco["crilin_iy"]==0), axis=1),
      f"crilin_peak_thr_yes_fraction_layer_{layer}": peak_current_layer_fraction}
    )

  reco.update({
      f"crilin_peak_noise_flag": peak_noise_flag
  })

  return mask, reco
