import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QFileDialog


#Used principally to create or load a shape (matrix with 0 and ones)
class maskArray():
    def __init__(self,array=None):
        if type(array) == np.ndarray:
            self.mask = array
        else:
            self.mask = np.zeros((100,100))

        from matplotlib.colors import colorConverter, LinearSegmentedColormap
        color1=colorConverter.to_rgba('white',alpha=0.0)
        color2=colorConverter.to_rgba('red',alpha=0.8)
        self.maskCmap=LinearSegmentedColormap.from_list('my_cmap2',[color1,color2],256)

    def create(self,baseArray=np.zeros((512,512)),fig=None):
        #Create a mask based on the vertices of a polygon
        #baseArray is the image on which the mask is created
        #The mask is stored in self.mask
        self.mask = np.zeros(baseArray.shape[:2])
        self.maskVertices = []
        if fig==None:
            self.fig = plt.figure()
        else:
            self.fig=fig
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.ax.imshow(baseArray,origin='lower')
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.maskImage=False
        self.maskDone=False
        self.fig.canvas.draw()
        self.fig.canvas.mpl_connect('button_press_event',self.onclick)
        plt.show()
    def onclick(self,event):
        #Function called when a click is performed on the image
        #The click position is stored in self.maskVertices
        if self.maskDone:
            return
        if event.button==1:
            #Left click: add a vertex
            self.maskVertices+=[[int(event.xdata),int(event.ydata)]]
            self.makeMaskEdges()
            if self.maskImage:
                self.maskImage.remove()
            self.maskImage=self.ax.imshow(self.maskEdges,cmap=self.maskCmap,origin='lower')
            self.fig.canvas.draw()
        elif event.button==3:
            #Right click : remove the last vortex
            if len(self.maskVertices)>0:
                self.maskVertices=self.maskVertices[:-1]
                self.makeMaskEdges()
                if self.maskImage:
                    self.maskImage.remove()
                self.maskImage=self.ax.imshow(self.maskEdges,cmap=self.maskCmap,origin='lower')
                self.fig.canvas.draw()
    def makeMaskEdges(self):
        #Create the edge of the mask from the vertices
        #The mask edges are stored in self.maskEdges
        self.maskEdges = np.zeros(self.mask.shape)
        self.maskEdges[self.maskVertices[0][1],self.maskVertices[0][0]]=1

        def line_interpolation(x1,y1,x2,y2):
            #Create a line between (x1,y1) and (x2,y2)

            def yValue(x):
                return (y2-y1)/(x2-x1)*(x-x1)+y1
            def xValue(y):
                return (x2-x1)/(y2-y1)*(y-y1)+x1
            
            n=max(abs(x2-x1),abs(y2-y1))
            for i in range(n):
                if abs(x2-x1)>abs(y2-y1):
                    x = x1+i*(x2-x1)/n
                    y = yValue(x)
                else:
                    y = y1+i*(y2-y1)/n
                    x = xValue(y)
                self.maskEdges[int(y),int(x)]=1

        if len(self.maskVertices)>1:
            for i in range(1,len(self.maskVertices)):
                line_interpolation(self.maskVertices[i-1][0],self.maskVertices[i-1][1],self.maskVertices[i][0],self.maskVertices[i][1])
    
    def fillMask(self):
        #Add the first vortex to close the loop
        self.maskVertices+=[self.maskVertices[0]]
        self.makeMaskEdges()
        self.maskDone=True


        #Fill the mask inside the polygon defined in self.create()
        if len(self.maskVertices)<3:
            raise ValueError('Not enough vertices')
        self.mask = np.copy(self.maskEdges)
        #Windows does not allow to increase the recursion limit, so we use a different algorithm
        #(If you want the better algorithm, use a better OS)
        if os.name=='nt':
            fillAlgorithm='even-odd line crossing'
        elif os.name=='posix':
            fillAlgorithm='recursive paint bucket'
        else:
            raise ValueError('Unknown OS')
        if fillAlgorithm=='recursive paint bucket':
            #We first create a super mask which is 1 point bigger than the mask (to make sure that (1,1) is outside the mask)
            #And again one point bigger to create a border
            superMask=np.zeros((self.mask.shape[0]+4,self.mask.shape[1]+4))
            superMask[2:-2,2:-2]=self.maskEdges
            superMask[0,:]=1
            superMask[-1,:]=1
            superMask[:,0]=1
            superMask[:,-1]=1
            #We start from the top left corner
            #Note : Python does not like recusrion too much, we have to increase the recursion length, so this is potentially dangerous
            #From a few test, it seems to be ok up to 1000x1000 pixels
            sys.setrecursionlimit(superMask.shape[0]*superMask.shape[1])
            import resource
            resource.setrlimit(resource.RLIMIT_STACK, (2**29,-1))
            def recursiveFill(i,j):
                if superMask[i,j]==0:
                    superMask[i,j]=-1
                    recursiveFill(i-1,j)
                    recursiveFill(i+1,j)
                    recursiveFill(i,j-1)
                    recursiveFill(i,j+1)
            recursiveFill(1,1)
            for i in range(self.mask.shape[0]):
                for j in range(self.mask.shape[1]):
                    if superMask[i+2,j+2]==0:
                        self.mask[i,j]=1

        elif fillAlgorithm=='even-odd line crossing':           
            #First fill the mask horizontally
            for i in range(self.mask.shape[0]):
                #count the number of edges crossed
                nEdges=0
                for j in range(self.mask.shape[1]):
                    if self.maskEdges[i,j]==1 and self.maskEdges[i,j-1]==0:
                        nEdges+=1
                if nEdges%2==0:
                    #If the number of edges crossed is even, we cross the mask. Otherwise we are only on the edge
                    polarity=0
                    for j in range(self.mask.shape[1]):
                        if self.maskEdges[i,j]==1 and self.maskEdges[i,j-1]==0:
                            polarity=1-polarity
                        if polarity==1:
                            self.mask[i,j]=1
            #Then fill the mask vertically
            for j in range(self.mask.shape[1]):
                #count the number of edges crossed
                nEdges=0
                for i in range(self.mask.shape[0]):
                    if self.maskEdges[i,j]==1 and self.maskEdges[i-1,j]==0:
                        nEdges+=1
                if nEdges%2==0:
                    #If the number of edges crossed is even, we cross the mask. Otherwise we are only on the edge
                    polarity=0
                    for i in range(self.mask.shape[0]):
                        if self.maskEdges[i,j]==1 and self.maskEdges[i-1,j]==0:
                            polarity=1-polarity
                        if polarity==1:
                            self.mask[i,j]=1
            #Fill the holes                
            for i in range(1,self.mask.shape[0]-1):                
                for j in range(1,self.mask.shape[1]-1):
                    if self.mask[i-1,j]==1 and self.mask[i+1,j]==1:
                        self.mask[i,j]=1
                    if self.mask[i,j-1]==1 and self.mask[i,j+1]==1:
                        self.mask[i,j]=1

        #Plot the filled mask
        if self.maskImage:
            self.maskImage.remove()
        self.maskImage=self.ax.imshow(self.mask,cmap=self.maskCmap,origin='lower')
        self.fig.canvas.draw()
    def restart(self):
        self.maskVertices=[]
        self.maskEdges=np.zeros(self.mask.shape)
        self.mask=np.zeros(self.mask.shape)
        self.maskDone=False
        if self.maskImage:
            self.maskImage.remove()
        self.maskImage=self.ax.imshow(self.maskEdges,cmap=self.maskCmap,origin='lower')
        self.fig.canvas.draw()
    def plot(self,ax=None,show=True):
        #Show the mask
        if ax==None:
            fig,ax=plt.subplots()
        im=ax.imshow(self.mask,cmap=self.maskCmap,origin='lower')
        if show:
            plt.show()
        return im
    def save(self,filename='prompt'):
        #Save the mask in a file
        if filename=='prompt':
            qapp = QApplication(sys.argv)
            currentFolder = os.getcwd()
            filename,filter = QFileDialog.getSaveFileName( caption='Save file', directory=currentFolder, filter='numpy (*.npy);;csv (*.csv);;txt (*.txt)', initialFilter='numpy (*.npy)')
        if filename=='':
            print('No file selected')
            return filename
        if filename[-4:]=='.npy':
            np.save(filename,self.mask)
        elif filename[-4:]=='.csv':
            np.savetxt(filename,self.mask,delimiter=',',fmt='%i')
        elif filename[-4:]=='.txt':
            np.savetxt(filename,self.mask,delimiter=' ',fmt='%i')
        return filename
    def load(self,filename):
        #Load the mask from a file
        if filename[-4:]=='.npy':
            self.mask = np.load(filename)
        elif filename[-4:]=='.csv':
            self.mask = np.loadtxt(filename,delimiter=',',dtype=int)
        elif filename[-4:]=='.txt':
            self.mask = np.loadtxt(filename,delimiter=' ',dtype=int)


