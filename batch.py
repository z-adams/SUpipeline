from pipeline import (
        run_pipeline,
        build_parameters,
        build_options, 
        default_parameters,
        default_options)
import os
from argparse import ArgumentParser
import logging
import multiprocessing
import time

### Logger setup, ignore me ###
arg_parser = ArgumentParser()
arg_parser.add_argument("--log", 
        help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
loglevel = arg_parser.parse_args().log
if loglevel is not None:
    numeric_level= getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level')
    logging.basicConfig(level=numeric_level)
logger = logging.getLogger(os.path.basename(__file__))
### stop ignoring ###

# Specify any scripts (located in batch root dir) to run
SCRIPTS = []

# Specify whether or not to use threading, and how many threads
USE_THREADING = True
NUM_THREADS = 24

# Do-it-yourself batch config: write a function that generates a list of
# configurations* to run through the pipeline
# *1 configuration: {'name': name, 'parameters': params, 'options': options}

# Here's an example (I use the default options and then just change energy)
def energy_sweep():
    BEAM_ENERGIES = [250e3, 300e3, 350e3, 400e3]
    configurations = []
    options = default_options()
    for E in BEAM_ENERGIES:
        logger.info("Generating configuration with beam energy %s", E)
        params = default_parameters()
        params['BEAM_ENERGY'] = E
        configurations.append(
                {'name': "{0:d}_eV".format(int(E)),
                 'parameters': params,
                 'options': options
                })
    return configurations

def dianas_sweep():
    MATERIALS = [{'name': 'CdTe', 
                  'density': 5.85,
                  'elements': [('Cd', 0.5), ('Te', 0.5)]},
                 {'name': 'YAG',
                  'density': 4.65,
                  'elements': [('Y', 0.449), ('Al', 0.227), ('O', 0.324)]},
                 {'name': 'BSO',
                  'density': 2.47968,
                  'elements': [('Bi', 0.752), ('O', 0.172), ('Si', 0.076)]},
                 {'name': 'BGO',
                  'density': 4.13281,
                  'elements': [('Bi', 0.671), ('Ge', 0.175), ('O', 0.154)]}
                 ]
    BEAM_ENERGIES = [350e3, 400e3, 450e3]
    THICKNESSES = [0.2, 0.4, 1.0, 1.5, 2.0]

    configurations = []
    options = default_options()
    options['RUN_LUMERICAL'] = False
    for MAT in MATERIALS:
        GEOMETRIES = [
                {'type': 1, 'layers': [('vacuum', -1), (MAT['name'], thickness)]}
                for thickness in THICKNESSES
                ]
        for E in BEAM_ENERGIES:
            for GEO in GEOMETRIES:
                logger.info("Generating for E:%s, GEO:%s, MAT:%s", E, GEO, MAT)
                params = default_parameters()
                params['NUM_PARTICLES'] = 1000
                params['BEAM_ENERGY'] = E
                params['GEOMETRY'] = GEO
                params['PEN_MATERIALS'] = [MAT]
                configurations.append(
                        {'name': "{0}_{1:d}keV_{2:d}um".format(MAT['name'],
                            int(E/1000), 
                            int(GEO['layers'][1][1]*1000)),
                         'parameters': params,
                         'options': options
                         })
    return configurations

def do_sim(config, scripts):
        logger.info("###################### Running pipeline config '%s' "\
                "######################", config['name'])
        logger.debug("Producing directory '%s'", config['name'])
        os.mkdir(config['name'])
        os.chdir(config['name'])
        logger.debug("CWD: %s", os.getcwd())
        run_pipeline(config['parameters'], config['options'], scripts=scripts)
        os.chdir('../..')

class MultiprocessingPool:
    def __init__(self, num_processes):
        self.capacity = num_processes
        self.num_active = 0
        self.processes = []
        self.running_total = 0

    def dispatch(self, poll_wait=1, tgt=None, arguments=()):
        while True:
            if self.num_active < self.capacity:
                logger.warn("Adding process %s, running total: %s", self.num_active, self.running_total)
                new_child = multiprocessing.Process(target=tgt, args=arguments)
                new_child.start()
                self.processes.append(new_child)
                self.num_active += 1
                self.running_total += 1
                return
            else:
                logger.warn("Polling processes")
                if poll_wait > 0:
                    time.sleep(poll_wait)
                self.poll_processes()

    def poll_processes(self):
        self.processes = [p for p in self.processes if p.is_alive() == True]
        self.num_active = len(self.processes)

    def join_all(self):
        for p in self.processes:
            p.join()


def main():

    configurations = dianas_sweep() # your generator function here
    scripts = ["../../../{}".format(s) for s in SCRIPTS]

    if USE_THREADING:
        pool = MultiprocessingPool(NUM_THREADS)
        for config in configurations:
            pool.dispatch(poll_wait=30, tgt=do_sim, arguments=(config,scripts,))
        pool.join_all()

    else:
        for config in configurations:
            do_sim(config, scripts)

if __name__ == '__main__':
    main()
    #configs = dianas_sweep()
    #for config in configs:
    #    print config['name']
