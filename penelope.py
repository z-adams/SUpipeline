# In the future, may want to have config files to generalize 
# http://pypenelope.sourceforge.net/code/penelopetools/api/input/penelope/description.html

from penelopetools.api.input.penelope.description import Description
from penelopetools.api.input.penelope.particle import ELECTRON
from penelopetools.api.program.shower import Shower2010
from penelopetools.api.input.penelope.materials import *
from penelopetools.api.input.shower2010.io import InputFile
from penelopetools.api.input.shower2010.source import Source
from penelopetools.api.input.shower2010.jobproperties import Simulation
from penelopetools.api.input.shower2010.options import Options


### Microscope ("source")
src = Source(particle=ELECTRON, beam_energy=350e3) # rest of params are defaults

### Geometry
# Select geometry (substrate)

# Create and select material
Cd = Element('Cd')
Te = Element('Te')

elems = Elements()
# elems.add(symbol, fraction=1.0)
# elems.add_element(element)
elems.add('Cd', fraction=0.5)
elems.add('Te', fraction=0.5)
elems.userdensity = 5.85
# penelopetools.api.input.penelope.materials.SimulationParamters

# Parameters:
#sim = SimulationParameters()
# absorption of e-, e+, phot
#sim.absorption_energy_electron(50)
#sim.absorption_energy_photon(50)
#sim.absorption_energy_positron(50)

# elastic scattering parameters C1, C2
#sim.elastic_scattering_paramters_c1(0.1)
#sim.elastic_scattering_paramters_c2(0.1)

# cutoff energy loss
#sim.cutoff_energyloss_inelasticcollisions(50)
#sim.cutoff_energyloss_bremsstrahlungemission(50)

# can get xml/in config files
#sim.to_inputfile()
#sim.to_xml()

params = SimulationParameters()  # defaults (e.g. e- energy=50), not "use default"

mat = Material(name="CdTe", filename="CdTe.mat", elements=elems, simulation_parameters=params)

mats = Materials()
mats.add(mat, userid=None)

### Geometry
#geom = Geometry(title='example')

### Simulation
sim = Simulation(randomnumberseeds=None, secondary_particles=True, trajectories=10)

### Trajectories

opt = Options()
opt.description = Description(title='example')
opt.source = src
opt.materials = mats
#opt.geometry = defaults to substrate
opt.simulation = sim

io = InputFile()

with open('test.in', 'w') as f:
    io.write(f, opt)

#sim = Shower2010()
#runner = program.get_runner()
