import numpy as np
import matplotlib.pyplot as plt

#Plot an arrow on a sphere
def plot_arrow(ax, theta, phi, color='red'):
    arrow=ax.quiver(0, 0, 0, np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta), color=color, arrow_length_ratio=0.1)
    arrow.theta=theta
    arrow.phi=phi
    return arrow

#Plot a sphere
def plot_sphere(ax: plt.Axes):
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='red', alpha=0.1)
    return 

#Plot the equator of the sphere
def plot_equator(ax):
    u = np.linspace(0, 2 * np.pi, 100)
    x = np.cos(u)
    y = np.sin(u)
    z = np.zeros(np.size(u))
    ax.plot(x, y, z, color='blue')

#Plot the meridian of the sphere
def plot_meridian(ax):
    u = np.linspace(0, 2*np.pi, 100)
    x = np.sin(u)
    y = np.zeros(np.size(u))
    z = np.cos(u)
    ax.plot(x, y, z, color='blue', linestyle='dashed')
    # x= np.zeros(np.size(u))
    # y= np.sin(u)
    # z= np.cos(u)
    # ax.plot(x, y, z, color='blue', linestyle='dashed')

def add_labels(ax):
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    return

def remove_arrows(arrows):
    for arrow in arrows:
        arrow.remove()
    return

#Creat an animation of an arrow rotating on a sphere
def move_arrows_on_sphere(ax,thetas_0, phis_0, thetas_f, phis_f,time=5,nb_frame=100):
    k=len(thetas_0)
    assert len(phis_0)==k
    assert len(thetas_f)==k
    assert len(phis_f)==k
    arrows=[]
    for i in range(k):
        arrows.append(plot_arrow(ax, thetas_0[i], phis_0[i]))
    for i in range(1,nb_frame+1):
        for j in range(k):
            arrows[j].remove()
            arrows[j]=plot_arrow(ax, thetas_0[j]+i*(thetas_f[j]-thetas_0[j])/nb_frame, phis_0[j]+i*(phis_f[j]-phis_0[j])/nb_frame)
        plt.pause(time/nb_frame)
    return arrows

def move_arrows_pulses(ax,thetas_0, phis_0, pulse_ax, pulse_length, time=5,nb_frame=100):
    k=len(thetas_0)
    assert len(phis_0)==k
    assert len(pulse_length)==k
    arrows=[]
    for i in range(k):
        arrows.append(plot_arrow(ax, thetas_0[i], phis_0[i]))
    thetas_in=thetas_0
    phis_in=phis_0
    thetas_out=thetas_0
    phis_out=phis_0
    if pulse_ax=='x':
        pulse_func=pulse_3d_x
    elif pulse_ax=='y':
        pulse_func=pulse_3d_y
    elif pulse_ax=='z':
        pulse_func=pulse_3d_z

    for i in range(1,nb_frame+1):
        for j in range(k):
            arrows[j].remove()
            thetas_out[j], phis_out[j]=pulse_func(thetas_in[j], phis_in[j], pulse_length[j]/nb_frame)
            arrows[j]=plot_arrow(ax, thetas_out[j], phis_out[j])
        thetas_in=thetas_out
        phis_in=phis_out
        plt.pause(time/nb_frame)
    return arrows, thetas_out, phis_out

def pulse_3d_x(theta,phi,pulse_length):
    Vin=np.array([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)])
    Rot=np.array([[1,0,0],[0,np.cos(pulse_length),-np.sin(pulse_length)],[0,np.sin(pulse_length),np.cos(pulse_length)]])
    Vout=np.dot(Rot,Vin)
    Vout_theta=np.arccos(Vout[2])
    Vout_phi=np.arctan2(Vout[1],Vout[0])
    return Vout_theta, Vout_phi

def pulse_3d_y(theta,phi,pulse_length):
    Vin=np.array([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)])
    Rot=np.array([[np.cos(pulse_length),0,np.sin(pulse_length)],[0,1,0],[-np.sin(pulse_length),0,np.cos(pulse_length)]])
    Vout=np.dot(Rot,Vin)
    Vout_theta=np.arccos(Vout[2])
    Vout_phi=np.arctan2(Vout[1],Vout[0])
    return Vout_theta, Vout_phi

