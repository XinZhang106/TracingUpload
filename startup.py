import datajoint as dj

dj.config["database.host"] = "vfsmdatajoint01.fsm.northwestern.edu"
dj.config["database.user"] = "Xin"
dj.config["database.password"] = "Xin_temppwd"
dj.conn()

brainslice_ori = ['Coronal', 'Vertical', 'Horizontal', 'Unknown']
retina_cut_ori = ['Dorsal', 'Ventral', 'Nasal', 'Temporal', 'Unkonwn']

#defining all relevant schemas and tables
animals = dj.create_virtual_module('animals', 'sln_animal')
images = dj.create_virtual_module('images', 'sln_image')
tissues = dj.create_virtual_module('tissues', 'sln_tissue')
lab = dj.create_virtual_module('lab', 'sln_lab')
who_are_you = 'Xin'

#class for safe uploading/reloading of a new tissue collection

