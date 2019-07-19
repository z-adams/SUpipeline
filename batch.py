from pipeline import (
        run_pipeline,
        build_parameters,
        build_options, 
        default_parameters,
        default_options)
import os
from argparse import ArgumentParser
import logging

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
                params['NUM_PARTICLES'] = 100
                params['BEAM_ENERGY'] = E
                params['GEOMETRY'] = GEO
                params['PEN_MATERIALS'] = MAT
                configurations.append(
                        {'name': "{0}_{1:d}keV_{2:d}um".format(MAT['name'],
                            int(E/1000), 
                            int(GEO['layers'][1][1]*1000)),
                         'parameters': params,
                         'options': options
                         })
    return configurations

def main():

    configurations = dianas_sweep() # your generator function here
    scripts = ["../../../{}".format(s) for s in SCRIPTS]

    for config in configurations:
        logger.info("###################### Running pipeline config '%s' "\
                "######################", config['name'])
        logger.debug("Producing directory '%s'", config['name'])
        os.mkdir(config['name'])
        os.chdir(config['name'])
        logger.debug("CWD: %s", os.getcwd())
        run_pipeline(config['parameters'], config['options'], scripts=scripts)
        os.chdir('../..')

if __name__ == '__main__':
    #main()
    configs = dianas_sweep()
    for config in configs:
        print config['name']
