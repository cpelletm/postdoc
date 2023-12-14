import numpy as np
from scipy.optimize import curve_fit,root_scalar,minimize

class fit():
    def __init__(self):
        self.free_params_guess = {'background': 'default', 'amplitude': 'default', 'center': 'default', 'sigma': 6}
        self.formula_display='background-amplitude/(1+((x-center)/sigma)**2)'


    def f(self,x,background,amplitude,center,sigma):
        return background-amplitude/(1+((x-center)/sigma)**2)
        
    def fit(self,x,y):
        if self.free_params_guess['background'] == 'default':
            background_guess = y[0]
        else :
            background_guess = self.free_params_guess['background']

        if self.free_params_guess['amplitude'] == 'default':
            amplitude_guess = max(y)-min(y)
        else :
            amplitude_guess = self.free_params_guess['amplitude']

        if self.free_params_guess['center'] == 'default':
            center_guess = x[np.argmin(y)]
        else :
            center_guess = self.free_params_guess['center']

        sigma_guess = self.free_params_guess['sigma']
        popt, pcov = curve_fit(self.f, x, y, p0=[background_guess,amplitude_guess,center_guess,sigma_guess])

        self.free_params={'background':popt[0],'amplitude':popt[1],'center':popt[2],'sigma':popt[3]}
        self.free_params_std={'background':np.sqrt(pcov[0,0]),'amplitude':np.sqrt(pcov[1,1]),'center':np.sqrt(pcov[2,2]),'sigma':np.sqrt(pcov[3,3])}
        self.fittedY=self.f(x,*popt)

    def legend(self):
        legend='f0= %.2f, sigma= %.2f'%(self.free_params['center'],self.free_params['sigma'])
        return legend

