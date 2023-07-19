import sys
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import Mat_data_processing as mat
from scipy.optimize import curve_fit,root_scalar,minimize
from scipy.signal import find_peaks
from scipy import fftpack, io
from PyQt5.QtWidgets import QApplication,QFileDialog
from numpy import sqrt,pi,cos,sin,exp,log
from numpy.linalg import norm



def extract_data(filename,xcol=0,ycol=1,exclude_neg=False,data='line',delimiter='auto',decimalPoint='.',matFile='ESR'):
	import csv
	if len(filename)<=4 or filename[-4]!='.' :
		if glob.glob(filename+'.txt') :
			f=glob.glob(filename+'.txt')[0]
		elif glob.glob(filename+'.csv') :
			f=glob.glob(filename+'.csv')[0]
		elif glob.glob(filename+'.asc') :
			f=glob.glob(filename+'.asc')[0]
		elif glob.glob(filename+'.mat') :
			f=glob.glob(filename+'.mat')[0]
		else :
			print('file not found')
			quit()
		filename=f
	if filename[-4:] =='.txt' : #Assumes that data is in column
		x=[]
		y=[]
		with open(filename,'r',encoding = "ISO-8859-1") as f:
			for line in f :
				line=line.split()
				if decimalPoint!='.' :
					line2=[]
					for elem in line :
						elem=elem.replace(decimalPoint,'.')
						line2+=[elem]
					line=line2
				try :
					if exclude_neg : #c'est extrèmement gitan ça monsieur
						if float(line[xcol])!=-1 :
							x+=[float(line[xcol])]
							y+=[float(line[ycol])]
					else :
						x+=[float(line[xcol])]
						y+=[float(line[ycol])]				
				except :
					pass
		return(np.array(x),np.array(y))
	elif filename[-4:] =='.asc' :
		x=[]
		y=[]
		def convert_comma_number(x):
			x=x.split(',')
			if len(x)==2 :
				y=float(x[0])+float(x[1])*10**(-len(x[1]))
			elif len(x)==1 :
				y=float(x[0])
			return y
		with open(filename,'r',encoding = "ISO-8859-1") as f:
			for line in f:
				line=line.split()
				try :
					x+=[convert_comma_number(line[0])]
					y+=[convert_comma_number(line[1])]
				except :
					pass
		return(np.array(x),np.array(y))
	elif filename[-4:] =='.csv' and data=='line':
		if delimiter=='auto' :
			delimiter=' '
		with open(filename,'r',encoding = "ISO-8859-1") as f:
			content=f.readlines()
			x=content[xcol]
			x=x.split()
			xdata=[]
			for item in x :
				try :
					xdata+=[float(item)]
				except :
					pass
			y=content[ycol]
			y=y.split()
			y=[float(item) for item in y]
			ydata=[]
			for item in y :
				try :
					ydata+=[float(item)]
				except :
					pass
		return(np.array(xdata),np.array(ydata))
	elif filename[-4:] =='.csv' and (data=='column' or data=='col'):
		if delimiter=='auto' :
			delimiter=','
		with open(filename,'r',encoding = "ISO-8859-1") as f:
			reader = csv.reader(f, delimiter=delimiter, quotechar='|')
			xdata=[]
			ydata=[]
			for line in reader:
				try :
					xdata+=[float(line[xcol])]
					ydata+=[float(line[ycol])]
				except :
					continue #pass marcherait aussi mais je me la pète
		return(np.array(xdata),np.array(ydata))
	elif filename[-4:] =='.mat' :
		#fname='/home/clement/Postdoc/Data/202303 11D and 11B charac/ODMR files/esr2_20230316_003'
		matDic=io.loadmat(filename)
		if matFile=='ESR':
			keys=['__header__', '__version__', '__globals__', 'smNVesr', '__function_workspace__']

			freqs=matDic[keys[3]][0,0][1][0,xcol//2][3][0]
			PL=matDic[keys[3]][0,0][1][0,ycol//2][4][0]
			x=freqs
			y=PL
			return(x,y)
		elif matFile=='PLTrace':
			keys=list(matDic.keys())
			PL=matDic[keys[3]][0]
			facq=matDic[keys[4]][0,0]
			n=len(PL)
			t=np.linspace(0,n/facq,n)
			return(t,PL)
		


#~~~~ Fits ~~~~
def lin_fit(x=[],y=[]) :
	x=np.array(x)
	y=np.array(y)
	if len(x)!=len(y) :
		print("no x given or wrong size (len(x)=%i and len(y)=%i)"%(len(x),len(y)))
		x=np.arange(len(y))

	A=np.vstack([x,np.ones(len(x))]).T
	a,b = np.linalg.lstsq(A, y, rcond=None)[0]
	return([a,b],a*x+b)

def quad_fit(x,y) :
	A=np.vstack([x**2,x,np.ones(len(x))]).T
	a,b,c = np.linalg.lstsq(A, y, rcond=None)[0]
	return([a,b,c],a*x**2+b*x+c)

def parabola_fit(x,y):
	if y[0]-min(y) > max(y)-y[0] :
		typ='upside'
	else :
		typ='downside'

	if typ=='upside' :
		x0=x[list(y).index(min(y))]
		y0=min(y)
		a=(y[0]-min(y))/(x[0]-x0)**2
	else :
		x0=x[list(y).index(max(y))]
		y0=max(y)
		a=(y[0]-max(y))/(x[0]-x0)**2

	def f(x,a,x0,y0):
		return a*(x-x0)**2+y0

	p0=[a,x0,y0]
	popt, pcov = curve_fit(f, x, y, p0)
	return(popt,f(x,*popt))

def fit_ordre_4(x,y) :
	x,y=np.array(x),np.array(y)
	A=np.vstack([x**4,x**3,x**2,x,np.ones(len(x))]).T
	a,b,c,d,e = np.linalg.lstsq(A, y, rcond=None)[0]
	return([a,b,c,d,e],a*x**4+b*x**3+c*x**2+d*x+e)

def fit_ordre_6(x,y) :
	A=np.vstack([x**6,x**5,x**4,x**3,x**2,x,np.ones(len(x))]).T
	w,z,a,b,c,d,e = np.linalg.lstsq(A, y, rcond=None)[0]
	return([w,z,a,b,c,d,e],w*x**6+z*x**5+a*x**4+b*x**3+c*x**2+d*x+e)

def gauss_fit(x,y,amp=None,x0=None,sigma=None,ss=0,err=False) :
	#HWHM = sigma*sqrt(2*np.log(2)) pour une gaussienne
	if not ss :
		ss=y[0]
	if not amp :
		if max(y)-ss > ss-min(y) :
			amp=max(y)-ss
		else :
			amp=min(y)-ss
	if not x0 :
		x0=x[int(len(x)/2)]
	if not sigma :
		sigma=x[int(len(x)/5)]-x[0]
	def f(x,amp,x0,sigma,ss) : #HWHM=1.18*sigma (sqrt(2*ln(2)))
		return amp*np.exp(-(x-x0)**2/(2*sigma**2))+ss
	p0=[amp,x0,sigma,ss]
	popt, pcov = curve_fit(f, x, y, p0)
	if err :
		return(popt,f(x,*popt),np.sqrt(np.diag(pcov)))
	else :
		return(popt,f(x,*popt))

def gauss_derivative_fit(x,y,amp=None,x0=None,sigma=None,ss=0):
	#Je gère pas le cas ou x n'est pas dans l'ordre croissant
	if not ss :
		ss=y[0]
	if not amp :
		abs_amp=max(max(y)-ss,ss-min(y))
		m=find_elem(min(y),y)
		M=find_elem(max(y),y)
		if m<M :
			amp=abs_amp
		if m>M :
			amp=-abs_amp
	if not x0 :
		x0=x[int(len(x)/2)]
	if not sigma :
		sigma=x[int(len(x)/5)]-x[0]
	def f(x,amp,x0,sigma,ss) : #HWHM=1.18*sigma (sqrt(2*ln(2)))
		return amp*(x-x0)/sigma*np.exp(-(x-x0)**2/(2*sigma**2))+ss
	p0=[amp,x0,sigma,ss]
	popt, pcov = curve_fit(f, x, y, p0)
	return(popt,f(x,*popt))

def lor_fit(x,y,amp=None,x0=None,sigma=None,ss=None,err=False) :
	#sigma=HWHM
	if not ss :
		ss=y[0]
	if not amp :
		if max(y)-ss > ss-min(y) :
			amp=max(y)-ss
		else :
			amp=min(y)-ss
	if not x0 :
		x0=x[int(len(x)/2)]
	if not sigma :
		sigma=x[int(len(x)/5)]-x[0]
	def f(x,amp,x0,sigma,ss) :
		return ss+amp*1/(1+((x-x0)/(sigma))**2)
	p0=[amp,x0,sigma,ss]
	popt, pcov = curve_fit(f, x, y, p0)
	if err :
		return(popt,f(x,*popt),np.sqrt(np.diag(pcov)))
	else :
		return(popt,f(x,*popt))

def lor_fit_fixed(x,y,amp=None,x0=0,sigma=1,ss=None):
	#x0 and sigma fixed
	if not ss :
		ss=y[-1]
	if not amp :
		if max(y)-ss > ss-min(y) :
			amp=max(y)-ss
		else :
			amp=min(y)-ss
	def f(x,amp,ss) :
		return ss+amp*1/(1+((x-x0)/(sigma))**2)
	p0=[amp,ss]
	popt, pcov = curve_fit(f, x, y, p0)
	return(popt,f(x,*popt))

def cos_fit(x,y,amp=None,omega=None,phi=0,ss=None):
	if not amp :
		amp=max(y)-min(y)
	if not omega :
		omega=2*np.pi/(max(x)-min(x))
	if not ss :
		ss=y[-1]
	def f(x,amp,omega,phi,ss):
		return amp*np.cos(omega*x+phi)+ss
	p0=[amp,omega,phi,ss]
	popt, pcov = curve_fit(f, x, y, p0)
	return(popt,f(x,*popt))

def invert_fit(x,y,amp=None):
	if not amp:
		n=closest_elem(x,1)
		amp=y[n]
	def f(x,amp):
		return amp/x
	p0=[amp]
	popt, pcov = curve_fit(f, x, y, p0)
	return(popt,f(x,*popt))

def exp_fit(x,y,amp=None,ss=None,tau=None,err=False) :
	if not amp :
		amp=max(y)-min(y)
	if not ss :
		ss=y[-1]
	if not tau :
		tau=x[int(len(x)/10)]-x[0]
	def f(x,amp,ss,tau) :
		return amp*np.exp(-x/tau)+ss
	p0=[amp,ss,tau]
	popt, pcov = curve_fit(f, x, y, p0)
	if err :
		return(popt,f(x,*popt),np.sqrt(np.diag(pcov)))
	else :
		return(popt,f(x,*popt))

def exp_fit_zero(x,y,amp=None,tau=None,norm=False,err=False) :
	if not amp :
		amp=max(y)-min(y)
	if not tau :
		tau=x[int(len(x)/10)]-x[0]
	if norm :
		amp=1
		def f(x,tau):
			return amp*np.exp(-x/tau)
		p0=[tau]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([0],[np.inf]))
	else :
		def f(x,amp,tau) :
			return amp*np.exp(-x/tau)
		p0=[amp,tau]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,0],[np.inf,np.inf]))
	if err :
		return(popt,f(x,*popt),np.sqrt(np.diag(pcov)))
	else :
		return(popt,f(x,*popt))

def stretch_exp_fit(x,y,amp=None,ss=None,tau=None,err=False) :
	if not amp :
		amp=max(y)-min(y)
	if not ss :
		ss=y[-1]
	if not tau :
		tau=x[int(len(x)/10)]-x[0]
	def f(x,amp,ss,tau) :
		return amp*np.exp(-np.sqrt(x/tau))+ss
	p0=[amp,ss,tau]
	popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,-np.inf,0],[np.inf,np.inf,np.inf]))
	if err :
		return(popt,f(x,*popt),np.sqrt(np.diag(pcov)))
	else :
		return(popt,f(x,*popt))

def stretch_exp_fit_zero(x,y,amp=None,tau=None,norm=False,err=False) :
	if not amp :
		amp=max(y)-min(y)
	if not tau :
		tau=x[int(len(x)/10)]-x[0]
	if norm :
		amp=1
		def f(x,tau):
			return amp*np.exp(-np.sqrt(x/tau))
		p0=[tau]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([0],[np.inf]))
	else :
		def f(x,amp,tau) :
			return amp*np.exp(-np.sqrt(x/tau))
		p0=[amp,tau]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,0],[np.inf,np.inf]))
	if err :
		return(popt,f(x,*popt),np.sqrt(np.diag(pcov)))
	else :
		return(popt,f(x,*popt))

def stretch_arb_exp_fit(x,y,amp=None,ss=None,tau=None,alpha=0.5,fixed=False,err=False):
	if not amp :
		amp=max(y)-min(y)
	if not ss :
		ss=y[-1]
	if not tau :
		tau=x[int(len(x)/10)]-x[0]
	if fixed :
		def f(x,amp,ss,tau) :
			return amp*np.exp(-(x/tau)**alpha)+ss
		p0=[amp,ss,tau]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,-np.inf,0],[np.inf,np.inf,np.inf]))
	else :
		def f(x,amp,ss,tau,alpha) :
			return amp*np.exp(-(x/tau)**alpha)+ss
		p0=[amp,ss,tau,alpha]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,-np.inf,0,0],[np.inf,np.inf,np.inf,np.inf]))
	if err :
		return(popt,f(x,*popt),np.sqrt(np.diag(pcov)))
	else :
		return(popt,f(x,*popt))