"""
General remarks on numpy FFT :
By default, forward FFT (np.fft in 1D or np.fft.fft2 in 2D) have the higher frequencies in the center of the array, and the lower frequencies on the side.
If you want to see the actual frequencies, use np.fft.fftfreq
You can bring back the higher frequencies to the edges of the array with np.fft.fftshift, but you need to go back before you apply the inverse FFT

Remarks on matrix ordering in numpy :
In numpy, the first index is the row, the second is the column, left to right and top to bottom. 
Example : M=[[M[0,0],M[0,1]],
             [M[1,0],M[1,1]]]

And     V=[V[0],
           V[1]]

np.dot(M,V) will give [M[0,0]*V[0]+M[0,1]*V[1],
                       M[1,0]*V[0]+M[1,1]*V[1]]
(which follows the usual convention in matrix algebra)
"""

class filter():
    def __init__(self,baseArray,typ='gaussian',lx=1,ly=1,filterSize=1):
        #filtersize in real space
        self.baseArray=baseArray
        self.typ=typ
        self.sigma=1/(2*np.pi*filterSize)
        self.nx=baseArray.shape[0]
        self.ny=baseArray.shape[1]
        self.kxs=np.fft.fftfreq(self.nx,lx/self.nx)
        self.kys=np.fft.fftfreq(self.ny,ly/self.ny)
        self.filterArray=np.zeros(baseArray.shape)
        self.makeFilter()
        
    def makeFilter(self):
        if self.typ=='gaussian':
            def filterFunction(kx,ky):
                return np.exp(-(kx**2+ky**2)/(2*self.sigma**2))
        elif self.typ=='circle':
            def filterFunction(kx,ky):
                return np.sqrt(kx**2+ky**2)<self.sigma
        elif self.typ=='square':
            def filterFunction(kx,ky):
                return abs(kx)<self.sigma and abs(ky)<self.sigma
        else:
            raise ValueError('Unknown filter type')
        for i in range(self.nx):
            for j in range(self.ny):
                self.filterArray[i,j]=filterFunction(self.kxs[i],self.kys[j])

