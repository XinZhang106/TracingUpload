import pickle

import startup
from tissue_dj import retina_tissue, brainSlice_tissue
from brain_image_dj import whole_brain_grouper
from retina_image_dj import rgc_image_manager
from retina_recon import reconstruct
import Axon

# r_tis = retina_tissue(3658, 'Left')
# r_tis.uploader('Xin')
# r_tis.save_local()
#
# b_tis = brainSlice_tissue(3658, 100, 'Coronal')
# b_tis.uploader('Xin')
# b_tis.save_local()

wholebrainfolder =r"R:\Ophthalmology\Research\SchwartzLab\Images_by_animal\3658\3658_brainWF\whole"
wb = whole_brain_grouper(wholebrainfolder, 3658)
# wb.input_brain_per_slide([12, 8, 8, 8, 8, 8])
wb.get_upload_list()
wb.slide_num_info()
#wb.upload_whole_brain()
#wb.save_whole_brain_imInfo()
wb.parse_qupath_annotation(r"D:\localData\chromaTrace\3658\qupath_whole_brain\3658_axon_terminals.csv")
wb.save_parsed_annotation()

# f = r'D:\programming\pythonPrograms\TracingUpload\local\3534\retina_tissue.plk'
# with open(f, 'rb') as file:
#     retina_tissue = pickle.load(file)
#
# wholeretina = rgc_image_manager(retina_tissue)
# #wholeretina.assign_whole_retina('Dorsal',718)
# wholeretina.load_annotation(r"D:\localData\chromaTrace\3534\retinaWF\annotation.csv")
# wholeretina.rotate_rgc()
# wholeretina.plot_rotated_rgc()

#testing reonstruction module
# myrecon = reconstruct(3534, 'Left', 159)
# cellids = [10593, 10594, 10595]
# myrecon.recon_loader_local_reproj(r"D:\localData\chromaTrace\3534\recon", cellids)
# myrecon.recon_save_local()

# group = Axon.Axon_grouper(3534)
# terminalcsv = startup.project_root/'local'/'3534'/'3534_parsed_annotation.csv'
# group.load_and_plot_local_sdbrain(terminalcsv)
