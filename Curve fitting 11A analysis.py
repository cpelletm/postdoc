import qcodes as qc
from qcodes.dataset.data_export import get_data_by_id,reshape_2D_data
from scipy.optimize import curve_fit,root_scalar,minimize

import numpy as np
import matplotlib.pyplot as plt

class qcLine() :
	def __init__(self,id=0,paramName=None) -> None:
		self.id=id
		self.ds=qc.dataset.load_by_id(id)
		self.sampleName=self.ds.sample_name
		self.experimentName=self.ds.exp_name
		if paramName==None :
			self.xName,self.yName=self.ds.parameters.split(',')[:2]
		else :
			self.xName=self.ds.parameters.split(',')[0]
			self.yName=paramName
		dataDic=self.ds.get_parameter_data()[self.yName]
		self.x=dataDic[self.xName]
		self.y=dataDic[self.yName]
		self.lineTitle=self.yName+' of '+self.sampleName+' in '+self.experimentName+ ' (id='+str(self.id)+')'

	def plot(self,ax=None,figsize=(10,10),show=True,**kwargs) :
		if ax==None :
			fig,ax=plt.subplots(figsize=figsize)
		ax.plot(self.x,self.y,**kwargs)
		ax.set_xlabel(self.xName)
		ax.set_ylabel(self.yName)
		ax.set_title(self.lineTitle)
		if show :
			plt.show()
		return(ax)

def lor_fit_with_gradient(x,y,amp=None,x0=None,sigma=None,ss=None,slope=None,err=False) :
	#sigma=HWHM
	if not ss :
		ss=y[0]
	if not amp :
		if max(y)-ss > ss-min(y) :
			amp=max(y)-ss
		else :
			amp=min(y)-ss
	if not x0 :
		if amp > 0 :
			x0=x[list(y).index(max(y))]
		else :
			x0=x[list(y).index(min(y))]
	if not sigma :
		sigma=x[int(len(x)/5)]-x[0]
	if not slope :
		slope=(y[-1]-y[0])/(x[-1]-x[0])
	def f(x,amp,x0,sigma,ss,slope) :
		return ss+amp*1/(1+((x-x0)/(sigma))**2)+slope*(x-x[0])
	p0=[amp,x0,sigma,ss,slope]
	popt, pcov = curve_fit(f, x, y, p0)
	if err :
		return(popt,f(x,*popt),np.sqrt(np.diag(pcov)))
	else :
		return(popt,f(x,*popt))

def find_ODMR(ODMR:qcLine):
    ODMR.x=ODMR.x*1e-6
    x,y=ODMR.x,ODMR.y
    nPhotons=max(y)*0.4 # 40 reps with 10 ms per point
    data=-y

    from scipy.ndimage import maximum_filter

    filter_win_size = int(15/(x[1]-x[0]))

    max_data = maximum_filter(data, filter_win_size)
    min_data = -maximum_filter(-data, filter_win_size)

    average_delta=sum(max_data-min_data)/len(max_data)
    peak_intensity_threshold = 1.3*average_delta
    # peak_intensity_threshold = 5*np.sqrt(nPhotons)/0.4

    # select places where we detect maximum but not minimum -> we dont want long plateaus
    peak_mask = np.logical_and(max_data == data, min_data != data)
    # select peaks where we have enough elevation
    peak_mask = np.logical_and(peak_mask, max_data - min_data > peak_intensity_threshold)
    # a trick to convert True to 1, False to -1
    peak_mask = peak_mask * 2 - 1
    # select only the up edges to eliminate multiple maximas in a single peak
    peak_mask = np.correlate(peak_mask, [-1, 1], mode='same') == 2

    max_places = np.where(peak_mask)[0]


    # plt.plot(x,y,'-')

    widths=[]
    contrasts=[]
    for place in max_places:
        try :
            fit_win_size=3*filter_win_size//4
            xfit=x[place-fit_win_size:place+fit_win_size]
            datafit=y[place-fit_win_size:place+fit_win_size]
            popt,yfit=lor_fit_with_gradient(xfit,datafit,sigma=6)
            width=popt[2]
            contrast=popt[0]/max(y)
            widths.append(width)
            contrasts.append(contrast)
            # plt.plot(xfit,yfit,'-',color='red',label='width=%.2f MHz, contrast=%.2f'%(width,contrast))
        except:
            pass

    # plt.legend()
    # plt.savefig('/home/clement/Postdoc/Data/202307 11A Charac/ODMR with pillar after O2 fitted/'+ODMR.sampleName+' id=%i'%ODMR.id+'.png')
    # plt.close()
    return widths,contrasts