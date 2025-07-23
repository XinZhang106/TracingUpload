import pickle

import matplotlib.pyplot as plt
import os
from PIL.Image import Image
from os import path, listdir, remove

from numpy.f2py.crackfortran import endifs

from startup import project_root, retina_cut_ori, djimage, djtissue, djcell
import numpy as np
from PIL import Image
import pandas as pd
from tissue_dj import retina_tissue
import roifile
class rgc_image_manager(retina_tissue):

    image_id = None #id the of retina whole image
    cut_orientation = None
    whole_im_path = None
    image = None
    stiched_image = None
    opn = np.array([0,0])
    dorsal = np.array([0,0])
    raw_rgc_coord = []
    rotated_rgc_coord = None
    recon_rgc_coord = []
    imaging_table = {'sdim_name_manual': [], 'sdim_id':[], 'zstack_name':[], 'zstack_id':[],
                     'cell_id':[], 'local_cell_id':[]}

    savefd = None

    def __init__(self, retina_tissue):
        self.animal_id = retina_tissue.animal_id
        self.retina_id = retina_tissue.retina_id
        self.retina_side = retina_tissue.retina_side
        self.savefd = project_root / 'local' / str(self.animal_id)
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

    def download_from_dj(self, animal_id, side):
        qstr = 'animal_id = ' + str(animal_id)
        qstr2 = 'side = "' + side + '"'
        query = djimage.WholeRetinaImage & qstr & qstr2
        result = query.fetch(as_dict = True)
        if (bool(result)==False):
            print('Retina not in the database please upload first!')
        else:
            self.image_id = result['image_id']
            self.side = side
            self.cut_orientation = result['cut_orientation']
            self.retina_id = result['tissue_id']
        return

    def assign_whole_retina(self, cut, imageid):

        if (cut in retina_cut_ori):
            self.cut_orientation = cut
            querystr = 'retina_id = ' + str(self.retina_id)
            query = djimage.WholeRetinaImage & querystr
            result = query.fetch(as_dict=True)
            if (bool(result)):
                print('Whole retina image already exists!')
                return

            insertDict = {'image_id': imageid, 'tissue_id': self.retina_id,
                          'cut_orientation': cut}
            djimage.WholeRetinaImage.insert1(insertDict)
        else:
            Exception('cut orientation cannot be recognized!')

        return

    def load_recon(self, reconFD):
        self.stiched_image = Image.open(path.join(reconFD, 'reconRetina.png'))
        mydf = pd.read_csv(path.join(reconFD, 'spherical.csv'),header = 0)
        self.recon_rgc_coord = mydf.to_numpy()
        return

    def rotate_rgc(self, save = True):
        rgcs = self.raw_rgc_coord - self.opn
        dorsal_vec = (self.dorsal - self.opn)
        dorsal_vec = dorsal_vec / (np.linalg.norm(dorsal_vec))
        self.rotated_rgc_coord = np.empty(np.shape(rgcs))

        if (self.retina_side == 'Right'):
            nasal_vec = np.array([dorsal_vec[1], -dorsal_vec[0]])
        elif (self.retina_side == 'Left'):
            nasal_vec = np.array([-dorsal_vec[1], dorsal_vec[0]])
        else:
            print ('Error: Eye side is unknown cannot calibrate. Exit function.')
            return
        changeBase = np.array([nasal_vec[0], dorsal_vec[0], nasal_vec[1], dorsal_vec[1]]).reshape([2, 2])
        oldTonew = np.linalg.inv(changeBase).astype('float64')

        for i in range(len(rgcs)):
            self.rotated_rgc_coord[i, :] = np.matmul(oldTonew, rgcs[i, :])

        if (save):
            tempdf = pd.DataFrame({'X': self.rotated_rgc_coord[:, 0], 'Y':self.rotated_rgc_coord[:, 1]})
            outputpath = os.path.join(self.savefd, 'rotated_rgc_coord.csv')
            tempdf.to_csv(outputpath, index = False)
            print('retina rotating finished. Please input rgc id to: '+outputpath)
        return

    def plot_rotated_rgc(self):
        if (self.rotated_rgc_coord.any()):
            figure, ax = plt.subplots(figsize= (6,6))
            ax.scatter(self.rotated_rgc_coord[:, 0], self.rotated_rgc_coord[:, 1])
            for i in range(len(self.rotated_rgc_coord)):
                ax.text(self.rotated_rgc_coord[i,0],
                        self.rotated_rgc_coord[i,1]+self.rotated_rgc_coord[i,1]*0.1,
                        str(i+1), fontsize = 9)
            ax.set_xlabel('+ Nasal')
            ax.set_ylabel('+ Dorsal')
            ax.set_title('RGC coordinates_no reconstruction')
            outputpath = os.path.join(self.savefd, 'rotated_RGC.png')
            if (os.path.exists(outputpath)):
                os.remove(outputpath)
            figure.savefig(outputpath)
            print('Figure saved for rotated RGC: '+ outputpath)
        else:
            print('No retina has not been rotated yet')
        return

    def load_annotation(self, anno_Folder):
        if (anno_Folder.endswith('.csv')):
            df = pd.read_csv(anno_Folder, header = 0)
            self.opn = np.array([df['X'][0], df['Y'][0]])
            self.dorsal = np.array([df['X'][1], df['Y'][1]])
            self.raw_rgc_coord = np.array([df['X'][2:], df['Y'][2:]])
            self.raw_rgc_coord = self.raw_rgc_coord.transpose()
        else:
            opnroi = roifile.ImagejRoi.fromfile(path.join(anno_Folder, 'opn.roi'))
            self.opn = opnroi.coordinates()

            dorsalroi = roifile.ImagejRoi.fromfile(path.join(anno_Folder, 'dorsal.roi'))
            self.dorsal = dorsalroi.coordinates()

            rgc = pd.read_csv(path.join(anno_Folder, 'rgc.csv'), header=0, index_col=0)
            self.raw_rgc_coord = rgc[['X', 'Y']].to_numpy()

            self.rotated_rgc_coord = self.rotate_rgc()
        return


    def prep_uploading_form(self, sd_base_folder, color_shift = False):
        subfds = [path.join(sd_base_folder, f) for f in listdir(sd_base_folder)]

        image_list = []
        for fd in subfds:
            filelist = listdir(fd)
            if (color_shift == False):
                file = [f for f in filelist if f.endswith('.nd2')]
                file = file[0]
            else:
                tifs = [f for f in filelist if f.endswith('.tif')]
                for t in tifs:
                    if (t != 'mask.tif'):
                        file = t

                image_list.append(path.join(fd,file))

        df = pd.DataFrame({'filename': image_list})
        uploadfilepath = project_root/'local'/str(self.animal_id)/'retina_sd_uploadlist.csv'
        df.to_csv(uploadfilepath, index= False)
        print('uploadign sd form prepared, now input cell ids manually...')
        return


    def get_confocal_cell_id(self, confocal_upload_fd, output = True):
        #todo what is that?
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

def main():
    retina = retina_tissue(3658, 'left')
    retina.retina_id = 160
    rgc_im = rgc_image_manager(retina)

    rgc_im.prep_uploading_form(r"D:\localData\chromaTrace\3658\retina_sd", True)
    return

#testing code
if __name__ == "__main__":
    main()

