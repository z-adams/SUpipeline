import numpy as np
from copy import deepcopy

max_N = 100
eh_gen = 4.43  # 3 * bandgap energy [eV]
#eh_gen = 2.95

class Cloud:
    def __init__(self, x, y, z, r, N):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.N = N

    def SDF(self, x, y, z):
        return np.sqrt(
                (x - self.x)**2 + (y - self.y)**2 + (z - self.z)**2) - self.r

    def density(self):
        return self.N / (4.0/3.0 * 3.141592653 * self.r**3)

def compute_charge(trajectory, volumes = None):
    """Produces the final charge density from a given trajectory"""
    charge_densities = []
    x = np.array([evt['x'] for evt in trajectory.events])  # [cm]
    y = np.array([evt['y'] for evt in trajectory.events])
    z = np.array([evt['z'] for evt in trajectory.events])
    E = np.array([evt['E'] for evt in trajectory.events])

    delta_E = E[0:-1] - E[1:]
    
    x2 = (x[0:-1] - x[1:])**2
    y2 = (y[0:-1] - y[1:])**2
    z2 = (z[0:-1] - z[1:])**2

    delta_X = np.sqrt(x2 + y2 + z2)

    v = 3e10 * np.sqrt((E[0:-1] + 511e3)**2 - 511e3**2) / (511e3 + E[0:-1])
    t = delta_X / v

    delta_X *= 1e4 # m3 to um3
    dist = np.sum(delta_X)

    num_points = np.shape(x)[0] - 1

    # For CdTe
    mu_q = 1100 * 1e-4  # cm^2 / V*s  * (m^2 / 10^4 cm^2) = [m^2 / V*s]
    k_B = 1.38065e-23  # [m^2 kg s^-2 K^-1]
    T = 300  # [K]
    q = 1.602177e-19  # [C]
    D = 25 #(mu_q * k_B * T) / q  # diffusion coefficient [m^4 kg / V*C*s^2]

    ## Compute charge diffusion
    time_elapsed = np.zeros(num_points)
    radius = np.zeros(num_points)
    for i in range(num_points):
        time_elapsed[i] = np.sum(t[i:])
        radius[i] = np.sqrt(6 * 25 * time_elapsed[i])
        N = delta_E[i] / eh_gen
        if volumes is not None:
            volumes.append(Cloud(x[i]*1e-2, y[i]*1e-2, z[i]*1e-2, 0, N))  # to [m]
            volumes[i].r = np.sqrt(6*D*time_elapsed[i])  # [m]

    ## Calculate summed trajectory and volume
    sum_num = np.zeros(num_points)
    vol = np.zeros(num_points)
    sum_vol = np.zeros(num_points)
    total_density = np.zeros(num_points)
    sum_time = np.zeros(num_points)
    for i in range(num_points):
        # Issue
        sum_num[i] = np.sum(delta_E[0:i+1]) / eh_gen  # is that what this is?
        vol[i] = (4./3.)*np.pi*(radius[i]+5e-9)**3
        sum_vol[i] = np.sum(vol[0:i+1])
        total_density[i] = sum_num[i] / sum_vol[i]
        sum_time[i] = np.sum(t[0:i+1])

    # Get final density of each trajectory
    final_density = total_density[-1]

    return final_density

