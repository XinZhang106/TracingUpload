import pandas as pd
import numpy as np
import pickle
from os import listdir,path
import re
from startup import project_root, djimage, djtissue
import tifffile
from tissue_dj import brainSlice_tissue

class whole_brain_grouper(brainSlice_tissue):
    im_folder = None
    whole_brain_data = {'im_name_list':[], 'image_ref_id_list':[],
                        'slide_num':[], 'brain_num':[]}
    brain_per_slide = []

    def __init__(self, im_folder, animal_id = None, brain= None):
        self.im_folder = im_folder
        if (brain):
            self.animal_id = brain.animal_id
            self.slice_thickness = brain.slice_thickness
            self.brain_slice_id = brain.brain_slice_id
        elif(animal_id):
            qstr = 'animal_id = '+str(animal_id)
            query = djtissue.BrainSliceBatch & qstr
            result = query.fetch1('tissue_id', 'thickness')
            self.slice_thickness = result['thickness']
            self.brain_slice_id = result['tissue_id']
            #download from datajoint
        else:
            print('Must fill least animal id or import brain class!')

        return

    def get_upload_list(self):
        allcontents = listdir(self.im_folder)
        self.whole_brain_data['im_name_list'] = [c for c in allcontents if c.endswith('.nd2')]
        self.whole_brain_data['image_ref_id_list'] = np.zeros([len(self.im_name_list),1])
        myfilter = r'_s(\d+)_b(\d+)_'
        for im in self.im_name_list:
            match = re.search(myfilter, im)
            if match:
                slide = match.group(1)
                self.whole_brain_data['slide_num'].append(slide)
                brain = match.group(2)
                self.whole_brain_data['brain_num'].append(brain)
            else:
                #roll back to avoid repeated rows
                self.whole_brain_data['slide_num'] = []
                self.whole_brain_data['brain_num'] = []
                self.whole_brain_data['im_name_list'] = []
                self.whole_brain_data['im_name_list'] = []
                self.whole_brain_data['im_ref_id_list'] = []
                Exception('Can not process whole brain image file: '+ im)
        return

    def upload_whole_brain(self):
        qstr = 'tissue_id = ' + self.brain_slice_id
        query = djimage.WholeBrainImage & qstr
        result = query.fetch(as_dict = True)
        if (bool(result)):
            Exception('whole brain images already loaded!')
        else:
            for i in range(self.whole_brain_data['im_name_list']):
                uploadDict = {'tissue_id': self.brain_slice_id,
                              'file_name': self.whole_brain_data['im_name_list'][i],
                              'folder': self.local_folder,
                              'slide_num': self.whole_brain_data['slide_num'][i],
                              'brain_num': self.whole_brain_data['brain_num'][i]}


            djimage.WholeBrainImage.insert1(uploadDict)

        # fetch the automatcially generated image ref ids after uploading
        new_ids_dictlis = djimage.WholeBrainImage.fetch('ref_image_id', order_by = 'ref_image_id desc',
                                                                  limist = len(self.image_ref_id_list), as_dict = True)
        self.whole_brain_data['image_ref_id_list'] = [a['ref_image_id'] for a in new_ids_dictlis]
        return

    def down_load_whole_brain(self):
        #todo
        return

    def parse_qupath_annotation(self, qupath_csv, whole_brain_data):
        self.sdim_list = {}
        df = pd.read_csv(qupath_csv)
        annotated_image = set(df['Image'])
        for im in annotated_image:
            cleanName = im.split('-')[0].strip()
            #entrycount = df['Image'].str.contains(cleanName).sum()
            self.sdim_list[cleanName] = {'midline': np.zeros([2, 2]),
                                       'terminals':[]}

        for i in range(len(df)):
            imagename = df.iloc['Image'][i].split("-")[0].strip()
            objname = df.iloc['Name'][i].strip()
            wb_idx = whole_brain_data['im_name_list'].index(imagename)

            if (objname == 'ml1'):
                self.sdim_list[imagename]['midline'][0, :] = np.array([df['Centroid X'][i], df['Centroid Y'][i]])
            elif (objname == 'ml2'):
                self.sdim_list[imagename]['midline'][1, :] = np.array([df['Centroid X'][i], df['Centroid Y'][i]])
            elif (objname.contains('t')):
                self.sdim_list[imagename]['terminals'].append([df['Centrois X'][i], df['Centroid Y'][i]])
            else:
                Exception('Annotation object name cannot be recogenized!')
                return
        return

    def save_parsed_annotation(self):
        all_ims = self.im_list.keys()
        flat_dict = {'index':[],'Image_name': [], 'ML1x':[], 'ML1y':[],
                     'ML2x':[], 'ML2y':[], 'centroid_x':[], 'centroid_y':[], 'multi_terminal':[],
                     'slide_num': [], 'brain_num':[]}
        idx = 0
        for im in all_ims:
            #iteration through all images
            im_item = all_ims[im]
            if (len(im_item['terminals'])>1):
                multi_flag = 1
            else:
                multi_flag = 0
            for i in range(0, len(im_item['terminals'])):
                #iteration through all terminals within the same image
                flat_dict['Image_name'].append(im)
                flat_dict['index'].append(idx)
                idx +=1
                flat_dict['ML1x'].append(im_item['midline'][0, 0])
                flat_dict['ML1y'].append(im_item['midline'][0, 1])
                flat_dict['ML2x'].append(im_item['midline'][1, 0])
                flat_dict['ML2y'].append(im_item['midline'][1, 1])
                flat_dict['centroid_x'].append(im_item['terminals'][i][0])
                flat_dict['centroid_y'].append(im_item['terminals'][i][1])
                flat_dict['multi_terminal'].append(multi_flag)

        df = pd.DataFrame(flat_dict)
        filename = str(self.animal_id)+'_parsed_annotation.csv'
        path = self.local_folder/filename
        df.to_csv(path, index = False)
        return



    def save(self, as_csv = False):
        #todo solve this
        if (as_csv == True):
            df = pd.DataFrame(self.whole_brain_data)
            file_name = str(self.animal)+'_wholeBrain_ref_id.csv'
            inputfile = self.local_folder/file_name
            df.to_csv(index=False)
        else:
            filename = str(self.animal) + '_wholeBrain.plk'
            inputfile = self.local_folder / filename
            with open(inputfile, 'wb') as f:
                pickle.dump(self, f)
            print('Whole brain saved as: ' + str(inputfile))
        return

    def calculate_AP(self):
        query['tissue_id'] = self.
        return

    def calculate_ML(self):
        return


class annotation_parse(animal_basic_info):
    im_list = {}






#spinning disk brain is mostly dealt in matlab
#class spinningDisk_brain:















