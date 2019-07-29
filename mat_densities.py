import scipy.io as sio
import numpy as np
import os
import re
import ast

def parse_file(my_file, name):
    densities = []
    with open(my_file, 'r') as f:
        f.readline()  # discard title
        options = f.readline()  # capture options
        params = f.readline()  # capture params
        f.readline()  # discard separation line
        f.readline()  # discard column headers
        for i, line in enumerate(f):
            d = re.search('([-+]?\d+\.\d+([eE]\+\d+))', line)
            if d:
                densities.append(float(d.group(0)))
    options = ast.literal_eval(options)
    params = ast.literal_eval(params)
    np_densities = np.array(densities)
    sio.savemat('{}.mat'.format(name),
            {'options': options, 'params': params, 'densities': densities})

if __name__ == '__main__':
    files = os.listdir('.')
    for my_file in files:
        name = re.search('(\w+)(?=.txt)', my_file)
        parse_file(my_file, name.group(0))