def pulse_3d_z(theta,phi,pulse_length):
    Vin=np.array([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)])
    Rot=np.array([[np.cos(pulse_length),-np.sin(pulse_length),0],[np.sin(pulse_length),np.cos(pulse_length),0],[0,0,1]])
    Vout=np.dot(Rot,Vin)
    Vout_theta=np.arccos(Vout[2])
    Vout_phi=np.arctan2(Vout[1],Vout[0])
    return Vout_theta, Vout_phi

def average_arrows(thetas, phis):
    x=0
    y=0
    z=0
    for i in range(len(thetas)):
        x+=np.sin(thetas[i])*np.cos(phis[i])
        y+=np.sin(thetas[i])*np.sin(phis[i])
        z+=np.cos(thetas[i])
    x=x/len(thetas)
    y=y/len(thetas)
    z=z/len(thetas)
    return [x,y,z]

def Ramsey_1spin(delta=-0.2, free_evolution_time=4):
    plt.ion()
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')  
    plot_sphere(ax)
    plot_equator(ax)
    add_labels(ax)

    plt.title("Ramsey sequence")
    thetas_in=[0]
    phis_in=[0]
    arrows=[plot_arrow(ax, 0, 0)]
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=[np.pi/2]
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("Free evolution")
    remove_arrows(arrows)
    t=free_evolution_time
    pulses=[delta*t]
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', pulses, time=t, nb_frame=t*10)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=[np.pi/2]
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")
    
# Ramsey_1spin(delta=-0.2)

def Ramsey_nSpins(n=10,deltaMax=0.3, free_evolution_time=4):
    plt.ion()
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')  
    plot_sphere(ax)
    plot_equator(ax)
    add_labels(ax)

    plt.title("Ramsey sequence")
    thetas_in=np.zeros(n)
    phis_in=np.zeros(n)
    arrows=[]
    for i in range(n):
        arrows.append(plot_arrow(ax, 0, 0))
    deltas=(np.random.rand(n)*2-1)*deltaMax
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("Free evolution")
    remove_arrows(arrows)
    t=free_evolution_time
    pulses=deltas*t
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', pulses, time=t, nb_frame=t*10)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("Average")
    remove_arrows(arrows)
    average=average_arrows(thetas_out, phis_out)
    ax.quiver(0, 0, 0, average[0], average[1], average[2], color='green', arrow_length_ratio=0.1)
    input("Press Enter to continue...")


# Ramsey_nSpins(n=10,deltaMax=0.3, free_evolution_time=3)

def echo_1spin(delta=-0.2, free_evolution_time=4):
    plt.ion()
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')  
    plot_sphere(ax)
    plot_equator(ax)
    add_labels(ax)

    plt.title("Spin echo sequence")
    thetas_in=[0]
    phis_in=[0]
    arrows=[plot_arrow(ax, 0, 0)]
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=[np.pi/2]
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("Free evolution")
    remove_arrows(arrows)
    t=free_evolution_time
    pulses=[delta*t]
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', pulses, time=t, nb_frame=t*10)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi pulse (y)")
    remove_arrows(arrows)
    pulses=[np.pi]
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("Free evolution")
    remove_arrows(arrows)
    t=free_evolution_time
    pulses=[delta*t]
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', pulses, time=t, nb_frame=t*10)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=[np.pi/2]
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

# echo_1spin(delta=-0.2)

def echo_nSpins(n=10,deltaMax=0.3, free_evolution_time=4):
    plt.ion()
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')  
    plot_sphere(ax)
    plot_equator(ax)
    add_labels(ax)

    plt.title("Spin echo sequence")
    thetas_in=np.zeros(n)
    phis_in=np.zeros(n)
    arrows=[]
    for i in range(n):
        arrows.append(plot_arrow(ax, 0, 0))
    deltas=(np.random.rand(n)*2-1)*deltaMax
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("Free evolution")
    remove_arrows(arrows)
    t=free_evolution_time
    pulses=deltas*t
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', pulses, time=t, nb_frame=t*10)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("Free evolution")
    remove_arrows(arrows)
    t=free_evolution_time
    pulses=deltas*t
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', pulses, time=t, nb_frame=t*10)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

# echo_nSpins(n=10,deltaMax=0.3, free_evolution_time=4)