def stretch_arb_exp_fit_zero(x,y,amp=None,tau=None,alpha=0.5,fixed=False,err=False):
	if not amp :
		amp=max(y)-min(y)
	if not tau :
		tau=x[int(len(x)/10)]-x[0]
	if fixed :
		def f(x,amp,tau) :
			return amp*np.exp(-(x/tau)**alpha)
		p0=[amp,tau]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,0],[np.inf,np.inf]))
	else :
		def f(x,amp,tau,alpha) :
			return amp*np.exp(-(x/tau)**alpha)
		p0=[amp,tau,alpha]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,0,0],[np.inf,np.inf,np.inf]))
	if err :
		return(popt,f(x,*popt),np.sqrt(np.diag(pcov)))
	else :
		return(popt,f(x,*popt))

def stretch_with_baseline(x,y,tau_BL=5e-3,alpha_BL=1,alpha_dip=0.5,amp=None,tau=None):
	if not amp :
		amp=max(y)-min(y)
	if not tau :
		tau=x[int(len(x)/10)]-x[0]
	def f(x,amp,tau) :
		return amp*np.exp(-(x/tau_BL)**alpha_BL)*np.exp(-(x/tau)**alpha_dip)
	p0=[amp,tau]
	popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,0],[np.inf,np.inf]))
	return(popt,f(x,*popt))

def third_stretch(x,y,amp=None,tau=None) :
	if not amp :
		amp=max(y)-min(y)
	if not tau :
		tau=x[int(len(x)/10)]-x[0]
	def f(x,amp,tau) :
		return amp*np.exp(-(x/tau)^(1/3))
	p0=[amp,tau]
	popt, pcov = curve_fit(f, x, y, p0)
	return(popt,f(x,popt[0],popt[1]))

def stretch_et_phonons(x,y,amp=None,tau=None,T1ph=5E-3,fixed=True,err=False) :
	if not amp :
		amp=max(y)-min(y)
	if not tau :
		tau=x[int(len(x)/10)]-x[0]
	if fixed :
		def f(x,amp,tau) :
			return amp*np.exp(-x/T1ph-sqrt(x/tau))
		p0=[amp,tau]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,0],[np.inf,np.inf]))
	else :
		def f(x,amp,tau,T1ph) :
			return amp*np.exp(-x/T1ph-sqrt(x/tau))
		p0=[amp,tau,T1ph]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,0,0],[np.inf,np.inf,np.inf]))
	if err :
		return(popt,f(x,*popt),np.sqrt(np.diag(pcov)))
	else :
		return(popt,f(x,*popt))

def stretch_et_phonons_non_zero(x,y,amp=None,ss=None,tau=None,T1ph=5E-3,fixed=True) :
	if not amp :
		amp=max(y)-min(y)
	if not tau :
		tau=x[int(len(x)/10)]-x[0]
	if not ss :
		ss=y[-1]
	if fixed :
		def f(x,amp,ss,tau) :
			return amp*np.exp(-x/T1ph-sqrt(x/tau))+ss
		p0=[amp,ss,tau]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,-np.inf,0],[np.inf,np.inf,np.inf]))
	else :
		def f(x,amp,ss,tau,T1ph) :
			return amp*np.exp(-x/T1ph-sqrt(x/tau))+ss
		p0=[amp,ss,tau,T1ph]
		popt, pcov = curve_fit(f, x, y, p0,bounds=([-np.inf,-np.inf,0,0],[np.inf,np.inf,np.inf,np.inf]))
	return(popt,f(x,*popt))

def Rabi_fit(x,y,amp=None,omega=None,tau=None,ss=None,phi=0,typ='lor'):
	if not amp :
		amp=max(y)-min(y)
	if not ss :
		ss=y[-1]
	if not tau :
		tau=x[int(len(x)/3)]-x[0]
	if not omega :
		omega=1/(x[int(len(x)/10)]-x[0])
	if typ=='lor' :
		def f(x,amp,ss,tau,omega) :
			return amp*np.exp(-x/tau)*np.cos(omega*x+phi)+ss
	elif typ=='gauss' :
		def f(x,amp,ss,tau,omega) :
			return amp*np.exp(-(x/tau)**2)*np.cos(omega*x+phi)+ss
	p0=[amp,ss,tau,omega]
	popt, pcov = curve_fit(f, x, y, p0)
	return(popt,f(x,*popt))

def fit_B_dipole(x,y,B0=2000,x0=10) : #x : distance en mm, y : champ mag en G
	def f(x,B0,x0):
		return(B0/(x+x0)**3)
	p0=[B0,x0]
	popt, pcov = curve_fit(f, x, y, p0)
	return(popt,f(x,popt[0],popt[1]))

def ESR_n_pics(x,y,cs='auto',width=False,ss=None,amp=None,typ='gauss') : #typ="gauss" ou "lor"
	if cs=='auto':
		cs=find_ESR_peaks(x,y)
	if not ss :
		ss=y[0]
	if not amp :
		if max(y)-ss > ss-min(y) :
			amp=max(y)-ss
		else :
			amp=min(y)-ss
	if not width :
		if max(x) < 50 : #Je sq c'est des GHz
			width=8e-3
		elif max(x) < 5E4 : #Je sq c'es des Mhz
			width=8
		else : #Je sq c'es des Hz
			width=8E6
	n=len(cs)
	widths=np.ones(n)*width
	amps=np.ones(n)*amp
	p0=[ss]
	for c in cs:
		p0+=[c]
	for w in widths:
		p0+=[w]
	for a in amps:
		p0+=[a]
	def f(x,*params):
		ss=params[0]
		n=(len(params)-1)//3
		y=ss
		for i in range(n):
			c=params[1+i]
			width=params[1+n+i]
			amp=params[1+2*n+i]
			if typ=="gauss" :
				y+=amp*np.exp(-((x-c)/width)**2)
			elif typ=="lor" :
				y+=amp*1/(1+((x-c)/width)**2)
		return(y)
	popt, pcov = curve_fit(f, x, y, p0)
	ss=popt[0]
	centers=popt[1:n+1]
	widths=abs(popt[n+1:2*n+1])
	amps=popt[2*n+1:]
	params=[ss,centers,widths,amps]
	return(params,f(x,*popt))

def ESR_fixed_amp_and_width(x,y,cs,amp=False,width=False,ss=False,typ='gauss'):
	if not ss :
		ss=y[0]
	if not amp :
		if max(y)-ss > ss-min(y) :
			amp=max(y)-ss
		else :
			amp=min(y)-ss
	if not width :
		if max(x) < 50 : #Je sq c'est des GHz
			width=1e-3
		elif max(x) < 5E4 : #Je sq c'es des Mhz
			width=1
		else : #Je sq c'es des Hz
			width=1E6
	p0=[ss,amp,width,*cs]
	def f(x,*params):
		ss=params[0]
		amp=params[1]
		width=params[2]
		cs=params[3:]
		y=ss
		for c in cs :
			if typ=="gauss" :
				y+=amp*np.exp(-((x-c)/width)**2)
			elif typ=="lor" :
				y+=amp*1/(1+((x-c)/width)**2)
		return(y)
	popt, pcov = curve_fit(f, x, y, p0)
	ss=popt[0]
	centers=popt[3:]
	width=abs(popt[2])
	amp=popt[1]
	params=[ss,centers,width,amp]
	return(params,f(x,*popt))

