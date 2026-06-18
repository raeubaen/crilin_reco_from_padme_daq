from ferrari_core.registry import register_routine

@register_routine("example_reco")
def example_reco(tree, detector_name, detector_dict_piece):
  det = detector_name
  reco_dict = {}

  branches_list = []
  branches = tree.arrays(branches_list
    library="ak"
  )
  mask_dict = np.ones(len(branches_list[0]), dtype=bool)

  reco_dict.update({
  })

  return mask_dict, reco_dict


