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

class MarchJob:
    def __init__(self):
        self.resolution = 1
        self.clouds = []

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

def subdivide_workload(global_mins, global_maxs, output_dimensions, resolution,
        direction, matrix, volumes, u_divisions, v_divisions):

    march_dist = global_maxs[2] - global_mins[2]
    mat_cell_u = output_dimensions[0] / int(u_divisions)
    mat_cell_v = output_dimensions[1] / int(v_divisions)
    sweep_cell_u = (global_maxs[0] - global_mins[0]) / int(u_divisions)
    sweep_cell_v = (global_maxs[1] - global_mins[1]) / int(v_divisions)

    args = []

    for u in range(u_divisions):
        for v in range(v_divisions):
            u0 = global_mins[0] + sweep_cell_u * u
            v0 = global_mins[1] + sweep_cell_v * v
            mat_u0 = mat_cell_u * u
            mat_v0 = mat_cell_v * v

            if u == u_divisions - 1:
                u1 = global_maxs[0]
                mat_u1 = output_dimensions[0]
            else:
                u1 = u0 + sweep_cell_u
                mat_u1 = mat_u0 + mat_cell_u

            if v == v_divisions - 1:
                v1 = global_maxs[1]
                mat_v1 = output_dimensions[1]
            else:
                v1 = v0 + sweep_cell_v
                mat_v1 = mat_v0 + mat_cell_v



            arg_list = ((u0, v0,), (u1, v1,), (mat_u0, mat_v0,),
                    #(mat_u_1, mat_v_1,),
                    matrix, volumes, global_maxs[2],
                    direction, march_dist, resolution)
            args.append(arg_list)
        """
        u_0 = global_mins[0] + sweep_cell_u * u
        v_0 = global_mins[1] + sweep_cell_v * (v_divisions - 1)
        u_1 = u_0 + sweep_cell_u
        v_1 = global_maxs[1]
        mat_u0 = mat_cell_u * u
        mat_v0 = mat_cell_v * (v_divisions - 1)
        mat_u1 = mat_u_0 + mat_cell_u
        mat_v1 = output_dimensions[1]
        args.append(((u_0, v_0,), (u_1, v_1,), (mat_u0, mat_v0,), matrix,
            volumes, global_maxs[2], direction, march_dist, resolution))

    final_u0 = global_mins[0] + sweep_cell_u * (u_divisions - 1)
    final_v0 = global_mins[1] + sweep_cell_v * (v_divisions - 1)
    final_u1 = global_maxs[0]
    final_v1 = global_maxs[1]
    final_mat_u0 = mat_cell_u * (u_divisions - 1)
    final_mat_v0 = mat_cell_v * (v_divisions - 1)
    final_mat_u1 = output_dimensions[0]
    final_mat_v1 = output_dimensions[1]
    args.append(((final_u0, final_v0,), (final_u1, final_v1,),
            (final_mat_u0, final_mat_v0,), #(final_mat_u1, final_mat_v1,),
            matrix, volumes, global_maxs[2], direction, march_dist,
            resolution))
    """
    return args

def march_subsection(uv_mins, uv_maxs, out_uv, out_matrix, volumes, origin_w,
        direction, max_depth, resolution):
    u = uv_mins[0]
    v = uv_mins[1]
    u_out = out_uv[0]
    while u < uv_maxs[0]:
        v_out = out_uv[1]
        v = uv_mins[1]
        while v < uv_maxs[1]:
            origin = Vec3(u, v, origin_w)
            out_matrix[u_out, v_out] = march(
                    origin, direction, volumes, max_depth, resolution)
            v += resolution
            v_out += 1
            if not v_out < out_matrix.shape[1]:
                break
        u += resolution
        u_out += 1
        if not u_out < out_matrix.shape[0]:
            break



def march_density(trajectory): #, direction):

    volumes = []
    compute_charge(trajectory, volumes)

    rmax = np.max([vol.r for vol in volumes])

    xmin = np.min([vol.x for vol in volumes])# - rmax
    xmax = np.max([vol.x for vol in volumes])# + rmax

    ymin = np.min([vol.y for vol in volumes])# - rmax
    ymax = np.max([vol.y for vol in volumes])# + rmax

    zmin = np.min([vol.z for vol in volumes])# - rmax
    zmax = np.max([vol.z for vol in volumes])# + rmax

    for vol in volumes:
        vol.r *= 1e3

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
    resolution = 1e-4

    x_steps = np.int_((xmax - xmin) / resolution)
    y_steps = np.int_((ymax - ymin) / resolution)
    matrix = np.zeros((x_steps, y_steps,))

    xmid = (xmax + xmin)/2
    ymid = (ymax + ymin)/2

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

    arg_list = subdivide_workload((xmin, ymin, zmin,), (xmax, ymax, zmax),
            (x_steps, y_steps,), resolution, direction, matrix, volumes, 3, 3)

    threads = []

    #threads.append(threading.Thread(target=march_subsection, args=args1))
    #threads.append(threading.Thread(target=march_subsection, args=args2))
    #threads.append(threading.Thread(target=march_subsection, args=args3))
    #threads.append(threading.Thread(target=march_subsection, args=args4))

    for a in arg_list:
        threads.append(threading.Thread(target=march_subsection, args=a))

    t_begin = time.time()
    for t in threads:
        t.start()

    #main_start = (xmin, ymin,)
    #main_stop = (xmax, ymax,)
    #mat_start = (0, 0,)
    #main_args = (main_start, main_stop, mat_start, matrix, volumes, zmax, direction, march_dist, resolution)

    #march_subsection(*arg_list[0])

    for t in threads:
        t.join()
    t_elapsed = time.time() - t_begin

    print "Finished marching after {} seconds".format(t_elapsed)
 
    return np.array(matrix)

if __name__ == '__main__':
    trajs = parse_traj("pe-trajectories.dat")
    mat = march_density(trajs[0])
    sio.savemat("data.mat", {'data': mat})
    plt.imshow(mat)
    plt.show()