def find_ESR_peaks(x,y,width=False,threshold=0.2,returnUnit='x',precise=False):
	'''
	width in unit of x  
	thrsehold = min peak height in proportion of max peak height 
	returnUnit='x' : return the x position of the peaks ; ='n' return the index of the peaks
	'''
	if not width :
		distance=int(6/(x[1]-x[0])) #assumes that x is in MHz, and takes an ESR width of 6 MHz
	else :
		distance=int(width/(x[1]-x[0]))

	y=y-min(y)
	y=y/max(y)
	if y[0]-min(y) > max(y)-y[0] : #Setup "ESR PL" (pics à l'envers)
		y=1-y
	height=threshold

	ns=find_peaks(y,height=height,distance=distance)[0]
	cs=[x[i] for i in ns]

	if precise :
		popt,yfit=ESR_n_pics(x,y,cs,width=width)
		cs=popt[1]
		if returnUnit=='n' :
			for k in range(len(cs)):
				i=0
				while x[i]<cs[k] :
					i+=1
				ns[k]=i

	if returnUnit=='x' :
		return(np.array(cs))
	if returnUnit=='n' :
		return(ns)

#~~~~~~ NV Physics ~~~~~~

def find_B_111(freq,transi='-') : #freq en MHz
	D=2870
	gamma=2.8
	if transi=='-' :
		return(D-freq)/gamma
	elif transi =='+' :
		return(freq-D)/gamma

def find_B_100(freq,transi='-',B_max=100,E=4,D=2870) :
	Sz=np.array([[1,0,0],[0,0,0],[0,0,-1]])
	Sx=1/np.sqrt(2)*np.array([[0,1,0],[1,0,1],[0,1,0]])
	Sy=1/(np.sqrt(2)*1j)*np.array([[0,1,0],[-1,0,1],[0,-1,0]])

	def Hamiltonian_0(B,classe=1) :
		#Unité naturelle : MHz,Gauss
		B=np.array(B)
		gamma=2.8
		if classe==1 :
			C=np.array([1,1,1])/np.sqrt(3)
			Bz=B.dot(C)
			Bx=np.sqrt(abs(B.dot(B)-Bz**2))
		if classe==2 :
			C=np.array([1,-1,-1])/np.sqrt(3)
			Bz=B.dot(C)
			Bx=np.sqrt(abs(B.dot(B)-Bz**2))
		if classe==3 :
			C=np.array([-1,1,-1])/np.sqrt(3)
			Bz=B.dot(C)
			Bx=np.sqrt(abs(B.dot(B)-Bz**2))
		if classe==4 :
			C=np.array([-1,-1,1])/np.sqrt(3)
			Bz=B.dot(C)
			Bx=np.sqrt(abs(B.dot(B)-Bz**2))
		H=D*Sz**2+gamma*(Bx*Sx+Bz*Sz)+E*(Sx.dot(Sx)-Sy.dot(Sy))
		return H

	def egvect(H) :
		val,vec=np.linalg.eigh(H) #H doit être Hermitienne
		vec=vec.T #Les vecteurs propres sortent en LIGNE (vecteur #1 : vec[0])
		return(val,vec)


	def f(amp):
		B=[amp,0,0]
		H=Hamiltonian_0(B,classe=1)
		val,vec=egvect(H)
		if transi=='-' :
			transi_NV=val[1]-val[0]
		if transi=='+' :
			transi_NV=val[2]-val[0]

		return transi_NV-freq


	RR=root_scalar(f,bracket=[0,B_max])
	return RR.root

class NVHamiltonian(): #x,y and z axis are taken as (100) axis
	c1=np.array([-1,1.,-1])/np.sqrt(3)
	c2=np.array([1,1,1])/np.sqrt(3)
	c3=np.array([-1,-1,1])/np.sqrt(3)
	c4=np.array([1,-1,-1])/np.sqrt(3)
	c5=np.array([0,0,1]) #La base propre de Sz 
	c6=np.array([2*sqrt(2)/3,0,-1/3]) #Une des trois autres classes pour B//[111]
	cs=[c1,c2,c3,c4,c5,c6]
	def __init__(self,B,c=1,E=4,D=2870,gamma_e=2.8,order='traditionnal'): #If B is not a magneticField Instance it should be of the form [Bx,By,Bz] ; E en MHz (spltting de 2*E en champs nul)
		#order='traditionnal' or 'ascending' : basis is (-1,0,+1) or (0,-1,+1)
		if order=='traditionnal' :
			self.Sz=np.array([[-1,0,0],[0,0,0],[0,0,1]])
			self.Sy=np.array([[0,1j,0],[-1j,0,1j],[0,-1j,0]])*1/np.sqrt(2)
			self.Sx=np.array([[0,1,0],[1,0,1],[0,1,0]])*1/np.sqrt(2)
			self.Sz2=np.array([[1,0,0],[0,0,0],[0,0,1]]) # Pour éviter une multilplcation matricielle
			self.H_E_transverse=np.array([[0,0,1],[0,0,0],[1,0,0]])
		if order=='ascending' :
			self.Sz=np.array([[0,0,0],[0,-1,0],[0,0,1]])
			self.Sy=np.array([[0,-1j,1j],[1j,0,0],[-1j,0,0]])*1/np.sqrt(2)
			self.Sx=np.array([[0,1,1],[1,0,0],[1,0,0]])*1/np.sqrt(2)
			self.Sz2=np.array([[0,0,0],[0,1,0],[0,0,1]]) # Pour éviter une multilplcation matricielle
			self.H_E_transverse=np.array([[0,0,1],[0,0,0],[1,0,0]])
			# self.H_E_transverse_real=np.array([[0,0,0],[0,0,1],[0,1,0]])
			# self.H_E_transverse_imag=np.array([[0,0,0],[0,0,1],[0,1,0]])
		if not isinstance(B,magneticField):
			B=magneticField(x=B[0],y=B[1],z=B[2])
		if c==5:
			self.Bz=abs(B.z)
			self.Bx=abs(B.x)
			self.By=abs(B.y)
		else :
			self.Bz=abs(self.cs[c-1].dot(B.cartesian)) #Attention, ici Bz est dans la base du NV (Bz')
			#Attention bis : je considère que z' est toujours aligné (dans le meme hémisphère) que B
			self.Bx=np.sqrt(abs(B.amp**2-self.Bz**2))#le abs est la pour éviter les blagues d'arrondis. Je mets tout ce qui n'est pas sur z sur le x
			self.By=0
		self.H=D*self.Sz2+gamma_e*(self.Bz*self.Sz+self.Bx*self.Sx+self.By*self.Sy)+E*self.H_E_transverse #Rajoute des fioritures si tu veux. Un peu que je veux
	def transitions(self):
		egva,egve=np.linalg.eigh(self.H)
		egva=np.sort(egva)
		return [egva[1]-egva[0],egva[2]-egva[0]]
	def egval(self):
		egva,egve=np.linalg.eigh(self.H)
		egva=np.sort(egva)
		return(egva)
	def egvect(self):
		egva,egve=np.linalg.eigh(self.H)
		egve=egve.T
		egve=[v for _,v in sorted(zip(egva,egve))]
		return(egve)

