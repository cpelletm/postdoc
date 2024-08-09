import sys
sys.path.append(r'D:\Clement python dev\postdoc')
from analyse import *
import Mat_data_processing as mat
import addcopyfighandler

def scan_08_07():
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240807_001.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['Norm forward']
    # a=a.T
    plot_map(a, vAxis=[scan.xmin,scan.xmax], hAxis=[scan.ymin, scan.ymax], invertH=True,invertV=True, correctGradient=False, color='RdBu', colorBarLabel='Norm (a.u.)')

# scan_08_07()

def Vz_08_07():
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240807_001.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['Vz forward']
    a=a[:110,:]
    a=a*2/7*1000
    a=a-a[0,0]
    # a=a.T
    plot_map(a, vAxis=[scan.xmin,scan.xmax], hAxis=[scan.ymin, scan.ymax], invertH=True,invertV=True, correctGradient=True, color='viridis', colorBarLabel='Vz (nm)')

# Vz_08_07()

def ESRmap_0805():
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\RF_imaging_temp\RFscan_20240805_002.mat'
    scanESR=mat.NVAFM_RFscan_matFile(fname)
    a=scanESR.ESRMap(refit=False)
    a=a[:,:]
    a=(a-a[0,0])*1000/28
    xAxis=scanESR.xrange
    yAxis=scanESR.yrange
    plot_map(a, vAxis=xAxis, hAxis=yAxis, vmin=-1, vmax=1, color='bwr' ,colorBarLabel='B (mT)' , invertH=True,invertV=True)

# ESRmap_00805()

def ESRmap_0808():
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\RF_imaging_temp\RFscan_20240808_002.mat'
    scanESR=mat.NVAFM_RFscan_matFile(fname)
    a=scanESR.ESRMap(refit=False)
    a=a[:,:]
    a=(a-a[0,0])*1000/28
    xAxis=scanESR.xrange
    yAxis=scanESR.yrange
    plot_map(a, vAxis=xAxis, hAxis=yAxis, color='bwr' ,colorBarLabel='B (mT)' , invertH=True,invertV=True, centerColorBar=0)

# ESRmap_0808()

def ESRmap_0809():
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\RF_imaging_temp\RFscan_20240809_001.mat'
    scanESR=mat.NVAFM_RFscan_matFile(fname)
    a=scanESR.ESRMap(refit=False)
    a=a[:,:]
    a=(a-a[0,0])*1000/28
    xAxis=scanESR.xrange
    yAxis=scanESR.yrange
    plot_map(a, vAxis=xAxis, hAxis=yAxis, color='bwr' ,colorBarLabel='B (mT)' , invertH=True,invertV=True, centerColorBar=0)

ESRmap_0809()

def ESRmap_0726():
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\RF_imaging_temp\RFscan_20240726_001.mat'
    scanESR=mat.NVAFM_RFscan_matFile(fname)
    a=scanESR.ESRMap(refit=False)
    a=a[:135,:]
    a=(a-a[0,0])*1000/28
    xAxis=scanESR.xrange
    yAxis=scanESR.yrange
    plot_map(a, vAxis=xAxis, hAxis=yAxis, vmin=-1, vmax=1, color='bwr' ,colorBarLabel='B (mT)' , invertH=True,invertV=True)

# ESRmap_0726()

def conversionDualIsoBToMHz(contrast,width,normValue,split=12):
    #contrast is in percent, width and split in MHz
    contrast=contrast/100
    x=np.linspace(-split/2,split/2,201)
    lor1=1-contrast*1/(1+((x-split/2)/width)**2)
    lor2=1-contrast*1/(1+((x+split/2)/width)**2)
    return np.interp(x=normValue,xp=lor2/lor1,fp=x)