class forwardPropagation():
    def __init__(self,magArray:np.ndarray,lx=1,ly=1,z=1,gaussianSmooth=0,magUnit=None):
        #magArray is the magnetization of the flake in real space (in magnetic moment per surface unit). It has to contain the magnetization along all 3 axes (dimension nx,ny,3)
        #magArray should have its origin at the bottom left corner, x axis horizontal and y axis vertical when plotted with plt.imshow
        #Assumes lx (full length in x), ly and z are in nm
        #gaussianSmooth is the standard deviation of the gaussian smoothing applied to the magnetization before the reverse FFT (in nm)
        #magUnit = {None, 'SI', 'muB'} : if None, no normalization is applied. If 'SI', the magnetization is in A. If 'muB', the magnetization is in Bohr magneton per surface unit
        #The magnetic field is in T if magUnit is 'SI', and in Gauss if magUnit is 'muB'
        self.magArray=magArray
        self.TFmagArray=fft3d(magArray)
        if magArray.shape[2]!=3:
            raise ValueError('magArray has to contain the 3d magnetization (dimension nx,ny,3)')
        self.lx=lx
        self.ly=ly
        self.z=z
        self.gaussianSmooth=gaussianSmooth
        self.nx=magArray.shape[0]
        self.ny=magArray.shape[1]
        self.kxs=np.fft.fftfreq(self.nx,lx/self.nx)
        self.kys=np.fft.fftfreq(self.ny,ly/self.ny)
        self.BArray=np.zeros(magArray.shape)
        self.TFBArray=np.zeros(magArray.shape,dtype=complex)
        if magUnit=='SI':
            mu0=4*np.pi*1e-7
            mu02D=mu0*1e9 #mu0 in T.nm/A (k is in nm^-1)
            self.propconstant=mu02D/2
        elif magUnit=='muB':
            mu0=4*np.pi*1e-7
            muB=9.274009994e-24
            mu02D=mu0*muB*10**(4+27) #mu0 in G/(muB/nm^3) (m is in muB/nm^2 and k is in nm^-1)
            self.propconstant=mu02D/2
        else:
            self.propconstant=1
        self.makeBArray()
        
    def makeBArray(self):
        #Propagation matrix curtesy of Lucas Thiel phD, I hope he was right
        def propMatrix(kx,ky,z):
            k=np.sqrt(kx**2+ky**2)
            D=np.zeros((3,3),dtype=complex)
            if k==0:
                D[2,2]=1
            else :
                D[0,0]=-(kx/k)**2
                D[0,1]=-(kx*ky/k**2)
                D[0,2]=-1j*kx/k
                D[1,0]=-(kx*ky/k**2)
                D[1,1]=-(ky/k)**2
                D[1,2]=-1j*ky/k
                D[2,0]=-1j*kx/k
                D[2,1]=-1j*ky/k
                D[2,2]=1
            D=D*k*np.exp(-k*z)*self.propconstant
            return D
        for i in range(self.nx):
            for j in range(self.ny):
                self.TFBArray[i,j,:]=np.dot(propMatrix(self.kxs[i],self.kys[j],self.z),self.TFmagArray[i,j,:])
        if self.gaussianSmooth>0:
            TFfilter=filter(self.TFBArray,typ='gaussian',lx=self.lx,ly=self.ly,filterSize=self.gaussianSmooth).filterArray
            self.TFBArray=self.TFBArray*TFfilter
      
        self.BArray=fft3d(self.TFBArray,inverse=True).real

    def plot3dField(self,ax=None,show=True,**plotargs):
        plot3Darray(self.BArray,ax=ax,show=show,centered=True,**plotargs)

    def plotFieldProjection(self,orientation='',theta=0,phi=0,ax=None,show=True,**plotargs):
        #theta and phi in degrees
        if orientation=='z':
            theta=0
            phi=0
        elif orientation=='x':
            theta=90
            phi=0
        elif orientation=='y':
            theta=90
            phi=90
        elif orientation=='NV1':
            theta=54.7
            phi=0
        elif orientation=='NV2':
            theta=54.7
            phi=90
        elif orientation=='NV3':
            theta=54.7
            phi=180
        elif orientation=='NV4':
            theta=54.7
            phi=270
        
        ux=np.sin(theta*np.pi/180)*np.sin(phi*np.pi/180)
        uy=np.sin(theta*np.pi/180)*np.cos(phi*np.pi/180)
        uz=np.cos(theta*np.pi/180)
        Bproj=ux*self.BArray[:,:,0]+uy*self.BArray[:,:,1]+uz*self.BArray[:,:,2]
        return plot2Darray(Bproj,ax=ax,show=show,centered=True,**plotargs)

