import os.path

import pandas as pd
import numpy as np
import pickle
from os import listdir, path, mkdir
import re
from startup import project_root, djimage, djtissue
import tifffile, nd2
from tissue_dj import brainSlice_tissue, animal

def euDis_point_linebypoints(x1, y1, x2, y2, x3, y3):
    linevec = np.array([x2-x1, y2-y1])
    dotT2ine = np.array([x3-x1, y3-y1])
    #A X B  = |A| * |B| * sin(theta)
    distance  = np.abs(np.cross(linevec, dotT2ine))/np.linalg.norm(linevec)
    #print(dis)
    return distance

class whole_brain_grouper(brainSlice_tissue):
    im_folder = None
    whole_brain_data = {'im_name_list':[], 'im_ref_id_list':[],
                        'slide_num':[], 'brain_num':[]}
    brain_per_slide = []

    def __init__(self, im_folder, animal_id, brain= None):
        self.im_folder = im_folder
        self.animal_id = animal_id
        self.local_folder = project_root/'local'/str(self.animal_id)
        if (path.exists(self.local_folder)==False):
            mkdir(self.local_folder)

        if (bool(brain)):
            self.animal_id = animal_id
            self.slice_thickness = brain.slice_thickness
            self.brain_slice_id = brain
        else:
            qstr = 'animal_id = '+str(animal_id)
            query = djtissue.BrainSliceBatch & qstr
            result = query.fetch1('tissue_id', 'thickness')
            if (len(result)>0):
                self.brain_slice_id = result[0]
                self.slice_thickness = result[1]
                print('Getting brain id from DJ, branslicebatch id: ' + str(self.brain_slice_id))
            else:
                print('Cannot find brain slice batch of animal: '+ str(self.animal_id))
                Exception()
                return
        return

    def input_brain_per_slide(self, brain_num_array):
        for i in range(0, len(brain_num_array)):
            if (isinstance(brain_num_array[i], int)!=True):
                print('Brain number per slice must be integer!')
                Exception()

            print('slide '+ str(i+1) + ' brain number: '+str(brain_num_array[i]))
        self.brain_per_slide = brain_num_array
        print('re run function if there is any mistake')
        return

    def get_upload_list(self):
        allcontents = listdir(self.im_folder)
        self.whole_brain_data['im_name_list'] = [c for c in allcontents if c.endswith('.nd2')]

        myfilter = r's(\d+)_b(\d+)'
        for im in self.whole_brain_data['im_name_list']:
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
                self.whole_brain_data['im_ref_id_list'] = []
                Exception('Can not process whole brain image file: '+ im)
        return

    def upload_whole_brain(self): #either upload the whole_brain_data dictionary or getting ref_image_id back if already loaded
        qstr = 'tissue_id = ' + str(self.brain_slice_id)
        query = djimage.WholeBrainImage & qstr
        result = query.fetch(as_dict = True)
        if (len(result) == self.whole_brain_data['im_name_list']):
            print('Whole brain reference image uploaded, downloading ref_image_id instead...')
        else:
            if (len(result) == 0):
                print('No whole brain images have been uploaded, uploading now...')
            else:
                #todo check BUG!
                #djimage.WholeBrainImage.delete(qstr)
                Exception('whole brain image partially uploaded, please check!')

            for i in range(len(self.whole_brain_data['im_name_list'])):
                uploadDict = {'tissue_id': self.brain_slice_id,
                              'file_name': self.whole_brain_data['im_name_list'][i],
                              'folder': self.local_folder,
                              'slide_num': self.whole_brain_data['slide_num'][i],
                              'brain_num': self.whole_brain_data['brain_num'][i]}

                djimage.WholeBrainImage.insert1(uploadDict)
        self.download_whole_brain_id()
        # fetch the automatcially generated image ref ids after uploading
        return

    def save_whole_brain_imInfo(self):
        filename = 'whole_brain_refid.csv'
        filepath = self.local_folder/filename
        df = pd.DataFrame(self.whole_brain_data)
        df.to_csv(filepath, index= False)
        return

    def download_whole_brain_id(self):
        self.whole_brain_data['im_ref_id_list'] = np.zeros([len(self.whole_brain_data['im_name_list']), 1])
        querydict = {'tissue_id': self.brain_slice_id}
        query = djimage.WholeBrainImage & querydict
        new_ids_dictlis = query.fetch('ref_image_id', 'file_name',
                                                        limit=len(self.whole_brain_data['im_name_list']), as_dict=True)
        for i in range(len(new_ids_dictlis)):
            pair = new_ids_dictlis[i]
            id_index = self.whole_brain_data['im_name_list'].index(pair['file_name'])
            self.whole_brain_data['im_ref_id_list'][id_index] = pair['ref_image_id']

        self.whole_brain_data['im_ref_id_list'] = self.whole_brain_data['im_ref_id_list'].flatten()
        return

    def parse_qupath_annotation(self, qupath_csv):
        self.sdim_list = {}
        df = pd.read_csv(qupath_csv)
        annotated_image = set(df['Image'])
        for im in annotated_image:
            cleanName = im.split('-')[0].strip()
            #entrycount = df['Image'].str.contains(cleanName).sum()
            self.sdim_list[cleanName] = {'midline': np.zeros([2, 2]),
                                       'terminals':[]}

        totalrows = len(df)
        for i in range(0, totalrows):
            imagename = df['Image'][i].split("-")[0].strip()
            objname = df['Name'][i].strip()
            #wb_idx = self.whole_brain_data['im_name_list'].index(imagename)

            if ('ml1' in objname):
                self.sdim_list[imagename]['midline'][0,0] = df['Centroid X'][i]
                self.sdim_list[imagename]['midline'][0,1] = df['Centroid Y'][i]
                #self.sdim_list[cleanName]['midline'][0, :] = np.array([df['Centroid X'][i], df['Centroid Y'][i]])
            elif ('ml2' in objname):
                self.sdim_list[imagename]['midline'][1,0] = df['Centroid X'][i]
                self.sdim_list[imagename]['midline'][1,1] = df['Centroid Y'][i]
                #self.sdim_list[cleanName]['midline'][1, :] = np.array([df['Centroid X'][i], df['Centroid Y'][i]])
            elif ('t' in objname):
                terminal = np.zeros([3,1]).flatten()
                terminal[0] = df['Centroid X'][i]
                terminal[1] = df['Centroid Y'][i]
                terminal[2] = df['Perimeter'][i]
                #terminal = np.array([df['Centroid X'][i], df['Centroid Y'][i], df['Perimeter']])
                self.sdim_list[imagename]['terminals'].append(terminal)
            else:
                raise Exception('Annotation object name cannot be recogenized!')

        return

        #check if every image has at least two midline point
        allims = self.sdim_list.keys()

        for im in allims:
            midpoints = self.sdim_list[im]['midline']
            if (0 in midpoints):
                print('Warning: image ' + str(im) + 'is not being processed correctly: midline missing!')

        return

    def save_parsed_annotation(self, slicing_PtoA = True):
        all_ims = self.sdim_list.keys()
        flat_dict = {'index':[],'Image_name': [], 'ml':[],
                     'centroid_x':[], 'centroid_y':[],
                     'centroid_radius':[], 'multi_terminal':[],
                     'ap': []}
        idx = 0
        for im in all_ims:
            #iteration through all images
            im_item = self.sdim_list[im]
            if (len(im_item['terminals'])>1):
                multi_flag = 1
            else:
                multi_flag = 0
            for i in range(0, len(im_item['terminals'])):
                #iteration through all terminals within the same image
                flat_dict['Image_name'].append(im)
                flat_dict['index'].append(idx)
                idx +=1

                wb_index = self.whole_brain_data['im_name_list'].index(im)
                slide_num = self.whole_brain_data['slide_num'][wb_index]
                brain_num = self.whole_brain_data['brain_num'][wb_index]
                ap = self.calculate_AP(slide_num, brain_num, slicing_PtoA)
                flat_dict['ap'].append(ap)

                this_terminal  = im_item['terminals'][i]
                flat_dict['centroid_x'].append(this_terminal[0])
                flat_dict['centroid_y'].append(this_terminal[1])
                flat_dict['centroid_radius'].append(this_terminal[2]/6.28)
                flat_dict['multi_terminal'].append(multi_flag)

                ml = self.calculate_ML(im_item['midline'], this_terminal)
                flat_dict['ml'].append(ml)

        df = pd.DataFrame(flat_dict)
        filename = str(self.animal_id)+'_parsed_annotation.csv'
        outputpath = self.local_folder/filename
        if (os.path.exists(outputpath)):
            os.remove(outputpath)
        df.to_csv(outputpath, index = False)
        return


    def calculate_AP(self, slide_num, brain_num, slicing_backwards = True):
        prev_brain = int(brain_num)
        if (slide_num !=1):
            for i in range(int(slide_num)-1):
                prev_brain += self.brain_per_slide[i]

        ap = prev_brain * self.slice_thickness
        if (slicing_backwards):
            return -ap
        else:
            return ap

    def calculate_ML(self, midline_ps, centroid):
        distance = euDis_point_linebypoints(midline_ps[0,0], midline_ps[0,1],
                                 midline_ps[1,0], midline_ps[1,1],
                                 centroid[0], centroid[1])
        return distance

