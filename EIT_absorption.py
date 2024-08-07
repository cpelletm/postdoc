import numpy as np
import matplotlib.pyplot as plt

Omega_C= 0.5
Omega_P= 0.01

def Chi(Delta_P,Delta_C):
    delta= Delta_P-Delta_C
    return delta/(2j*delta+4*Delta_P*delta-abs(Omega_C)**2)

def Chi2(delta,Delta_P):
    return delta/(2j*delta+4*Delta_P*delta-abs(Omega_C)**2)

def plot_Delta_P_and_Delta_C():
    # Plot chi vs Delta_P and Delta_C
    min_Delta= -3
    max_Delta= 3
    n_pixel= 512
    Delta_P= np.linspace(min_Delta,max_Delta,n_pixel)
    Delta_C= np.linspace(min_Delta,max_Delta,n_pixel)
    X,Y= np.meshgrid(Delta_P,Delta_C)
    Z= Chi(X,Y)

    plt.imshow(-np.imag(Z),extent=[min_Delta,max_Delta,min_Delta,max_Delta],origin='lower',cmap='viridis')
    plt.xlabel(r'$\Delta_P$',fontsize=14)
    plt.ylabel(r'$\Delta_C$',fontsize=14)
    plt.title('EIT absorption')
    cb=plt.colorbar()
    cb.set_label('Absorption')
    plt.show()

def plot_delta_and_Delta_P():
    # Plot chi vs delta and Delta_P
    min_Delta= -3
    max_Delta= 3
    n_pixel= 512
    Delta_P= np.linspace(min_Delta,max_Delta,n_pixel)
    delta= np.linspace(min_Delta,max_Delta,n_pixel)
    X,Y= np.meshgrid(delta,Delta_P)
    Z= Chi2(X,Y)

    plt.imshow(-np.imag(Z),extent=[min_Delta,max_Delta,min_Delta,max_Delta],origin='lower',cmap='viridis')
    plt.xlabel(r'$\delta$',fontsize=14)
    plt.ylabel(r'$\Delta_P$',fontsize=14)
    plt.title('EIT absorption')
    cb=plt.colorbar()
    cb.set_label('Absorption')
    plt.show()

# plot_Delta_P_and_Delta_C()
plot_delta_and_Delta_P()