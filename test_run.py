from tissue_dj import retina_tissue, brainSlice_tissue
from brain_image_dj import whole_brain_grouper

# r_tis = retina_tissue(3534, 'Left')
# r_tis.uploader('Xin')
# r_tis.save_local()
#
# b_tis = brainSlice_tissue(3534, 100, 'Coronal')
# b_tis.uploader('Xin')
# b_tis.save_local()

wholebrainfolder = r"D:\localData\chromaTrace\3534\WF-brain\whole"
wb = whole_brain_grouper(wholebrainfolder, 3534)
wb.input_brain_per_slide([11, 8, 5, 8, 8, 6])
wb.get_upload_list()
wb.upload_whole_brain()
wb.save_whole_brain_imInfo()


