
from tissue_dj import animal, retina_tissue, brainSlice_tissue
from retina_image_dj import rgc_image_manager
from brain_image_dj import whole_brain_grouper

print ('Starting organizing imaging data... Input animal id:')
animal_id = int(input())
mouse = animal(animal_id)

print('side of the retina: ')
side = str(input())
rt = retina_tissue(animal_id, side)
rt.uploader()
