from ferrari_core.registry import register_routine
import os

USE_CUDA = os.getenv("USE_CUDA", "0") == "1"

print(USE_CUDA)

if USE_CUDA:
    import cupy as xp
else:
    import numpy as xp


@register_routine("gaussian_filter")
def gaussian_filter(waves, lp_freq, sampling_rate, **kwargs):

    globals().update(kwargs)

    n = waves.shape[-1]

    # Frequency axis [GHz]
    freq = xp.fft.rfftfreq(n, d=1.0 / sampling_rate)

    # Gaussian sigma chosen so gain = 1/sqrt(2) at lp_freq
    sigma = lp_freq / xp.sqrt(xp.log(2))

    H = xp.exp(-(freq / sigma) ** 2)

    wf_fft = xp.fft.rfft(waves, axis=-1)
    wf_fft *= H[None, None, :]
    return xp.fft.irfft(wf_fft, n=n, axis=-1)