class magneticField():
	def __init__(self,x='spherical',y='spherical',z='spherical',theta='cartesian',phi='cartesian',amp='cartesian',**HamiltonianArgs): #Give either x,y,z or theta,phi,amp (polar/azimutal from the z axis)
		if x=='spherical' and theta=='cartesian' :
			raise(ValueError('Wrong input for B'))
		elif x=='spherical':
			self.x=amp*np.cos(theta)*np.sin(phi)
			self.y=amp*np.sin(theta)*np.sin(phi)
			self.z=amp*np.cos(phi)
			self.theta=theta
			self.phi=phi
			self.amp=amp
		elif theta=='cartesian' :
			self.amp=np.sqrt(x**2+y**2+z**2)
			if self.amp==0:
				self.theta=0
				self.phi=0
			else :
				self.theta=np.arccos(z/self.amp)
				self.phi=np.arctan2(y,x)
			self.x=x
			self.y=y
			self.z=z
		else :
			raise(ValueError('You must either give (x,y,z) or (theta,phi,amp )'))
		self.cartesian=np.array([self.x,self.y,self.z])
		self.sphericalDeg=np.array([self.theta*180/np.pi,self.phi*180/np.pi])
		self.HamiltonianArgs=HamiltonianArgs
		self.norm=sqrt(self.x**2+self.y**2+self.z**2)
	def transitions4Classes(self):
		transis=[]
		for i in range(4):
			t=NVHamiltonian(self,c=i+1,**self.HamiltonianArgs).transitions()
			transis+=[t[0],t[1]]
		return np.sort(transis)
	def transitions4ClassesPlus(self):
		transis=[]
		for i in range(4):
			t=NVHamiltonian(self,c=i+1,**self.HamiltonianArgs).transitions()
			transis+=[t[1]]
		return np.sort(transis)
	def transitions4ClassesMoins(self):
		transis=[]
		for i in range(4):
			t=NVHamiltonian(self,c=i+1,**self.HamiltonianArgs).transitions()
			transis+=[t[0]]
		return np.sort(transis)
	def angleFrom100(self):
		scalar=max(abs(self.x),abs(self.y),abs(self.z))/self.amp
		angle=np.arccos(scalar)
		return angle*180/np.pi
	def angleFrom111(self):
		scalar=0
		for c in NVHamiltonian.cs[:4] :
			if abs(c.dot(self.cartesian)) > scalar :
				scalar=abs(c.dot(self.cartesian))
		scalar=scalar/self.amp
		angle=np.arccos(scalar)
		return angle*180/np.pi
	def __repr__(self):
		return('Bx=%f; By=%f, Bz= %f'%(self.x,self.y,self.z))

class electricField():
	def __init__(*params,base='NV'):
		pass

def find_B_cartesian(peaks,Bmax=1000,startingB=False,transis='all'): #Obsolète
	peaks=np.sort(peaks)
	if len(peaks)==8 :
		def err_func(B,peaks): #B is given in the form [x,y,z]
			B=magneticField(x=B[0],y=B[1],z=B[2])
			simuPeaks=B.transitions4Classes()
			err=np.linalg.norm(peaks-simuPeaks)
			return err
	elif len(peaks)==2:
		def err_func(B,peaks): #B is given in the form [x,y,z]
			B=magneticField(x=B[0],y=B[1],z=B[2])
			simuPeaks=B.transitions4Classes()
			completePeaks=np.sort([peaks[0]]*4+[peaks[1]]*4)
			err=np.linalg.norm(completePeaks-simuPeaks)
			return err
	elif len(peaks)==4 and transis=='-': 
		def err_func(B,peaks): #B is given in the form [x,y,z]
			B=magneticField(x=B[0],y=B[1],z=B[2])
			simuPeaks=B.transitions4ClassesMoins()
			err=np.linalg.norm(peaks-simuPeaks)
			return err
	elif len(peaks)==4 and transis=='+': 
		def err_func(B,peaks): #B is given in the form [x,y,z]
			B=magneticField(x=B[0],y=B[1],z=B[2])
			simuPeaks=B.transitions4ClassesPlus()
			err=np.linalg.norm(peaks-simuPeaks)
			return err
	if startingB :
		x0=[startingB.x,startingB.y,startingB.z]
	else :
		x0=[100,0,0]
	sol=minimize(err_func,x0=x0,args=peaks,bounds=[(-1,Bmax),(-1,Bmax),(-1,Bmax)]) #c'est équivalent à un rectangle dans [0,54.74]x[0,45] deg
	return magneticField(x=sol.x[0],y=sol.x[1],z=sol.x[2])

def find_B_cartesian_mesh(peaks,precise=True,transis='all',Blims='auto',n=20,**HamiltonianArgs): #Transi + a l'air de déconner, à vérifier plus tard...

	if Blims=='auto':
		Bmax=(max(peaks)-min(peaks))*sqrt(3)/(2*2.8) #delta nu/(2*gamma)*sqrt(3) C'est calculé pour que le pire cas de figure soit une 100, pas sur de ce que ca vaut pour les gros champs (après Gslac en particulier)
		Blims=[[-1,Bmax],[-1,Bmax],[-1,Bmax]]

	peaks=np.sort(peaks)
	Bxs=np.linspace(Blims[0][0],Blims[0][1],n)
	Bys=np.linspace(Blims[1][0],Blims[1][1],n)
	Bzs=np.linspace(Blims[2][0],Blims[2][1],n)

	opt=np.inf
	if transis=='all':
		def errfunc(B):
			B=magneticField(x=B[0],y=B[1],z=B[2],**HamiltonianArgs)
			simuPeaks=B.transitions4Classes()
			err=np.linalg.norm(peaks-simuPeaks)
			return err
	elif transis=='-' :
		def errfunc(B):
			B=magneticField(x=B[0],y=B[1],z=B[2],**HamiltonianArgs)
			simuPeaks=B.transitions4ClassesMoins()
			err=np.linalg.norm(peaks-simuPeaks)
			return err
	elif transis=='+' :
		def errfunc(B):
			B=magneticField(x=B[0],y=B[1],z=B[2],**HamiltonianArgs)
			simuPeaks=B.transitions4ClassesPlus()
			err=np.linalg.norm(peaks-simuPeaks)
			return err
	else :
		raise(ValueError('Did not understand "transi"'))

	for Bx in Bxs :
		for By in Bys :
			for Bz in Bzs :
				B=[Bx,By,Bz]
				diff=errfunc(B)
				if diff < opt :
					opt=diff
					bestB=B
	bestB=magneticField(x=bestB[0],y=bestB[1],z=bestB[2])
	if not precise :		
		return(bestB)
	else :
		steps=np.array([Bxs[1]-Bxs[0],Bys[1]-Bys[0],Bzs[1]-Bzs[0]])
		x0=[bestB.x,bestB.y,bestB.z]
		bounds=[(x0[i]-steps[i],x0[i]+steps[i]) for i in range(3)]
		sol=minimize(errfunc,x0=x0,bounds=bounds)
		return(magneticField(x=sol.x[0],y=sol.x[1],z=sol.x[2]))

