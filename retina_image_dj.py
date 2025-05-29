import pickle
import roifile
from PIL.Image import Image
from os import path, listdir, remove
from startup import project_root, retina_cut_ori, djimage, djtissue, djcell
import numpy as np
from PIL import Image
import pandas as pd
from tissue_dj import retina_tissue

class rgc_image_manager(retina_tissue):

    image_id = None #id the of retina whole image
    cut_orientation = None
    whole_im_path = None
    image = None
    stiched_image = None
    opn = np.zeros([2,1])
    dorsal = np.zeros([2,1])
    raw_rgc_coord = []
    rotated_rgc_coord = []
    recon_rgc_coord = []
    imaging_table = {'sdim_name_manual': [], 'sdim_id':[], 'zstack_name':[], 'zstack_id':[],
                     'cell_id':[], 'local_cell_id':[]}

    def __init__(self, retina_tissue):
        self.animal = retina_tissue.animal
        self.retina_id = retina_tissue.retina_id
        return

    def load_local(self):
        filename = str(self.animal)+'_wholeretina.plk'
        input_file = project_root / 'local' / filename
        with open(input_file, 'rb') as f:
            loaded = pickle.load(f)

        self = loaded
        return

    def save(self):
        filename = str(self.animal)+'_wholeretina.plk'
        output_file = self.local_folder/filename
        with open(output_file, 'wb') as f:
            pickle.dump(self, output_file)
        return

    # def download_from_dj(self, animal_id, side):
    #     qstr = 'animal_id = ' + str(animal_id)
    #     qstr2 = 'side = "' + side + '"'
    #     query = images.WholeRetinaImage & qstr & qstr2
    #     result = query.fetch(as_dict = True)
    #     if (bool(result)==False):
    #         print('Retina not in the database please upload first!')
    #     else:
    #         self.image_id = result['image_id']
    #         self.side = side
    #         self.cut_orientation = result['cut_orientation']
    #         self.retina_id = result['tissue_id']
    #     return

    def assign_whole_retina(self, tissue_pickle, cut, imageid):
        self.cut_orientation = cut
        querystr = 'retina_id = '+str(self.retina_id)
        query = djimage.WholeRetinaImage & querystr
        result = query.fetch(as_dict=True)
        if (bool(result)):
            print('Whole retina image already exists!')
            return

        insertDict = {'image_id' : imageid, 'tissue_id': self.retina_id,
                      'cut_orientation': cut}
        djimage.WholeRetinaImage.insert1(insertDict)

        return

    def load_recon(self, reconFD):
        self.stiched_image = Image.open(path.join(reconFD, 'reconRetina.png'))
        mydf = pd.read_csv(path.join(reconFD, 'spherical.csv'),header = 0)
        self.recon_rgc_coord = mydf.to_numpy()
        return

    def rotate_rgc(self, side):
        rgcs = self.raw_rgc_coord - self.opn
        dorsal_vec = (self.dorsal - self.opn)
        dorsal_vec = dorsal_vec / (np.linalg.norm(dorsal_vec))
        self.rotated_rgc_coord = np.empty(np.shape(rgcs))

        if (side == 'Right'):
            nasal_vec = np.array([dorsal_vec[1], -dorsal_vec[0]])
        elif (side == 'Left'):
            nasal_vec = np.array([-dorsal_vec[1], dorsal_vec[0]])
        else:
            print ('Error: Eye side is unknown cannot calibrate. Exit function.')
            return
        changeBase = np.array([nasal_vec[0], dorsal_vec[0], nasal_vec[1], dorsal_vec[1]]).reshape([2, 2])
        oldTonew = np.linalg.inv(changeBase).astype('float64')

        for i in range(len(rgcs)):
            self.rotated_rgc_coord[i, :] = np.matmul(oldTonew, rgcs[i, :])
        return

    def load_annotation(self, anno_Folder):

        opnroi = roifile.ImagejRoi.fromfile(path.join(anno_Folder, 'opn.roi'))
        self.opn = opnroi.coordinates()

        dorsalroi = roifile.ImagejRoi.fromfile(path.join(anno_Folder, 'dorsal.roi'))
        self.dorsal = dorsalroi.coordinates()

        rgc = pd.read_csv(path.join(anno_Folder, 'rgc.csv'), header = None)
        self.raw_rgc_coord = rgc.to_numpy()
        self.rotated_rgc_coord = self.rotate_rgc()
        return

    def get_confocal_cell_id(self, confocal_upload_fd, output = True):
        nd2ims = [im for im in listdir(confocal_upload_fd) if im.endswith('.nd2')]
        q = {'folder': confocal_upload_fd}
        for im in nd2ims:
            q['image_filename'] = im
            query = djimage.Image & q
            result = query.fetch1('image_id')
            if (bool(result)==False):
                print('Cannot find image--'+str(path.join(confocal_upload_fd, im)))
                return
            else:
                self.imaging_table['zstack_name'].append(im)
                self.imaging_table['zstack_id'].append(result['image_id'])
                cell_qeury = {}
                cell_qeury['image_id'] = result['image_id']
                result2 = djimage.RetinalCellImage & cell_qeury
                self.imaging_table['cell_id'].append(result2['cell_unid'])

        if (output):
            cfc_fname = str(self.animal)+'_sd_and_zstack_info.csv'
            output_file = project_root / 'local' /cfc_fname
            df = pd.DataFrame(self.imaging_table)
            df.to_csv(output_file, index = False)
        return

    #manually input local cell id and fname for spinning disk file
    #todo function for uploading spinning disk images

    def get_sd_id(self, output = True):
        temp_id_ar = np.zeros([len(self.imaging_table['cell_id']),1])
        for i in range(len(self.imaging_table['cell_id'])):
            qstr = 'cell_unid = ' + str(self.imaging_table['cell_id'][i])
            query = djimage.AxonInBrain & qstr
            result = query.fetch1('image_id')
            if (bool(result)):
                temp_id_ar[i] = result['image_id']
            else:
                Exception('Cannot find the spinning disk')

        self.imaging_table['sdim_id'] = temp_id_ar

        if (output):
            cfc_fname = str(self.animal) + '_sd_and_zstack_info.csv'
            output_file = project_root / 'local' / cfc_fname
            if (path.exists(output_file)):
                remove(output_file)

            df = pd.DataFrame(self.imaging_table)
            df.to_csv(output_file, index = False)

        return

