def scan_0806_05_isoBToMHz():
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240806_005.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['Norm forward']
    for i in range(a.shape[0]):
        if np.isnan(a[i,:]).any():
            break
    a=a[:i,:]
    a=a-np.mean(a-1)
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            a[i,j]=conversionDualIsoBToMHz(contrast=3.5,width=6.2,normValue=a[i,j])
    plot_map(a, vAxis=[scan.xmin,scan.xmax], hAxis=[scan.ymin, scan.ymax], invertH=True,invertV=True, correctGradient=False, color='RdBu', colorBarLabel=r'$\Delta \nu$ (MHz)')

# scan_0806_05_isoBToMHz()

def linescan_avg_0806_05(show=True):
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240806_005.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['Norm forward']
    for i in range(a.shape[0]):
        if np.isnan(a[i,:]).any():
            break
    a=a[:i,:]
    a=a-np.mean(a-1)
    line=a[0,:]
    line=conversionDualIsoBToMHz(contrast=3.5,width=6.2,normValue=line)
    for i in range(1,a.shape[0]):
        line+=conversionDualIsoBToMHz(contrast=3.5,width=6.2,normValue=a[i,:])
    line=line/a.shape[0]
    xAxis=np.linspace(scan.ymin,scan.ymax,len(line))
    xAxis=(xAxis-min(xAxis))*2000
    if show:
        plt.plot(xAxis,line)
        plt.xlabel('Y (nm)')
        plt.ylabel('Frequency (MHz)')
        plt.show()
    return xAxis,line

# linescan_avg_0806_05()

def scan_0806_06_isoBToMHz():
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240806_006.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['Norm forward']
    for i in range(a.shape[0]):
        if np.isnan(a[i,:]).any():
            break
    a=a[:i,:]
    a=a-np.mean(a-1)
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            a[i,j]=conversionDualIsoBToMHz(contrast=2.5,width=7.9,normValue=a[i,j])
    plot_map(a, vAxis=[scan.xmin,scan.xmax], hAxis=[scan.ymin, scan.ymax], invertH=True,invertV=True, correctGradient=False, color='RdBu', colorBarLabel=r'$\Delta \nu$ (MHz)')

# scan_0806_06_isoBToMHz()

def linescan_avg_0806_06(show=True):
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240806_006.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['Norm forward']
    for i in range(a.shape[0]):
        if np.isnan(a[i,:]).any():
            break
    a=a[:i,:]
    a=a-np.mean(a-1)
    line=a[0,:]
    line=conversionDualIsoBToMHz(contrast=2.5,width=7.9,normValue=line)
    for i in range(1,a.shape[0]):
        line+=conversionDualIsoBToMHz(contrast=2.5,width=7.9,normValue=a[i,:])
    line=line/a.shape[0]
    xAxis=np.linspace(scan.ymin,scan.ymax,len(line))
    xAxis=(xAxis-min(xAxis))*2000
    if show:
        plt.plot(xAxis,line)
        plt.xlabel('Y (nm)')
        plt.ylabel('Frequency (MHz)')
        plt.show()
    return xAxis,line

# linescan_avg_0806_06()

def scan_0806_07_isoBToMHz():
    #Just to see if this is consistent with the feedback scan done later
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240806_007.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['Norm forward']
    for i in range(a.shape[0]):
        if np.isnan(a[i,:]).any():
            break
    a=a[:i,:]
    a=a-np.mean(a-1)
    for i in range(a.shape[0]):
        for j in range(a.shape[1]):
            a[i,j]=conversionDualIsoBToMHz(contrast=5.4,width=7.9,normValue=a[i,j])
    plot_map(a, vAxis=[scan.xmin,scan.xmax], hAxis=[scan.ymin, scan.ymax], invertH=True,invertV=True, correctGradient=False, color='RdBu', colorBarLabel=r'$\Delta \nu$ (MHz)')

# scan_0806_07_isoBToMHz()

def scan_0806_08():
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240806_008.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['RFFreq forward']
    for i in range(a.shape[0]):
        if np.isnan(a[i,:]).any():
            break
    a=a[:i,:]
    a=a-a[0,0]
    a*=1000
    plot_map(a, vAxis=[scan.xmin,scan.xmax], hAxis=[scan.ymin, scan.ymax], invertH=True,invertV=True, correctGradient=False, color='RdBu', colorBarLabel=r'$\Delta \nu$ (MHz)')