def simu_ESR(x,peaks,widths=8,amps=-0.1,ss=1,typ='gauss'):
	n=len(peaks)
	if not (isinstance(widths,list) or isinstance(widths,np.ndarray)):
		widths=[widths]*n
	if not (isinstance(amps,list) or isinstance(amps,np.ndarray)):
		amps=[amps]*n
	y=np.ones(len(x))*ss
	for i in range(n):
		c=peaks[i]
		width=widths[i]
		amp=amps[i]
		if typ=='gauss' :
			y+=amp*np.exp(-((x-c)/width)**2)
		elif typ=="lor" :
			y+=amp*1/(1+((x-c)/width)**2)
	return y

def find_nearest_ESR(x,y,peaks='auto',Bmax=500,typ='gauss',returnType='default',transis='all',fittingProtocol='cartesian'): #peaks : centers of resonances in MHz
	if peaks=='auto':
		peaks=find_ESR_peaks(x,y)
		if len(peaks)==8 :
			peaks=find_ESR_peaks(x,y,precise=True)
		else :
			raise ValueError('"auto" does not support spectrum without 8 peaks yet')
	popt,yfit= ESR_n_pics(x,y,peaks)
	n=len(peaks)
	ss=popt[0]
	peaks=popt[1]
	widths=popt[2]
	amps=popt[3]
	if fittingProtocol=='cartesian' :
		B=find_B_cartesian_mesh(peaks,transis=transis)
	else :
		raise ValueError('Cartesian only, spherical was not working')
	if transis=='all' :
		cs=B.transitions4Classes()
	elif transis=='+':
		cs=B.transitions4ClassesPlus()
	elif transis=='-':
		cs=B.transitions4ClassesMoins()

	if n==2 :
		widths=[widths[0]]*4+[widths[1]]*4
		amps=[amps[0]/4]*4+[amps[1]/4]*4
	elif n==4 :
		pass #A implanter avec la 111, comme find_B
	yfit=simu_ESR(x,cs,widths,amps,ss,typ=typ)
	def angleFrom100(B):
		scalar=max(abs(B.x),abs(B.y),abs(B.z))/B.amp
		angle=np.arccos(scalar)
		return angle*180/np.pi
	def angleFrom111(B):
		scalar=0
		for c in NVHamiltonian.cs :
			if abs(c.dot(B.cartesian)) > scalar :
				scalar=abs(c.dot(B.cartesian))
		scalar=scalar/B.amp
		angle=np.arccos(scalar)
		return angle*180/np.pi
	if returnType=='spherical' :
		popt=[B.amp,B.theta,B.phi]
	elif returnType=='cartesian' :
		popt=[B.x,B.y,B.z]
	else :
		popt=[B.amp,angleFrom100(B),angleFrom111(B),sum(widths)/len(widths)]
	return popt,yfit

class NV_C13_Hamiltonian():

	def __init__(self,B,c=1,E=4,D=2870,gamma_e=2.8):

		NVHamClass=NVHamiltonian(B,c=c,E=E,D=D,gamma_e=gamma_e)
		self.NVHam=convolution(NVHamClass.H,np.identity(2))

		Ix=1/2*np.array([[0,1],[1,0]])
		Iy=1/2*np.array([[0,0+1j],[0-1j,0]])
		Iz=1/2*np.array([[1,0],[0,-1]])
		gammaNucl=1.07*1e-3 #MHz/G
		self.C13Ham=convolution(np.identity(3),Iz*gammaNucl*NVHamClass.Bz) #C'est peut être la norme de B plutot mais osef un peu vu que ce terme sert à rien

		Axx=190.2
		Ayy=120.3
		Azz=129.1
		Axz=-25
		self.HFHam=Axx*convolution(NVHamClass.Sx,Ix)+Ayy*convolution(NVHamClass.Sy,Iy)+Azz*convolution(NVHamClass.Sz,Iz)+Axz*(convolution(NVHamClass.Sx,Iz)+convolution(NVHamClass.Sz,Ix))

		self.H=self.NVHam+self.C13Ham+self.HFHam

	def egval(self):
		egva,egve=np.linalg.eigh(self.H)
		egva=np.sort(egva)
		return(egva)
	def egvect(self):
		egva,egve=np.linalg.eigh(self.H)
		egve=egve.T
		egve=[v for _,v in sorted(zip(egva,egve))]
		return(egve)

	def transitions(self):
		egv=self.egval()
		g1=egv[0]
		g2=egv[1]
		es=egv[2:]
		transis=[]
		for e in es:
			transis+=[e-g1,e-g2]

		return(np.sort(transis))





	
#~~~~~~ stats ~~~~~~
def make_hist(y,bins=10,**kwargs):
	hist,bins=np.histogram(y,bins=bins,**kwargs)
	newBins=(bins[1:]+bins[:-1])/2
	return(newBins,hist)

def mean(y):
	return np.average(y)

def hist_mean(x,y):
	return np.average(x,weights=y)

def sigma(y):
	mu=mean(y)
	return np.sqrt(np.average((y-mu)**2))

def hist_sigma(x,y):
	mu=hist_mean(x,y)
	return np.sqrt(np.average((x-mu)**2,weights=y))

def closest_elem(l,target):
	basis=abs(target-l[0])
	n=0
	for i in range(len(l)):
		if abs(target-l[i]) < basis:
			n=i
			basis=abs(target-l[i])
	return n

def estim_error(y,yfit,rel=True):
	#C'est pas si simple, si tu prends juste l'erreur relative de chaque point tu donnes beaucoup plus de poids aux valeurs proches de 0. Le je fais un truc un peu sale mais qui donne autant de poids (absolu) à chaque point
	n=len(y)
	assert n==len(yfit)
	y=np.array(y)
	yfit=np.array(yfit)
	vAvg=sum(abs(yfit))/n #le abs est crade mais au cas ou tu aies des valeurs positives et négatives
	if rel :
		errors=(y-yfit)**2/vAvg**2
	else :
		errors=(y-yfit)**2
	return(sum(errors)/n)

def RMSD(y,yfit):
	#root mean square deviation/error
	return sigma(y-yfit)

def R2(y,yfit):
	R=1-sigma(y-yfit)**2/sigma(y)**2
	return R

