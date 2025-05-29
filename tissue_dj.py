import startup
import pickle

from startup import tissues as TissueSchm
from startup import animals as AnimalSchm
from startup import project_root

class animal_basic_info:
    animal = None
    brainslice_id = None
    retina_id = None

class tissue_operator(animal_basic_info):
    def __init__(self):
        return

    def create_new_tissueCollection(self, animalid):
        self.animal = animalid
        return

    def insert_retina(self, retina_side, comment = None):
        qstr = 'animal_id = '+ str(self.animal)
        qstr2 = 'side = ' + '"' + retina_side + '"'
        query = TissueSchm.Retina() & qstr & qstr2
        result = query.fetch(as_dict=True)
        if (bool(result)):
            print('Retina already exists!')
        else:
            if comment:
                TissueSchm.Tissue.insert1({'owner': startup.who_are_you, 'tissue_info': comment})
            else:
                TissueSchm.Tissue.insert1({'owner': startup.who_are_you})
            id = TissueSchm.Tissue.fetch('tissue_id', order_by='tissue_id desc', limit=1, as_dict=True)[0]
            id = id['tissue_id']
            print('Tissue created: '+ str(id))

            #insert the eye
            query = AnimalSchm.Eye & qstr
            result = query.fetch(as_dict=True)
            if (bool(result)== False):
                #insert eye
                AnimalSchm.Eye.insert1({'animal_id': self.animal, 'side': retina_side})
                print('Inserting '+ retina_side + ' of animal: '+str(self.animal))

            #assign the newest tissue if to the retina
            TissueSchm.Retina.insert1({'tissue_id': id, 'animal_id': self.animal, 'side':retina_side})
            self.retina_id = id
            print('Inserting successful! Mouse: ' + str(self.animal)+', Retina tissue id: '+ str(self.retina_id))
        return

    def insert_brainslice(self, slicethick, slice_orientation, comment = None):
        qstr = 'animal_id= '+ str(self.animal)
        query = TissueSchm.BrainSliceBatch & qstr
        result = query.fetch(as_dict=True)
        if (bool(result)):
            print('Brain slice batch already exists!')
        else:
            if comment:
                TissueSchm.Tissue.insert1({'owner': startup.who_are_you, 'tissue_info': comment})
            else:
                TissueSchm.Tissue.insert1({'owner': startup.who_are_you})
            id = TissueSchm.Tissue.fetch('tissue_id', order_by='tissue_id desc', limit=1, as_dict=True)[0]
            id = id['tissue_id']
            print('Tissue created: '+ str(id))
            self.brainslice_id = id

            TissueSchm.BrainSliceBatch.insert1({'tissue_id': id,
                                                     'slicing_orientation': slice_orientation,
                                                     'thickness': slicethick,
                                                     'animal_id': self.animal})
            print ('Brain slice inserted, tissue id: ' + str(id))
        return

    def save_as_dict(self):
        # Get the path to the current file's directory

        # Define a path to the subfolder and file
        filename = str(self.animal)+'_tissue.plk'
        output_file = project_root / 'local' / filename

        # Write something to the file
        with open(output_file, 'wb') as f:
            pickle.dump(self, f)
        return

    def load_from_dict(self, animalid):
        return

    def download_from_DJ(self, animal_id):
        query_string = 'animal_id = ' + str(animal_id)
        retina = TissueSchm.Retina & query_string
        self.retina_id = retina.fetch(as_dict = True)['tissue_id']

        brainslice = TissueSchm.BrainSliceBatch & query_string
        self.brainslice_id = brainslice.fetch(as_dict = True)['tissue_id']

        self.animal = animal_id
        return



