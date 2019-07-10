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
numeric_level= getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level')
logging.basicConfig(level=numeric_level)
logger = logging.getLogger(os.path.basename(__file__))
### stop ignoring ###

# Specify any scripts (located in batch root dir) to run
SCRIPTS = ["get_3D_n_matrix.lsf"]

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

def main():

    configurations = energy_sweep() # your generator function here
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
    main()
