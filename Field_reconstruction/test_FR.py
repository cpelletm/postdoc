import sys
sys.path.append('/home/clement/Postdoc/python/Perso')
import numpy as np
import matplotlib.pyplot as plt
import Field_reconstruction.FR as fr
import Mat_data_processing as mdp
import analyse as an



scan=mdp.NVAFM_scan_matFile('/home/clement/Postdoc/python/Perso/Field_reconstruction/scan_20230827_001.mat')
scanData=scan.dataDic['RFFreq forward'][:78]
scanData=an.gradientCompensation(scanData)

ma=fr.maskArray()
ma.create(baseArray=scanData)

# import imageio.v3 as iio
# im=iio.imread('/home/clement/Postdoc/python/Perso/Field_reconstruction/test_scan.png')
# ma=fr.maskArray()
# ma.create(baseArray=im[:,:,0])