def fft3d(array,shift=False,inverse=False):
    #FFT of a 3d array
    assert(array.shape[2]==3)
    TFarray=np.zeros(array.shape,dtype=complex)
    for i in range(3):
        if inverse:
            TFarray[:,:,i]=np.fft.ifft2(array[:,:,i])
        else:
            TFarray[:,:,i]=np.fft.fft2(array[:,:,i])
        if shift:
            TFarray[:,:,i]=np.fft.fftshift(TFarray[:,:,i])     
    return TFarray

def plot2Darray(array,ax=None,show=True,centered=False,title=None):
    #Plot a single component of a 3d array
    if ax==None:
        fig,ax=plt.subplots()
    else :
        fig=ax.get_figure()
    if centered:
        vmin,vmax=-np.max(abs(array)),np.max(abs(array))
    else:
        vmin,vmax=np.min(array),np.max(array)
    image=ax.imshow(array,cmap='RdBu',vmin=vmin,vmax=vmax,origin='lower')
    if title:
        ax.set_title(title)
    cbar=fig.colorbar(image,ax=ax)
    cbar.minorticks_on()
    if show:
        fig.set_tight_layout(True)
        plt.show()
    return image,cbar

def plot3Darray(array,ax=None,show=True,centered=False):
    #Plot the 3 components side by side
    if ax==None:
        fig,ax=plt.subplots(figsize=(13, 3), ncols=3)
    names=['x','y','z']
    for i in range(3):
        plot2Darray(array[:,:,i],ax=ax[i],show=False,centered=centered,title=names[i])
    if show:
        fig.set_tight_layout(True)
        plt.show()

def homogeneous3dMag(shape,orientation='',theta=0,phi=0,Ms=1):
    #Shape is a 2d array containing the shape of the flake (in 0 and 1), or a maskArray object
    #theta and phi are the angles of the magnetization in degrees
    #Ms is the saturation magnetization (in whatever unit you use)
    if type(shape)==maskArray:
        shape=shape.mask
    if orientation=='z':
        theta=0
        phi=0
    elif orientation=='x':
        theta=90
        phi=0
    elif orientation=='y':
        theta=90
        phi=90
    mag=np.zeros((shape.shape[0],shape.shape[1],3))
    mag[:,:,0]=shape*Ms*np.sin(theta*np.pi/180)*np.sin(phi*np.pi/180)
    mag[:,:,1]=shape*Ms*np.sin(theta*np.pi/180)*np.cos(phi*np.pi/180)
    mag[:,:,2]=shape*Ms*np.cos(theta*np.pi/180)
    return mag

if __name__=='__main__':
    ma=maskArray()
    ma.load('/home/clement/Postdoc/python/Perso/test_shape.npy')
    mag=homogeneous3dMag(ma.mask,theta=0,phi=90,Ms=24)
    # TFmag=fft3d(mag,shift=True)
    # plot3darray(abs(TFmag))
    # TFmask=filter(TFmag,typ='gaussian',lx=1,ly=10,filterSize=10).filterArray
    # TFmag=TFmag*TFmask


    prop=forwardPropagation(mag,lx=15000,ly=15000,z=50,gaussianSmooth=50,magUnit='muB')
    prop.plotFieldProjection(orientation='x')




        