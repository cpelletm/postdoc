from analyse import *
import Mat_data_processing as mat

def scan_0725():
    fname='/home/clement/Postdoc/Data/202407 CrSBr/scans/scan_20240725_002.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['Norm forward']
    a=a.T
    plot_map(a, vAxis=[scan.xmin,scan.xmax], hAxis=[scan.ymin, scan.ymax], invertH=True,invertV=True, correctGradient=False, color='RdBu', colorBarLabel='Norm (a.u.)')

def Vz_0725():
    fname='/home/clement/Postdoc/Data/202407 CrSBr/scans/scan_20240725_002.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['Vz forward']
    a=a*2/7*1000
    a=a-a[0,0]
    a=a.T
    plot_map(a, vAxis=[scan.xmin,scan.xmax], hAxis=[scan.ymin, scan.ymax], invertH=True,invertV=True, correctGradient=True, color='viridis', colorBarLabel='Vz (nm)')

def ESRmap_0726():
    fname='/home/clement/Postdoc/Data/202407 CrSBr/scans/RFscan_20240726_001.mat'
    scanESR=mat.NVAFM_RFscan_matFile(fname)
    a=scanESR.ESRMap(refit=False)
    a=a[:135,:]
    a=(a-a[0,0])*1000/28
    xAxis=scanESR.xrange
    yAxis=scanESR.yrange
    plot_map(a, vAxis=xAxis, hAxis=yAxis, vmin=-0.3, vmax=0.3, color='bwr' ,colorBarLabel='B (mT)' , invertH=True,invertV=True)