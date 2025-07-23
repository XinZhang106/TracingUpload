import startup
from startup import djtissue, djanimal, djimage, djcell, project_root
import matplotlib.pyplot as plt
import numpy as np

#plot for topographic mapping
def get_ap_ml_fromDJ(sdim_list=None, animal_id = None):
    #the return is AP, ML, and sdimage id in this order
    if (sdim_list==None and animal_id==None):
        print('Need information for plotting!\n')
        return
    else:
        if(animal_id==None):
        #plotting by image id list
            ap = np.zeros([len(sdim_list),1])
            ml = np.zeros([len(sdim_list), 1])
            for i in range(len(sdim_list)):
                querydict = {'image_id': sdim_list[i]}
                query = djimage.AxonInBrain & querydict
                iminfo = query.fetch('image_id','medial_lateral', 'distance_from_fist_slice',
                                     as_dict = True)

                ap[i] = iminfo['distance_from_fist_slice']
                ml[i] = iminfo['distance_from_fist_slice']
            return ap, ml, sdim_list

        else:
            sliceq = {'animal_id': animal_id}
            query = djtissue.BrainSliceBatch & sliceq
            sliceid = query.fetch1('tissue_id')

            wb_qdict = {'tissue_id': sliceid}
            wb_proj = djimage.WholeBrainImage.proj('tissue_id') & wb_qdict

            #now query for whole brain image using the slice id
            super_proj = djimage.AxonInBrain.proj('distance_from_fist_slice', 'medial_lateral',
                                                  ref_image_id = 'whole_brain') * wb_proj

            data = super_proj.fetch(as_dict = True)
            ap = np.zeros([len(data),1])
            ml = np.zeros([len(data),1])
            imid = np.zeros([len(data),1])
            #now data is a list of dictionaries
            for i in range(len(data)):
                ap[i] = data[i]['distance_from_fist_slice']
                ml[i] = data[i]['medial_lateral']
                imid[i] = data[i]['image_id']

            return ap, ml, imid

def plot_sd_im_topo(ap, ml, sc_devide = None, saveassvg = True, animalid = None):
    #the purpose of this function is to see if images need to be combined to generate axons
    #for axon to RGC mapping, please refer to plot function 
    ax, fig = plt.subplots(figsize = [6,6])
    ax.scatter(ap, ml)

    if (sc_devide!=None):
        ax.axvline(x = sc_devide)

    if (saveassvg):
        if (animalid==None):
            print('Please input the id of the animal! Figure temporarily saved under folder LOCAL')
            filepath = project_root/'local'/'Spinning_disk_axon_topo.svg'

        else:
            filepath = project_root/str(animalid)/'Spinning_disk_axon_topo.svg'

        fig.savefig(filepath)
        print('Figure saved: ' + str(filepath))
    return


#plot for color ?mapping?

#testing block here
def main():
    ap, ml, imid = get_ap_ml_fromDJ(animal_id=3658)
    print(ap)
    print(ml)
    print(imid)
    return


if __name__ == "__main__":
    main()

