from os import path, mkdir
import startup
import pickle

from startup import djtissue, djanimal
from startup import project_root

class animal:
    animal_id = None
    local_folder = None
    def __init__(self, id):
        self.animal_id = id
        self.local_folder = project_root/ 'local' / str(id)

class retina_tissue(animal):
    retina_id = None
    retina_side = None
    def __init__(self, animalid, side):
        self.animal_id = animalid
        self.local_folder = project_root /'local' / str(self.animal_id)
        if (path.exists(self.local_folder)!=True):
            mkdir(self.local_folder)

        if (side in ['Left', 'Right']):
            self.retina_side = side
        else:
            Exception('Check your typo of side!')
            return

    def uploader(self, user_name):
        qdict = {}
        qdict['animal_id'] = self.animal_id
        qdict['side'] = self.retina_side
        query = djtissue.Retina & qdict
        result = query.fetch('tissue_id')
        if (result.size > 0):
            print('Retina tissue exists: ' + str(result))
            self.retina_id = result[0]
        else:
            eye_dict = {'animal_id':self.animal_id, 'side':self.retina_side}
            eye_query = djanimal.Eye & eye_dict
            eyein = eye_query.fetch('animal_id')
            if (eyein.size == 0):
                djanimal.Eye.insert1(eye_dict)

            djtissue.Tissue.insert1({'owner':user_name})
            #get automatically assigned tissue id
            self.retina_id = djtissue.Tissue.fetch('tissue_id', order_by='tissue_id desc', limit=1, as_dict=True)[0]
            self.retina_id = self.retina_id['tissue_id']
            djtissue.Retina.insert1({'tissue_id':self.retina_id, 'animal_id':self.animal_id,
                                    'side':self.retina_side})
            print('Inserting successful!')
        return

    def save_local(self):
        file_name = 'retina_tissue.plk'
        file_total_path = self.local_folder/file_name

        with open(file_total_path, 'wb') as f:
            pickle.dump(self, f)
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

        self.local_folder = project_root / 'local' / str(self.animal_id)
        if (path.exists(self.local_folder)!= True):
            mkdir(self.local_folder)

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
        result = query.fetch('tissue_id')
        if (bool(result)):
            print('brain slice tissue already exists!')
            self.brain_slice_id = result[0]
        else:
            #insert into sln_tissue.Tissue first
            djtissue.Tissue.insert1({'owner':user})
            inserted_brainslice = djtissue.Tissue.fetch('tissue_id', order_by='tissue_id desc',
                                                   limit=1, as_dict=True)[0]
            self.brain_slice_id = inserted_brainslice['tissue_id']
            djtissue.BrainSliceBatch.insert1({'tissue_id': self.brain_slice_id,
                                              'slicing_orientation': self.slice_orientation,
                                              'thickness': self.slice_thickness,
                                             'animal_id':self.animal_id})
        return

    def save_local(self):
        file_name = 'brian_slice_tissue.plk'
        total_path = self.local_folder/file_name
        with open(total_path, 'wb') as f:
            pickle.dump(self,f)
        return

    def downloader(self):
        #todo fill this functon
        return



