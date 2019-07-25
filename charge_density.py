import numpy as np

max_N = 100
eh_gen = 4.43  # 3 * bandgap energy

def compute_charge(trajectory):
    """Produces the final charge density from a given trajectory"""
    charge_densities = []
    x = np.array([evt['x'] for evt in trajectory.events])
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

    ## Compute charge diffusion
    time_elapsed = np.zeros(num_points)
    radius = np.zeros(num_points)
    for i in range(num_points):
        time_elapsed[i] = np.sum(t[i:])
        radius[i] = np.sqrt(6 * 0.25 * time_elapsed[i])

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