class sd_im_grouper(animal):
    sd_base_folder = None
    sd_table = None
    #uploading of spinning disk axon image is done in matlab
    
    def __init__(self, animalid, sd_base_folder):
        self.animal_id = animalid
        self.sd_base_folder = sd_base_folder
        return

    def load_whole_parse_table(self):
        filename = str(self.animal_id)+'_parsed_annotation.csv'
        path = self.local_folder/filename
        self.sd_table = pd.read_csv(path,index_col = 0)
        return

    def fill_table(self):


        return

    def assign_sdIm_toAxonIm(self):
        #todo
        return

    def download_image_id_to_table(self, original_folder):#input the folder where uploading into sln_image.Image happened
        image_id_list = []
        for i in range(len(self.sd_table)):
            qdict = {}
            qdict['image_filename'] = self.sd_table['Image_name'][i]
            qdict['folder'] = original_folder
            query = djimage.Image & qdict
            result = query.fetch1('image_id')
            if (bool(result)):
                image_id_list.append(result['image_id'])
            else:
                image_id_list.append(None)

        self.sd_table['image_id'] = image_id_list
        return

    def upload_shifted_tif(self, nd2p, tifp, maskp):
        #todo
        uploadingDict = {}
        uploadingDict['image_filename'] = tifp
        uploadingDict['folder'] = os.path.dirname(tifp)


        with nd2.ND2File(nd2p) as originalfile:
            metadata = originalfile.metadata
        return

















