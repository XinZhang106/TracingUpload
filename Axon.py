import pandas as pd
import matplotlib.pyplot as plt
from startup import project_root
import os

class Axon_grouper():

    save_fd = None

    def __init__(self, animal_id):
        self.save_fd = project_root/'local'/str(animal_id)
        return

    def load_and_plot_local_sdbrain(self, sdfilep):
        df = pd.read_csv(sdfilep, header = 0)
        maplist = df.index[df['Map'] == 1].tolist()
        figure, ax = plt.subplots(figsize=(6,6))

        ax.scatter(df['ap'][maplist], df['ml'][maplist])
        for i in range(len(maplist)):
            #print(tomap['Image_name'])
            this_idx = maplist[i]
            text = str(df['index'][this_idx])
            ax.text(df['ap'][this_idx], df['ml'][this_idx]+ df['ml'][this_idx]*0.01, text, fontsize=10, va = 'center')

        figure.show()
        outputpath = os.path.join(self.save_fd, 'SC_terminal_loc.png')
        if (os.path.exists(outputpath)):
            os.remove(outputpath)

        figure.savefig(outputpath)
        return

    def manualCombine_uploadingFile(self, sdfilep):
        df = pd.read_csv(sdfilep, header = 0)
        self.axon = []
        maplist = df.index[df['Map'] == 1].tolist()
        manulAxonIndex = df['']
        #for i in maplist:






