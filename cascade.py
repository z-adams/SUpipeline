import imp
import os
import sys
import numpy as np
import logging

from batch import run_batch
from pipeline import default_options, default_parameters
from traj_parser import parse_traj, separate_collisions

logger = logging.getLogger(os.path.basename(__file__))

#fp, pathname, description = imp.find_module(SUPIPELINE_LOCATION + "batch")
#batch = imp.load_module("batch", fp, pathname, description)

def cascade_tracks():
    BEAM_ENERGIES = [1e3, 10e3, 100e3]
    MATERIALS = [{'name': 'Diamond',
                  'density': 3.51,
                  'elements': [('C', 1.0,)]},
                 {'name': 'Ce:YAG',  # approximately YAG
                  'density': 4.56,
                  'elements': [('Y', 0.449,), ('Al', 0.227,), ('O', 0.324,)]},
                 {'name': 'PbBiGa',  # weird, potentially dubious simulation
                  'density': 8.2,
                  'elements': [('Pb', 0.210,), ('Bi', 0.184,),
                      ('Ga', 0.132,), ('O', 0.474,)]},
                 {'name': 'CdS',
                  'density': 4.821,
                  'elements': [('Cd', 0.778,), ('S', 0.222)]},
                 {'name': 'CdSe',
                  'density': 5.82,
                  'elements': [('Cd', 0.587,), ('Se', 0.413,)]},
                 {'name': 'CdTe',
                  'density': 5.85,
                  'elements': [('Cd', 0.468,), ('Te', 0.532)]},
                  ]
    configurations = []
    options = default_options()
    options['RUN_LUMERICAL'] = False
    options['WRITE_CHARGE_MAT'] = False
    options['RUN_MANUAL_CHARGE'] = False
    for MAT in MATERIALS:
        GEO = {'type': 0, 'material': MAT['name']}
        for E in BEAM_ENERGIES:
            logger.info("Generating for E:%s, MAT:%s", E, MAT)
            params = default_parameters()
            params['NUM_PARTICLES'] = 10
            params['PARTICLE'] = 2  # photon
            params['INCLUDE_SECONDARIES'] = True
            params['BEAM_ENERGY'] = E
            params['GEOMETRY'] = GEO
            params['PEN_MATERIALS'] = [MAT]
            configurations.append(
                    {'name': "{0}_{1:d}keV".format(MAT['name'], int(E/1000)),
                     'parameters': params,
                     'options': options
                     })
    return configurations

def cascade_time(trajectory):
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
    delta_t = delta_X / v

    return np.sum(delta_t)

def build_line_format(columns):
    line_format = ""
    for i in range(len(output)):
        line_format += "{}"
        if i == len(output) - 1:
            line_format += "\n"
        else:
            line_format += "\t"
    return line_format

def write_column_data_to_file(columns, filename):
    """ Writes a list of lists to a file as columns
        Expects a square list of dictionaries containing:
        {'title': xxx, 'data': [list]}
    """
    with open(filename, 'w+') as f:
        num_columns = len(columns)
        num_rows = len(columns[0]['data'])
        # Write column headers
        for i, elem in enumerate(columns):
            f.write(elem['name'])
            if i < num_columns - 1:
                f.write("\t")
            else:
                f.write("\n")
        
        for i in range(num_rows):
            for c, elem in enumerate(columns):
                f.write(str(elem['data'][i]))
                if c < num_columns - 1:
                    f.write("\t")
                else:
                    f.write("\n")


def compute_times():
    time_output = []
    depths_of_absorption = []
    configs = cascade_tracks()
    run_batch(cascade_tracks)
    folders = os.listdir('.')
    #for folder in folders:
    for config in configs:
        folder = config['name']
        os.chdir("{}/pyPENELOPE".format(folder))
        trajectories = parse_traj("pe-trajectories.dat")
        showers = separate_collisions(trajectories)

        cascade_maxs = []
        absorption_depths = []
        for shower in showers:
            tmp_times = []
            tmp_depth = -1
            for traj in shower:
                tmp_times.append(cascade_time(traj))
                if traj.kpar == 2:
                    try:
                        tmp_depth = next(
                            evt['z'] for evt in traj.events if evt['ICOL'] == 3)
                    except:
                        tmp_depth = -1
            cascade_maxs.append(max(tmp_times))
            absorption_depths.append(tmp_depth)
        time_output.append({'name': folder, 'data': cascade_maxs})  #TODO HACK
        depths_of_absorption.append({'name': folder, 'data': absorption_depths})
        os.chdir('../../')

    write_column_data_to_file(time_output, "time_output.txt")
    write_column_data_to_file(depths_of_absorption, "depths.txt")
if __name__ == '__main__':
    compute_times()