def concatenate(t,n,moving_average=True,norm=True):
    if moving_average:
        if norm :
            newt=np.array([sum(t[i:i+n])/n for i in range(len(t)-n)])
        else :
            newt=np.array([sum(t[i:i+n]) for i in range(len(t)-n)])
    else :
        s=len(t)//n
        if norm :
            newt=np.array([sum(t[n*i:n*(i+1)])/n for i in range(s)])
        else :
            newt=np.array([sum(t[n*i:n*(i+1)]) for i in range(s)])

    return newt

def reduce_array(array,new_array_size):
	N=len(array)
	n=new_array_size

	yold=array
	ynew=np.zeros(n)

	xold=np.linspace(0,1,N)
	xnew=np.linspace(0,1,n+1)

	indices=np.zeros(n+1,dtype=int)
	k=0
	for i in range(N):
		if xold[i]>xnew[k] :
			indices[k]=i
			k+=1
	indices[0]=0
	indices[-1]=N
	for i in range(n):
		ynew[i]=sum(yold[indices[i]:indices[i+1]]/(indices[i+1]-indices[i]))
	return (ynew)
	



def average(t,n):
	m=len(t)//n
	newt=np.array([sum(t[n*i:n*(i+1)])/n for i in range(m)])
	return newt

def derivative(x,y):
	dx=x[1]-x[0]
	n=len(y)
	assert n==len(x)
	y2=np.array([(y[i+1]-y[i])/dx for i in range(n-1)])
	x2=np.array([(x[i+1]+x[i])/2 for i in range(n-1)])
	return(x2,y2)

def integration(x,y):
	dx=x[1]-x[0]
	s=(y[0]+y[-1])/2
	for i in range(1,len(y)-1):
		s+=y[i]
	s=s*dx
	return(s)

def psd(x,y,plot=False): #Assume que x est en s.
	import scipy.signal

	df=1/(x[1]-x[0])
	# f contains the frequency components
	# S is the PSD
	(f, S) = scipy.signal.periodogram(y, df, scaling='density')

	if not plot :
		return f,S

	if plot:
		plt.semilogy(f, S)

		ymin,ymax=plt.ylim()
		logS=np.log(S)
		logAvg=mean(logS)
		logSigma=sigma(logS)
		logYmin=logAvg-5*logSigma
		ymin=np.exp(logYmin)
		plt.ylim([ymin,ymax])

		plt.xlabel('frequency [Hz]')
		plt.ylabel('PSD [V**2/Hz]')
		plt.show()
		return

def lor(x,x0=0,sigma=1,norm=True):
	y=sigma**2/((x-x0)**2+sigma**2)
	if norm:
		return y/(pi*sigma)
	else :
		return y

def gauss(x,x0=0,sigma=1,norm=True):
	y=exp(-(x-x0)**2/(2*sigma**2))
	if norm:
		return y/(sqrt(2*pi)*sigma)
	else :
		return y

#~~~~~~ Math ~~~~~~~~

def lcm(a,b):
	#existe de base dans python 3.9, mais pas dans les autre
	import math
	return abs(a*b) // math.gcd(a, b)

#~~~~~~ Algebre ~~~~~~

def convolution(M1,M2):
	l1=len(M1[:,0])
	l2=len(M2[:,0])
	l=l1*l2
	M=np.zeros((l,l),dtype=complex)
	for i1 in range(l1) :
		for j1 in range(l1) :
			for i2 in range(l2) :
				for j2 in range(l2) :
					i=i1*l2+i2
					j=j1*l2+j2
					M[i,j]=M1[i1,j1]*M2[i2,j2]
	return(M)

def solve_rate_equation(*Ms):
	#Ms=Matrice de passage avec le taux de passage de départ (colonne) vers ligne
	#Exemple : gamma_las pour un NV dans la base (0,-1,+1)
	gexample=1e-3
	Mexample=gexample*np.array([
	[0,1,1],
	[0,0,0],
	[0,0,0]])

	M0=Ms[0]
	n=len(M0[0,:])

	M=sum(Ms)
	for j in range(n):
		M[j,j]=-sum(M[:,j])
	M[n-1,:]=np.ones(n)

	sol=np.array([0]*(n-1)+[1])
	X=np.linalg.inv(M).dot(sol)

	return(X)

#~~~~~~ 2D plot ~~~~~~
def extract_2d(fname):
	data=[]
	with open(fname,'r',encoding = "ISO-8859-1") as f:
		for line in f:
			line=line.split()
			try :
				row=[float(elem) for elem in line]
				data+=[row]
			except :
				pass
	return(np.array(data))

def gradientCompensation(data2D):
	lavg=sum(data2D[:,i] for i in range(len(data2D[0,:])))/len(data2D[0,:])
	cavg=sum(data2D[i,:] for i in range(len(data2D[:,0])))/len(data2D[:,0])
	[a1,b],lfit=lin_fit(y=lavg)
	lxfit=np.arange(len(lfit))
	[a2,b],cfit=lin_fit(y=cavg)
	cxfit=np.arange(len(cfit))

	for i in range(len(data2D[:,0])):
		for j in range(len(data2D[0,:])):
			data2D[i,j]-=a1*lxfit[i]+a2*cxfit[j]
	return(data2D)

def plot_map(C:np.array, vAxis=[], hAxis=[], color='viridis',invertV=False,invertH=False,flipHV=False,squarePixels=True,correctGradient=False, vmin=None, vmax=None, vlabel='Y voltage (V)',hlabel='X voltage (V)',colorBarLabel='', centerColorBar=None, figSize=None, removeCb=False, show=True, hlim=None, vlim=None):
	#color : "viridis", "Blues_r", "bwr" ...
	#invertX/Y: inverts the x/y axis (biggest values on tthe lefet)
	#flipXY : flips the x and y axes
	#squarePixels : Ensure that the pixels are squared (in the future, maybe put a ratio of x/y length for each pixel)
	#correctGradient : compensate the gradients (1st order) in both x and y
	#vmin/max : min/max values on the scale
	#x/y label : label of the x and y axes
	#colorBarLabel : label of the colorbar

	nv,nh=np.shape(C)
	if len(vAxis)==0:
		vAxis=np.linspace(0,1,nv)
	elif len(vAxis)!=nv:
		vAxis=np.linspace(vAxis[0],vAxis[-1],nv)
	if len(hAxis)==0:
		hAxis=np.linspace(0,1,nh)
	elif len(hAxis)!=nh:
		hAxis=np.linspace(hAxis[0],hAxis[-1],nh)
	  
	if flipHV :
		C=C.T
		hAxis,vAxis=vAxis,hAxis
		hlabel,vlabel=vlabel,hlabel
	if correctGradient :
		C=gradientCompensation(C)
	
	fig, ax = plt.subplots(figsize=figSize)
	if squarePixels :
		ax.set_aspect('equal')
	if vmin is None :
		vmin=np.nanmin(C)
	if vmax is None :
		vmax=np.nanmax(C)
	if centerColorBar is not None :
		Delta=max(abs(vmin-centerColorBar),abs(vmax-centerColorBar))
		vmin=centerColorBar-Delta
		vmax=centerColorBar+Delta
	scan=ax.pcolormesh(hAxis,vAxis,C,cmap=color,vmin=vmin,vmax=vmax,shading='nearest')

	if invertV :
		ax.invert_xaxis()
	if invertH :
		ax.invert_yaxis()
	ax.set_xlabel(vlabel)
	ax.set_ylabel(hlabel)
	if hlim is not None :
		ax.set_xlim(hlim)
	if vlim is not None :
		ax.set_ylim(vlim)
	cb=plt.colorbar(mappable=scan,ax=ax,label=colorBarLabel)
	fig.set_tight_layout(tight=True)
	if removeCb :
		cb.remove()
	if show :
		plt.show()
	


