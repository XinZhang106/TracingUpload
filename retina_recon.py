import startup
from startup import djanimal, djtissue
import matplotlib.pyplot as plt
import os.path
import pandas as pd
from tissue_dj import retina_tissue
import numpy as np

def spherical_to_cartesian(lon_deg, lat_deg, radius=100):
    lon = np.radians(lon_deg * np.pi)
    lat = np.radians(lat_deg * np.pi)

    x = radius * np.cos(lat) * np.cos(lon)
    y = radius * np.cos(lat) * np.sin(lon)
    z = radius * np.sin(lat)

    return x, y, z


def azimuthal_equidistant_projection(theta, phi, r = 1):
    """
    Project spherical coordinates (r, theta, phi) to 2D Cartesian coordinates (x, y)
    using the azimuthal equidistant projection centered at the pole (phi = 0).

    Parameters:
    - r: radius (can be 1 for unit sphere)
    - theta: azimuthal angle (longitude-like), in radians
    - phi: polar angle (colatitude), in radians
    """
    # For unit sphere, use r = 1. Otherwise, scale the radial distance.
    rho = r * phi  # Linear scaling of polar angle to radial distance
    x = rho * np.sin(theta)
    y = rho * np.cos(theta)
    return x, y

class reconstruct(retina_tissue):
    celllist = None
    folder = None
    spheric = None
    cartesian = None
    reconed = False
    localfd = None

    def __init__(self,animalid, retinaside, retinaid = None):
        self.animal_id = animalid
        self.retina_side = retinaside
        self.local_folder = startup.project_root/'local'/str(animalid)
        if (retinaid==None):
            querydict = {}
            querydict['animal_id'] = animalid
            query = djtissue.Retina & querydict
            self.retina_id = query.fetch1('tissue_id')
        else:
            self.retina_id = retinaid
        return

    def recon_loader_local_reproj(self, reconfd, cellid_list, plot_2d = True):
        spherical = os.path.join(reconfd, 'RGCspherical.csv')
        if (os.path.exists(spherical)):
            self.folder = reconfd
            df = pd.read_csv(spherical, header = 0)
            self.spheric = np.zeros([len(df), 2])
            self.cartesian = np.zeros([len(df), 2])
            self.spheric[:, 0] = df['RGC.phi']
            self.spheric[:, 1] = df['RGC.lambda']
            #self.cartesian[:, 0], self.cartesian[:, 1], rando = spherical_to_cartesian(self.spheric[:, 1], self.spheric[:, 0])
            self.cartesian[:, 0], self.cartesian[:, 1] = azimuthal_equidistant_projection(self.spheric[:, 1],
                                                                                          self.spheric[:, 0])
            self.celllist = cellid_list
            self.reconed = True

            if (plot_2d):
                fig, ax = plt.subplots(figsize=(6, 6))

                for i in range(len(cellid_list)):
                    text = str(i+1)
                    text_x = self.cartesian[i, 0]
                    text_y = self.cartesian[i, 1]+self.cartesian[i,1]*0.1
                    ax.text(text_x, text_y, text, fontsize=9, ha='left', va='center')
                ax.scatter(self.cartesian[:, 0], self.cartesian[:, 1])
                ax.set_xlabel('- Nasal, + Temporal')
                ax.set_ylabel('-Ventral, + Dorsal')
                plotname = 'Recontruction_reprojection.png'
                outputpath = os.path.join(self.local_folder, plotname)
                if (os.path.exists(outputpath)):
                    os.remove(outputpath)

                #fig.draw()
                fig.tight_layout()
                fig.savefig(outputpath)

        else:
            Exception('Cannot find spherical coordinates file. Please check for RGCspherical.csv in the recon folder!')
        return

    def recon_upload(self):
        if (self.reconed):
            insertdict = {}
            insertdict['tissue_id'] = self.retina_id
            insertdict['animal_id'] = self.animal_id
            insertdict['side'] = self.retina_side

            insertdict['folder'] = self.folder
            insertdict['cell_ids'] = self.celllist
            insertdict['spherical'] = self.spheric
            insertdict['reproj'] = self.cartesian

            djtissue.RetinaRecon.insert1(insertdict)
            print('Reconstruction insertion successful!')
        return

    def recon_save_local(self):
        filename = 'retinarecon_summary.csv'
        outputpath = os.path.join(self.local_folder, filename)
        datadict = {}
        datadict['sphe_phi'] = self.spheric[:, 0]
        datadict['sphe_lambda'] = self.spheric[:, 1]
        datadict['carte_x'] = self.cartesian[:, 0]
        datadict['carte_y'] = self.cartesian[:, 1]
        df = pd.DataFrame(datadict)
        df.to_csv(outputpath, index = False, header=True)
        print('Saved to local: ' + str(outputpath))
        return