def echo_n_spins_noisy(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.01):
    plt.ion()
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')  
    plot_sphere(ax)
    plot_equator(ax)
    add_labels(ax)

    plt.title("Spin echo sequence")
    thetas_in=np.zeros(n)
    phis_in=np.zeros(n)
    arrows=[]
    for i in range(n):
        arrows.append(plot_arrow(ax, 0, 0))
    deltas=(np.random.rand(n)*2-1)*deltaMax
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("Free evolution") 
    t=free_evolution_time
    for i in range(t*10):
        remove_arrows(arrows)
        change=np.random.random(n)<pchange
        for k in range(n):
            if change[k]:
                deltas[k]=(np.random.rand()*2-1)*deltaMax
        arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', deltas/10, time=1/10, nb_frame=1)
        thetas_in=thetas_out
        phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("Free evolution") 
    t=free_evolution_time
    for i in range(t*10):
        remove_arrows(arrows)
        change=np.random.random(n)<pchange
        for k in range(n):
            if change[k]:
                deltas[k]=(np.random.rand()*2-1)*deltaMax
        arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', deltas/10, time=1/10, nb_frame=1)
        thetas_in=thetas_out
        phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

# echo_n_spins_noisy(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.02)

def CP_nSpins(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.01, nPulses=4):
    plt.ion()
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')  
    plot_sphere(ax)
    plot_equator(ax)
    add_labels(ax)

    plt.title("CP sequence")
    thetas_in=np.zeros(n)
    phis_in=np.zeros(n)
    arrows=[]
    for i in range(n):
        arrows.append(plot_arrow(ax, 0, 0))
    deltas=(np.random.rand(n)*2-1)*deltaMax
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    for j in range(nPulses):
        plt.title("Free evolution") 
        t=free_evolution_time/(2*nPulses)
        for i in range(int(t*10)):
            remove_arrows(arrows)
            change=np.random.random(n)<pchange
            for k in range(n):
                if change[k]:
                    deltas[k]=(np.random.rand()*2-1)*deltaMax
            arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', deltas/10, time=1/10, nb_frame=1)
            thetas_in=thetas_out
            phis_in=phis_out

        plt.title("pi pulse (y)")
        remove_arrows(arrows)
        pulses=np.pi*np.ones(n)
        arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
        thetas_in=thetas_out
        phis_in=phis_out

        plt.title("Free evolution") 
        t=free_evolution_time/(2*nPulses)
        for i in range(int(t*10)):
            remove_arrows(arrows)
            change=np.random.random(n)<pchange
            for k in range(n):
                if change[k]:
                    deltas[k]=(np.random.rand()*2-1)*deltaMax
            arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', deltas/10, time=1/10, nb_frame=1)
            thetas_in=thetas_out
            phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

# CP_nSpins(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.03, nPulses=4)

def CP_nSpins_imperfect(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.01, nPulses=4, extra_pulse=0.3):
    plt.ion()
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')  
    plot_sphere(ax)
    plot_equator(ax)
    add_labels(ax)

    plt.title("CP sequence")
    thetas_in=np.zeros(n)
    phis_in=np.zeros(n)
    arrows=[]
    for i in range(n):
        arrows.append(plot_arrow(ax, 0, 0))
    deltas=(np.random.rand(n)*2-1)*deltaMax
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    for j in range(nPulses):
        plt.title("Free evolution 1") 
        t=free_evolution_time/(nPulses)
        for i in range(int(t*10)):
            remove_arrows(arrows)
            change=np.random.random(n)<pchange
            for k in range(n):
                if change[k]:
                    deltas[k]=(np.random.rand()*2-1)*deltaMax
            arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', deltas/10, time=1/10, nb_frame=1)
            thetas_in=thetas_out
            phis_in=phis_out

        plt.title("pi pulse (y)")
        remove_arrows(arrows)
        pulses=(np.pi+extra_pulse)*np.ones(n)
        arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
        thetas_in=thetas_out
        phis_in=phis_out

        plt.title("Free evolution 2") 
        t=free_evolution_time/(nPulses)
        for i in range(int(t*10)):
            remove_arrows(arrows)
            change=np.random.random(n)<pchange
            for k in range(n):
                if change[k]:
                    deltas[k]=(np.random.rand()*2-1)*deltaMax
            arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', deltas/10, time=1/10, nb_frame=1)
            thetas_in=thetas_out
            phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

