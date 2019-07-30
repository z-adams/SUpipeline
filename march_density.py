from charge_density import Sphere, compute_charge
from traj_parser import parse_traj
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
import threading
import time

class Vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def norm(self):
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def unit_vec(self):
        mag = self.norm()
        return Vec3(self.x/mag, self.y/mag, self.z/mag)

    def __mul__(self, scalar):
        return Vec3(self.x*scalar, self.y*scalar, self.z*scalar)

    def __add__(self, vec):
        return Vec3(self.x+vec.x, self.y+vec.y, self.z+vec.z)

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction.unit_vec()

    def get_point(self, distance):
        return self.origin + self.direction * distance

def test_volumes(volumes, point):
    total = 0
    for vol in volumes:
        if vol.SDF(point.x, point.y, point.z) < 0:
            total += 1
    return total

def march(origin, direction, volumes, max_depth, step_len):
    depth = 0
    total_charge = 0
    num_steps = 0
    ray = Ray(origin, direction)
    while depth < max_depth:
        depth += step_len
        num_steps += 1
        total_charge += test_volumes(volumes, ray.get_point(depth))
    return total_charge

def march_density(trajectory): #, direction):

    volumes = []
    compute_charge(trajectory, volumes)

    rmax = np.max([vol.r for vol in volumes])

    xmin = np.min([vol.x for vol in volumes]) - rmax
    xmax = np.max([vol.x for vol in volumes]) + rmax

    ymin = np.min([vol.y for vol in volumes]) - rmax
    ymax = np.max([vol.y for vol in volumes]) + rmax

    zmin = np.min([vol.z for vol in volumes]) - rmax
    zmax = np.max([vol.z for vol in volumes]) + rmax

    #if direction == directions.X:
    #    pass
    #elif direction == directions.Y:
    #    pass
    #elif direction == directions.Z:
    #    pass
    #else:
    #    pass # error

    # March volume
    # units are in cm
    # Z proj
    direction = Vec3(0, 0, -1)
    resolution = 1e-3

    x_steps = np.int_((xmax - xmin) / resolution)
    y_steps = np.int_((ymax - ymin) / resolution)
    matrix = np.zeros((x_steps, y_steps,))

    xmid = (xmax - xmin)/2
    ymid = (ymax - ymin)/2

    march_dist = zmax - zmin

    """          (x_steps, y_steps)
         +---+---+
         | 2 | 1 |
         +---+---+
         | 3 | 4 |
         +---+---+
    (0,0)
    """
    
    start_1 = (xmid, ymid,)
    stop_1 = (xmax, ymax,)
    mat_start1 = (x_steps/2, y_steps/2,)
    args1 = (start_1, stop_1, mat_start1, matrix, volumes, zmax, direction, march_dist, resolution)

    start_2 = (xmin, ymid,)
    stop_2 = (xmid, ymax,)
    mat_start2 = (0, y_steps/2,)
    args2 = (start_2, stop_2, mat_start2, matrix, volumes, zmax, direction, march_dist, resolution)

    start_3 = (xmin, ymin,)
    stop_3 = (xmid, ymid,)
    mat_start3 = (0, 0,)
    args3 = (start_3, stop_3, mat_start3, matrix, volumes, zmax, direction, march_dist, resolution)

    start_4 = (xmid, ymin,)
    stop_4 = (xmax, ymid,)
    mat_start4 = (x_steps/2, 0,)
    args4 = (start_4, stop_4, mat_start4, matrix, volumes, zmax, direction, march_dist, resolution)

    threads = []
    threads.append(threading.Thread(target=march_subsection, args=args1))
    threads.append(threading.Thread(target=march_subsection, args=args2))
    threads.append(threading.Thread(target=march_subsection, args=args3))
    threads.append(threading.Thread(target=march_subsection, args=args4))

    t_begin = time.time()
    for t in threads:
        t.start()

    for t in threads:
        t.join()
    t_elapsed = time.time() - t_begin

    print "Finished marching after {} seconds".format(t_elapsed)
 
    return np.array(matrix)

def march_subsection(uv_mins, uv_maxs, out_uv, out_matrix, volumes, origin_w, direction, max_depth, resolution):
    u = uv_mins[0]
    v = uv_mins[1]
    u_out = out_uv[0]
    v_out = out_uv[1]
    while u < uv_maxs[0]:
        while v < uv_maxs[1]:
            origin = Vec3(u, v, origin_w)
            out_matrix[u_out, v_out] = march(origin, direction, volumes, max_depth, resolution)
            v += resolution
            v_out += 1
            if not v_out < out_matrix.shape[1]:
                break
        u += resolution
        u_out += 1
        if not u_out < out_matrix.shape[0]:
            break

if __name__ == '__main__':
    trajs = parse_traj("pe-trajectories.dat")
    mat = march_density(trajs[0])
    sio.savemat("data.mat", {'data': mat})
    plt.imshow(mat)
    plt.show()
