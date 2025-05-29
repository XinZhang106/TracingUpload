from pandas.core.window import Expanding

import startup
import pickle

from startup import djtissue, djanimal
from startup import project_root

class animal:
    animal_id = None
    local_folder = None
    def __init__(self, id):
        self.animal_id = id
        self.local_folder = project_root / str(id)

class retina_tissue(animal):
    retina_id = None
    retina_side = None
    def __init__(self, animalid, side):
        self.animal_id = animalid
        if (side in ['Left', 'Right']):
            self.retina_side = side
        else:
            Exception('Check your typo of side!')
            return

    def uploader(self, user_name):
        qdict = {}
        qdict['animal_id'] = self.animal_id
        qdict['side'] = self.retina_side
        query = djtissue & qdict
        result = query.fetch1('tissue_id')
        if (bool(result)):
            print('Retina tissue exists: ' + str(result['tissue_id']))
            self.retina_id = result['tissue_id']
        else:
            animal.Eye.insert1({'animal_id':self.animal_id, 'side':self.retina_side})
            djtissue.Tissue.insert1({'owner':user_name})
            #get automatically assigned tissue id
            self.retina_id = djtissue.Tissue.fetch('tissue_id', order_by='tissue_id desc', limit=1, as_dict=True)[0]
            djtissue.retina.insert1({'tissue_id':self.retina_id, 'animal_id':self.animal_id,
                                    'side':self.retina_side})
        return

    def save(self, as_dict = False):
        #todo finish this
        return

    def downloader(self):
        #todo
        return

class brainSlice_tissue(animal):
    brain_slice_id = None
    slice_thickness = 0
    slice_orientation = None

    def __init__(self, animal_id, thickness, orientation):
        self.animal_id = animal_id
        self.slice_thickness = thickness
        if (orientation in ['Coronal', 'Saggital', 'Horizontal']):
            self.slice_orientation = orientation
        else:
            Exception('Check your typo of slicing orientation!')
        return

    def uploader(self, user):
        #check if repeated
        qdic = {}
        qdic['animal_id'] = self.animal_id

        query = djtissue.BrainSliceBatch & qdic
        result = query.fetch1('tissue_id')
        if (bool(result)):
            print('brain slice tissue already exists!')
            self.brain_slice_id = result['tissue_id']
        else:
            #insert into sln_tissue.Tissue first
            djtissue.Tissue.insert1({'owner':user})
            self.brain_slice_id = djtissue.Tissue.fetch('tissue_id', order_by='tissue_id desc',
                                                   limit=1, as_dict=True)[0]
            djtissue.BrainSliceBatch.insert1({'tissue_id': self.brain_slice_id,
                                              'slicing_orientation': self.slice_orientation,
                                              'thickness': self.slice_thickness,
                                             'animal_id':self.animal_id})
        return

    def downloader(self):
        #todo fill this functon
        return