# CP_nSpins_imperfect(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.03, nPulses=4, extra_pulse=0.1)

def CPMG_nSpins(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.01, nPulses=4, extra_pulse=0.3):
    plt.ion()
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')  
    plot_sphere(ax)
    plot_equator(ax)
    add_labels(ax)

    plt.title("CPMG sequence")
    thetas_in=np.zeros(n)
    phis_in=np.zeros(n)
    arrows=[]
    for i in range(n):
        arrows.append(plot_arrow(ax, 0, 0))
    deltas=(np.random.rand(n)*2-1)*deltaMax
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    for j in range(nPulses):
        plt.title("Free evolution 1") 
        t=free_evolution_time/(nPulses)
        for i in range(int(t*10)):
            remove_arrows(arrows)
            change=np.random.random(n)<pchange
            for k in range(n):
                if change[k]:
                    deltas[k]=(np.random.rand()*2-1)*deltaMax
            arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', deltas/10, time=1/10, nb_frame=1)
            thetas_in=thetas_out
            phis_in=phis_out

        plt.title("pi pulse (x)")
        remove_arrows(arrows)
        pulses=(np.pi+extra_pulse)*np.ones(n)
        arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'x', pulses, time=1, nb_frame=20)
        thetas_in=thetas_out
        phis_in=phis_out

        plt.title("Free evolution 2") 
        t=free_evolution_time/(nPulses)
        for i in range(int(t*10)):
            remove_arrows(arrows)
            change=np.random.random(n)<pchange
            for k in range(n):
                if change[k]:
                    deltas[k]=(np.random.rand()*2-1)*deltaMax
            arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', deltas/10, time=1/10, nb_frame=1)
            thetas_in=thetas_out
            phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

# CPMG_nSpins(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.02, nPulses=4, extra_pulse=0.1)

def Ramsey_MRI(n=10, deltaMax=0.3, free_evolution_time=4, pchange=0):
    plt.ion()
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')  
    plot_sphere(ax)
    plot_equator(ax)
    add_labels(ax)

    plt.title("Ramsey sequence")
    thetas_in=np.zeros(n)
    phis_in=np.zeros(n)
    arrows=[]
    for i in range(n):
        arrows.append(plot_arrow(ax, 0, 0))
    deltas=(np.random.rand(n)*2-1)*deltaMax
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("Free evolution 1") 
    t=free_evolution_time
    for i in range(int(t*10)):
        remove_arrows(arrows)
        change=np.random.random(n)<pchange
        for k in range(n):
            if change[k]:
                deltas[k]=(np.random.rand()*2-1)*deltaMax
        arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'z', deltas/10, time=1/10, nb_frame=1)
        thetas_in=thetas_out
        phis_in=phis_out
    input("Press Enter to continue...")

    plt.title("pi/2 pulse (y)")
    remove_arrows(arrows)
    pulses=np.pi/2*np.ones(n)
    arrows,thetas_out, phis_out=move_arrows_pulses(ax, thetas_in, phis_in, 'y', pulses, time=1, nb_frame=20)
    thetas_in=thetas_out
    phis_in=phis_out
    input("Press Enter to continue...")


if __name__ == '__main__':
    # Ramsey_1spin(delta=0, free_evolution_time=1)
    # Ramsey_1spin(delta=-0.2, free_evolution_time=4)
    # Ramsey_nSpins(n=10,deltaMax=0.3, free_evolution_time=4)
    # echo_1spin(delta=-0.2)
    echo_nSpins(n=10,deltaMax=0.3, free_evolution_time=4)
    # echo_n_spins_noisy(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.0125)
    # CP_nSpins(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.0125, nPulses=4)
    # CP_nSpins_imperfect(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.0125, nPulses=4, extra_pulse=0.1)
    # CPMG_nSpins(n=10,deltaMax=0.3, free_evolution_time=4, pchange=0.0125, nPulses=4, extra_pulse=0.1)

    #MRI bones
    # Ramsey_MRI(n=10, deltaMax=0.3, free_evolution_time=4, pchange=0)

    #MRI liquids
    # Ramsey_MRI(n=10, deltaMax=0.3, free_evolution_time=4, pchange=1)