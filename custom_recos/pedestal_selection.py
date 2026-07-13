from ferrari_core.registry import register_routine
import os

import numpy as xp


@register_routine("pedestal_selection")
def pedestal_selection(global_infos, **kwargs):

    globals().update(kwargs)

    print(global_infos)
    return (global_infos["arrays"]["event_trigger_mask"] == 64)