#~~~~~~ Présentation ~~~~~~

def color(i):
	colors=plt.rcParams['axes.prop_cycle'].by_key()['color']
	return(colors[i])

def ecris_gros(x,y):
	plt.figure(num=1,figsize=(9,6),dpi=80) #à écrire au début a priori


	ax=plt.gca()
	ax.tick_params(labelsize=20)
	ax.set_xlabel(r'B $\parallel$[100] (G)',fontsize=20,fontweight='bold')
	ax.set_ylabel(r'Photoluminescence' ,fontsize=20,fontweight='bold')
	color = next(ax._get_lines.prop_cycler)['color']
	plt.plot(x,y,'o',markerfacecolor="None",ms=8,mew=2,color=color)
	err_sup=[1.05]*len(x)
	err_inf=[0.95]*len(x)
	ax.fill_between(x,err_inf,err_sup,alpha=0.3,color='red')

def petite_figure():
	plt.figure(num=1,figsize=(3,2),dpi=80)
	plt.xticks(fontsize=12)
	plt.yticks(fontsize=12)
	plt.locator_params(axis='x', nbins=5)

def exemple_animation():
	import matplotlib.animation as animation
	fnames,fval=extract_glob('Série ESR 2',16)
	fig = plt.figure() # initialise la figure
	line, = plt.plot([], []) 
	x,y=extract_data(fnames[0])
	plt.xlim(min(x), max(x))
	plt.ylim(min(y),max(y))

	def animate(i): 
		f=fnames[i]
		x,y=extract_data(f)
		line.set_data(x, y)
		return line,
	 
	ani = animation.FuncAnimation(fig, animate, frames=len(fnames), blit=True, interval=50, repeat=False)

	plt.show()

def print_matrix(M,bname='default') :
	from tabulate import tabulate
	if bname=='default':
		bname=['%i'%i for i in range(len(M[0,:]))]
	
	if M.dtype.name=='float64' :
		headers=['']+['|'+name+'>' for name in bname]
		table=[]
		for i in range(len(bname)) :
			line=[]
			line+=['<'+bname[i]+'|']
			values=list(M[i,:])
			line+=values
			table+=[line]
		print(tabulate(table,headers))

	elif M.dtype.name=='complex128' :
		print('Real Part :')
		headers=['']+['|'+name+'>' for name in bname]
		table=[]
		for i in range(len(bname)) :
			line=[]
			line+=['<'+bname[i]+'|']
			line+=[v.real for v in M[i,:]]
			table+=[line]
		print(tabulate(table,headers),'\n')

		print('Imaginary Part :')
		headers=['']+['|'+name+'>' for name in bname]
		table=[]
		for i in range(len(bname)) :
			line=[]
			line+=['<'+bname[i]+'|']
			line+=[v.imag for v in M[i,:]]
			table+=[line]
		print(tabulate(table,headers))

#~~~~~~~~ Outils ~~~~~~~~~~

def order_list(fnames,FirstValIndex='default', LastValIndex=-4):
	if FirstValIndex=='default':
		elem=fnames[0]
		FirstValIndex=LastValIndex
		numcharac=['%i'%i for i in range(10)]+['.'] #numbers can include decimal points. Should - also be included ?
		while elem[FirstValIndex-1] in numcharac :
			FirstValIndex-=1


	fval=[float(fnames[i][FirstValIndex:LastValIndex]) for i in range(len(fnames))] 
	fnames=[s for _,s in sorted(zip(fval,fnames))]
	fval=sorted(fval)
	return(fnames,fval)

def extract_glob(SubFolderName='.',FirstValIndex='default', LastValIndex=-4): #FirstValIndex=premier caractère numérique
	fnames=glob.glob(SubFolderName+'/*.csv')+glob.glob(SubFolderName+'/*.mat')
	return(order_list(fnames,FirstValIndex=FirstValIndex, LastValIndex=LastValIndex))

def ask_name():
	qapp = QApplication(sys.argv)
	fname,filters=QFileDialog.getOpenFileName()	
	return fname

def save_data(*columns,fname='default',dirname='./'):
	import csv
	from pathlib import Path
	fname=dirname+fname+'.csv'

	with open(fname,'w',newline='') as csvfile :
		spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		for c in columns :
			spamwriter.writerow(c)

def find_elem(elem,liste):
	try :
		elem[0] #du sale, mais je me trompe souvent entre elem et liste. Ca devrait fonctionner
		elem,liste=liste,elem
	except:
		pass

	if elem in liste :
		l=list(liste)
		i=l.index(elem)
		return i
	else :
		dif=np.inf
		for i in range(len(liste)):
			if abs(liste[i]-elem) < dif :
				dif=abs(liste[i]-elem)
				index=i
		return index

def find_local_min(x,y,x0):
	i=find_elem(x,x0)
	while y[i+1]<y[i]:
		i+=1
	while y[i-1]<y[i]:
		i-=1
	return i

def find_local_max(x,y,x0):
	i=find_elem(x,x0)
	while y[i+1]>y[i]:
		i+=1
	while y[i-1]>y[i]:
		i-=1
	return i

def sort_y_by_x(x,y):
	y=[s for _,s in sorted(zip(x,y))]
	x=sorted(x)
	return(x,y)

def dichotomy(f,target,xmin,xmax,precision='auto',**fargs):
	import time
	tmax=10 #s

	assert (f(xmax,**fargs)-target)*(f(xmin,**fargs)-target) < 0

	if f(xmax,**fargs)-target > 0:
		pass
	else :
		xmin,xmax=xmax,xmin #S'arrange pour que f(xmax)> target et f(xmin)< target

	if precision=='auto':
		precision=abs((f(xmax,**fargs)-target))*1e-10


	t=time.time()
	ctr=0
	delta=f(xmax,**fargs)-f(xmin,**fargs)
	while delta > precision:
		xmid=(xmin+xmax)/2
		if f(xmid,**fargs)>target:
			xmax=xmid
		else :
			xmin=xmid

		delta=f(xmax,**fargs)-f(xmin,**fargs)
		ctr+=1
		if time.time()-10>t:
			raise ValueError('Took too long (iter=%i)'%ctr)

	return(xmin,xmax)



