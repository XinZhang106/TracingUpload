import tissue_load

new_tissue = tissue_load.tissue()

new_tissue.create_new_tissueCollection(3532)
#new_tissue.insert_retina('Left')
#new_tissue.insert_brainslice(100, 'Coronal')
new_tissue.brainslice_id = 152
new_tissue.retina_id = 150
new_tissue.save_as_dict()

