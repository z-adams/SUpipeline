# In the future, may want to have config files to generalize 
# http://pypenelope.sourceforge.net/code/penelopetools/api/input/penelope/description.html

from penelopetools.api.input.penelope.description import Description
from penelopetools.api.input.penelope.particle import ELECTRON
from penelopetools.api.input.penelope.io import XMLFile
from penelopetools.api.runner.shower import Shower2010
from penelopetools.api.input.penelope.materials import *
from penelopetools.api.input.pengeom.usergeometry.substrate import Substrate
from penelopetools.api.input.pengeom.usergeometry.multilayers import *
from penelopetools.api.input.shower2010.source import Source
from penelopetools.api.input.shower2010.jobproperties import Simulation
from penelopetools.api.input.shower2010.options import Options
from penelopetools.gui.util import get_config

import logging
import os

logger = logging.getLogger(os.path.basename(__file__))

def run_penelope(num_particles=10, beam_energy=350e3, 
        materials=None, geometry=None, energy_parameters=None):
    """ Calls the penelope API to perform a PENELOPE simulation of electrons
    incidents on the specified geometry.
    
    If materials OR geomtry are None, a CdTe substrate wil be used

    args:
    num_particles -- the number of primary particles to simulate
    beam_energy -- the energy of the primary particles
    materials -- list of materials to be used in the simulation
    geometry -- geometry definition for simulation
    energy_parameters -- dict containing energy parameters for the materials

    For detailed datatype formats, see their respective sections below
    In general, materials and geometries are described by dicts containing
    their parameters. Material names are used to instruct geometry which
    material to use, and material IDs are handled internally, hidden from
    the user (see below).

    returns nothing
    """
    logger.debug("Running PENELOPE with parameters: num_particles=%d, " \
        "beam_energy=%e, materials=%s, geometry=%s, energy_parameters=%s", 
        num_particles, beam_energy, materials, geometry, energy_parameters)

    # material IDs are hidden from the user, they are instead referenced by name
    # IDs are internally assigned and the name <-> ID relationship is 
    # stored in the mat_id_pairs dictionary.
    next_mat_id = 1  # 0 is reserved for vacuum
    mat_id_pairs = {'vacuum': 0}

    def get_mat_id(name):
        return mat_id_pairs[name.lower()]

    ### Microscope ("source")
    src = Source(particle=ELECTRON, beam_energy=beam_energy)

    ### Materials

    # The materials are described using the following dictionary:
    # 'elements' is a list of tuples containing the chemical symbol of the
    # element and its mass fraction in the material

    # material = {
    #   'name': 'AbCd', 
    #   'density': density,
    #   'elements': [('Ab', fraction,), ('Cd', fraction,)...]
    #   }

    # Energy Parameters: (equivalent to "use default simulation parameters")
    if energy_parameters is None:
        energy_parameters = {
                'absorption_energy_electron': beam_energy * 0.01,
                'absorption_energy_photon': beam_energy * 0.001,
                'absorption_energy_positron': beam_energy * 0.01,
                'elastic_scattering_parameter_c1': 0.2,
                'elastic_scattering_parameter_c2': 0.2,
                'cutoff_energyloss_inelasticcollisions': beam_energy * 0.01,
                'cutoff_energyloss_bremsstrahlungemission': beam_energy * 0.001 
                }
    params = SimulationParameters(**energy_parameters)

    # Default setup (CdTe substrate):
    if materials is None or geometry is None:
        logger.info("Auto-configuring material and geometry")
        materials = [
                {'name': 'CdTe', 'density': 5.85, 
                    'elements': [('Cd', 0.5), ('Te', 0.5)]}
                ]
        geometry = {'type': 0, 'material': 'CdTe'}


    mats = Materials()
    for material in materials:
        logger.debug("Processing material '%s'", material['name'])
        elems = Elements()
        elems.userdensity = material['density']
        for element in material['elements']:
            elems.add(element[0], fraction=element[1])
        filename = "{}.mat".format(material['name'])
        mat = Material(name=material['name'], filename=filename, elements=elems,
                simulation_parameters=params)
        mats.add(mat, userid=next_mat_id)
        mat_id_pairs[material['name'].lower()] = next_mat_id 
        next_mat_id += 1
        
    ### Geometry

    # TODO design decisions: multiple dict formats or not?
    # The geometry argument can take on a variety of dictionary formats,
    # different geometries have their own formats (yay/oh-god for duck typing)
    # They share the 'type' attribute which corresponds to the geometry type
    # (only 2 currently implemented):
    # 0 - Substrate
    # 1 - multi-layer
    # Since material IDs are hidden from the caller, materials are referenced
    # by name (the same name used when it was defined; case-insensitive)

    # substrate = {
    #   'type': 0,
    #   'material': 'AbCd'
    #   }

    ## thickness is in meters
    ## first layer is the substrate, usually ('vacuum', -1) (infinite vacuum)
    # multilayer = {
    #   'type': 1,
    #   'layers': [(material, thickness,), ...]
    #   }

    if geometry['type'] == 0:  # substrate
        logger.debug("Geometry is type: substrate")
        mat_id = get_mat_id(geometry['material'])
        geom = Substrate(substrate_material_id=mat_id)

    elif geometry['type'] == 1:  # multi-layer
        logger.debug("Geometry is type: multi-layer")
        mat_id = get_mat_id(geometry['layers'][0][0])
        geom = MultiLayers(substrate_material_id=mat_id)
        for layer in geometry['layers'][1:]:  # skip substrate
            logger.debug("Adding layer '%s'", layer)
            mat_id = get_mat_id(layer[0])
            geom.layers.append(Layer(thickness=layer[1], material_id=mat_id))
    else:
        logger.warning("Unrecognized geometry type index")
        raise IndexError


    ### Simulation
    sim = Simulation(randomnumberseeds=None, secondary_particles=True, 
            trajectories=num_particles)

    ### Trajectories

    opt = Options()
    opt.description = Description(title='sim')
    opt.source = src
    opt.materials = mats
    opt.simulation = sim
    opt.geometry = geom

    with open('sim.xml', 'w') as f:
        logger.debug("Writing .xml config file")
        XMLFile().write(f, opt)

    CONFIG = get_config()
    shwr = Shower2010(CONFIG, options=opt)
    logger.info("#### Beginning shower sim (PENELOPE logs to follow) ####")
    shwr.start()
    logger.info("#### Shower sim complete ####")

if __name__ == '__main__':
    run_penelope()
