# In the future, may want to have config files to generalize 
# http://pypenelope.sourceforge.net/code/penelopetools/api/input/penelope/description.html

from penelopetools.api.input.penelope.description import Description
from penelopetools.api.input.penelope.particle import ELECTRON
from penelopetools.api.runner.shower import Shower2010
from penelopetools.api.input.penelope.materials import *
from penelopetools.api.input.pengeom.usergeometry.substrate import Substrate
from penelopetools.api.input.shower2010.io import InputFile
from penelopetools.api.input.shower2010.io import XMLFile
from penelopetools.api.input.shower2010.source import Source
from penelopetools.api.input.shower2010.jobproperties import Simulation
from penelopetools.api.input.shower2010.options import Options

BEAM_ENERGY=350e3 # 

### Microscope ("source")
src = Source(particle=ELECTRON, beam_energy=BEAM_ENERGY)

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
        'absorption_energy_electron': BEAM_ENERGY * 0.1,
        'absorption_energy_photon': BEAM_ENERGY * 0.01,
        'absorption_energy_positron': BEAM_ENERGY * 0.1,
        'elastic_scattering_parameter_c1': 0.2,
        'elastic_scattering_parameter_c2': 0.2,
        'cutoff_energyloss_inelasticcollisions': BEAM_ENERGY * 0.1,
        'cutoff_energyloss_bremsstrahlungemission': BEAM_ENERGY * 0.01 
        }
params = SimulationParameters(**energy_parameters)

mat = Material(name="CdTe", filename="CdTe.mat", elements=elems, simulation_parameters=params)

mats = Materials()
mats.add(mat, userid=1)

### Simulation
sim = Simulation(randomnumberseeds=None, secondary_particles=True, trajectories=10)

### Trajectories

opt = Options()
opt.description = Description(title='example')
opt.source = src
opt.materials = mats
opt.simulation = sim
opt.geometry = Substrate(substrate_material_id=1)

#io = InputFile()
x = XMLFile()

with open('test.xml', 'w') as f:
    x.write(f, opt)

CONFIG = "/home/zander/.pypenelope/pypenelope.cfg"
shwr = Shower2010(CONFIG, options=opt)
shwr.start()
