# In the future, may want to have config files to generalize 
# http://pypenelope.sourceforge.net/code/penelopetools/api/input/penelope/description.html

from penelopetools.api.input.penelope.description import Description
from penelopetools.api.input.penelope.particle import ELECTRON
from penelopetools.api.runner.shower import Shower2010
from penelopetools.api.input.penelope.materials import *
from penelopetools.api.input.pengeom.usergeometry.substrate import Substrate
from penelopetools.api.input.pengeom.usergeometry.multilayers import *
from penelopetools.api.input.shower2010.source import Source
from penelopetools.api.input.shower2010.jobproperties import Simulation
from penelopetools.api.input.shower2010.options import Options
from penelopetools.gui.util import get_config

def run_penelope(num_particles=10, beam_energy=350e3, 
        materials=None, geometry=None):
    """ Calls the penelope API to perform a PENELOPE simulation of electrons
    incidents on the specified geometry.
    
    If materials OR geomtry are None, a CdTe substrate wil be used

    args:
    num_particles -- the number of primary particles to simulate
    beam_energy -- the energy of the primary particles
    mats -- list of materials to be used in the simulation*
    geom -- geometry definition for simulation*

    * For argument datatype formats, see their respective sections below

    returns nothing
    """
    ### Microscope ("source")
    src = Source(particle=ELECTRON, beam_energy=beam_energy)

    ### Materials

    # The materials are described using the following dictionary:
    # 'elements' is a list of tuples containing the chemical symbol of the
    # element and its mass fraction in the material

    # material = {
    #   'name': 'AbCd', 
    #   'density': density,
    #   'id': id,
    #   'elements': [('Ab', fraction,), ('Cd', fraction,)...]
    #   }

    # Energy Parameters: (equivalent to "use default simulation parameters")
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
        materials = [
                {'name': 'CdTe', 'density': 5.85, 'id': 1, 
                    'elements': [('Cd', 0.5), ('Te', 0.5)]}
                ]
        geometry = {'type': 0, 'material_id': 1}


    mats = Materials()
    for material in materials:
        elems = Elements()
        elems.userdensity = material['density']
        for element in material['elements']:
            elems.add(element[0], fraction=element[1])
        filename = "{}.mat".format(material['name'])
        mat = Material(name=material['name'], filename=filename, elements=elems,
                simulation_parameters=params)
        mats.add(mat, userid=material['id'])
        
    ### Geometry

    # TODO design decisions: multiple dict formats or not?
    # The geometry argument can take on a variety of dictionary formats,
    # different geometries have their own formats (yay/oh-god for duck typing)
    # They share the 'type' attribute which corresponds to the geometry type
    # (only 2 currently implemented):
    # 0 - Substrate
    # 1 - multi-layer

    # substrate = {
    #   'type': 0,
    #   'material_id': i
    #   }

    ## thickness is in meters
    ## first layer is the substrate, usually (0, -1) (infinite vacuum)
    # multilayer = {
    #   'type': 1,
    #   'layers': [(mat_id, thickness,), ...]
    #   }

    if geometry['type'] == 0:  # substrate
        geom = Substrate(substrate_material_id=geometry['material_id'])

    elif geometry['type'] == 1:  # multi-layer
        geom = Multilayers(substrate_material_id=geometry['layers'][0])
        for layer in geometry['layers'][1:]:  # skip substrate
            geom.layers.append(Layer(thickness=layer[1], material_id=layer[0]))

    else:
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

    CONFIG = get_config() #"/home/zander/.pypenelope/pypenelope.cfg"
    shwr = Shower2010(CONFIG, options=opt)
    shwr.start()

if __name__ == '__main__':
    run_penelope()
