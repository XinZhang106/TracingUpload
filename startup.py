import datajoint as dj
from pathlib import Path

project_root = Path(__file__).resolve().parent
dj.config["database.host"] = "vfsmdatajoint01.fsm.northwestern.edu"
dj.config["database.user"] = "Xin"
dj.config["database.password"] = "Xin_temppwd"
dj.conn()

brainslice_ori = ['Coronal', 'Vertical', 'Horizontal', 'Unknown']
retina_cut_ori = ['Dorsal', 'Ventral', 'Nasal', 'Temporal', 'Unknown']

#defining all relevant schemas and tables
djanimal = dj.create_virtual_module('djanimal', 'sln_animal')
djimage = dj.create_virtual_module('djimage', 'sln_image')
djtissue = dj.create_virtual_module('djtissue', 'sln_tissue')
djlab = dj.create_virtual_module('djlab', 'sln_lab')
djcell = dj.create_virtual_module('djcell', 'sln_cell')

#class for safe uploading/reloading of a new tissue collection

