from ferrari_core.registry import register_routine
import numpy as np

@register_routine("post_reco_crilin")
def post_reco_crilin(mask, reco, **kwargs):

  globals().update(kwargs)


  for layer in range(5):
    charge = reco["crilin_charge"].copy()

    charge[reco["crilin_layer"] != layer] = 0

    charge_sum = np.sum(charge, axis=1)

    charge_fraction = np.zeros_like(charge)
    charge_fraction[charge_sum>0] = charge[charge_sum>0] / charge_sum[charge_sum>0][:, None]

    w = np.maximum(0.0, w0_log_centroid + np.log(np.clip(charge_fraction, 1e-8, None)))

    w /= (np.sum(w, axis=1, keepdims=True))

    ix_centroid = w @ reco["crilin_ix"][0]
    iy_centroid = w @ reco["crilin_iy"][0]

    reco.update({f"crilin_ix_centroid_layer_{layer}": ix_centroid, f"crilin_iy_centroid_layer_{layer}": iy_centroid})

    reco.update({
      f"crilin_charge_sum_layer_{layer}": charge_sum,
      f"crilin_charge_central_layer_{layer}": np.sum(charge*(reco["crilin_ix"]==0)*(reco["crilin_iy"]==0), axis=1),
      f"crilin_charge_fraction_layer_{layer}": charge_fraction}
    )

  return mask, reco