# scan_0806_08()

def linescan_avg_0806_08(show=True):
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240806_008.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['RFFreq forward']
    for i in range(a.shape[0]):
        if np.isnan(a[i,:]).any():
            break
    a=a[:i,:]
    a=a-a[0,0]
    a*=1000
    line=a[0,:]
    for i in range(1,a.shape[0]):
        line+=a[i,:]
    line=line/a.shape[0]
    xAxis=np.linspace(scan.ymin,scan.ymax,len(line))
    xAxis=(xAxis-min(xAxis))*2000
    if show:
        plt.plot(xAxis,line)
        plt.xlabel('Y (nm)')
        plt.ylabel('Frequency (MHz)')
        plt.show()
    return xAxis,line

# linescan_avg_0806_08()

def linescan_0806_08_firstLine(show=True):
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240806_008.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['RFFreq forward']
    a=a-a[0,0]
    a*=1000
    line=a[0,:]
    xAxis=np.linspace(scan.ymin,scan.ymax,len(line))
    xAxis=(xAxis-min(xAxis))*2000
    if show:
        plt.plot(xAxis,line)
        plt.xlabel('Y (nm)')
        plt.ylabel('Frequency (MHz)')
        plt.show()
    return xAxis,line

# linescan_0806_08_firstLine()

def linescan_0806_10(show=True):
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240806_010.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['RFFreq forward']
    a=a-a[0,0]
    a*=1000
    line=a[0,:]
    xAxis=np.linspace(scan.ymin,scan.ymax,len(line))
    xAxis=(xAxis-min(xAxis))*2000
    if show:
        plt.plot(xAxis,line)
        plt.xlabel('Y (nm)')
        plt.ylabel('Frequency (MHz)')
        plt.show()
    return xAxis,line

# linescan_0806_10()

def linescan_0806_11(show=True):
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240806_011.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['RFFreq forward']
    a=a-a[0,0]
    a*=1000
    line=a[0,:]
    xAxis=np.linspace(scan.ymin,scan.ymax,len(line))
    xAxis=(xAxis-min(xAxis))*2000
    if show:
        plt.plot(xAxis,line)
        plt.xlabel('Y (nm)')
        plt.ylabel('Frequency (MHz)')
        plt.show()
    return xAxis,line

# linescan_0806_11()

def linescan_0806_12(show=True):
    fname=r'K:\Experiments\Experiment_203_LT\NVAFM_203_LT\appdesigner_data\Imaging\2024\scan_20240806_012.mat'
    scan=mat.NVAFM_scan_matFile(fname)
    scan.findRange()
    a=scan.dataDic['RFFreq forward']
    a=a-a[0,0]
    a*=1000
    line=a[0,:]
    xAxis=np.linspace(scan.ymin,scan.ymax,len(line))
    xAxis=(xAxis-min(xAxis))*2000
    if show:
        plt.plot(xAxis,line)
        plt.xlabel('Y (nm)')
        plt.ylabel('Frequency (MHz)')
        plt.show()
    return xAxis,line

# linescan_0806_12()

def plotAllLines():
    xAxis,line=linescan_avg_0806_05(show=False)
    plt.plot(xAxis,line,label='100 G')
    xAxis,line=linescan_avg_0806_06(show=False)
    plt.plot(xAxis,line+10,label='700 G')
    xAxis,line=linescan_0806_08_firstLine(show=False)
    plt.plot(xAxis,line+20,label='1300 G')
    xAxis,line=linescan_0806_10(show=False)
    plt.plot(xAxis,line+30,label='1500 G')
    xAxis,line=linescan_0806_11(show=False)
    plt.plot(xAxis,line+40,label='1700 G')
    xAxis,line=linescan_0806_12(show=False)
    plt.plot(xAxis,line+50,label='1900 G')
    plt.xlabel('Y (nm)')
    plt.ylabel('Frequency (MHz)')
    plt.legend()
    plt.show()

# plotAllLines()