# In the future, may want to have config files to generalize 
# http://pypenelope.sourceforge.net/code/penelopetools/api/input/penelope/description.html

from penelopetools.api.input.penelope.description import Description
from penelopetools.api.input.penelope.particle import ELECTRON
from penelopetools.api.runner.shower import Shower2010
from penelopetools.api.input.penelope.materials import *
from penelopetools.api.input.pengeom.usergeometry.substrate import Substrate
from penelopetools.api.input.shower2010.source import Source
from penelopetools.api.input.shower2010.jobproperties import Simulation
from penelopetools.api.input.shower2010.options import Options
from penelopetools.gui.util import get_config

def run_penelope(num_particles=10, beam_energy=350e3):
    """ Calls the penelope API to perform a PENELOPE simulation of electrons
    incidents on a CdTe substrate (will be later generalized)

    args:
    num_particles -- the number of primary particles to simulate
    beam_energy -- the energy of the primary particles

    returns nothing
    """
    ### Microscope ("source")
    src = Source(particle=ELECTRON, beam_energy=beam_energy)

    ### Materials

    # Create and select material
    Cd = Element('Cd')
    Te = Element('Te')

    elems = Elements()
    elems.add('Cd', fraction=0.5)
    elems.add('Te', fraction=0.5)
    elems.userdensity = 5.85

    # Parameters: (equivalent to "use default simulation parameters" checkbox
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

    mat = Material(name="CdTe", filename="CdTe.mat", elements=elems, 
            simulation_parameters=params)

    mats = Materials()
    mats.add(mat, userid=1)

    ### Simulation
    sim = Simulation(randomnumberseeds=None, secondary_particles=True, 
            trajectories=num_particles)

    ### Trajectories

    opt = Options()
    opt.description = Description(title='sim')
    opt.source = src
    opt.materials = mats
    opt.simulation = sim
    opt.geometry = Substrate(substrate_material_id=1)

    CONFIG = get_config() #"/home/zander/.pypenelope/pypenelope.cfg"
    shwr = Shower2010(CONFIG, options=opt)
    shwr.start()

if __name__ == '__main__':
    run_penelope()
