# -*- coding: utf-8 -*-
#
#
# (c)  Baycrest Centre for Geriatric Care ("Baycrest"), 2012, all rights reserved.
#
# No redistribution, clinical use or commercial re-sale is permitted.
# Usage-license is only granted for personal or academic usage.
# You may change sources for your private or academic use.
# If you want to contribute to the project, you need to sign a contributor's license. 
# Please contact info@thevirtualbrain.org for further details.
# Neither the name of Baycrest nor the names of any TVB contributors may be used to endorse or 
# promote products or services derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY BAYCREST ''AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, 
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL BAYCREST BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS 
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY 
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
#
#

"""
Generate 8.125 seconds of 2048 Hz data at the surface level, stochastic integration.

``Run time``: approximately 5 hours (workstation circa 2010, MKL.)

``Memory requirement``: ~ 7 GB
``Storage requirement``: 2.1 GB

.. moduleauthor:: Stuart A. Knock <Stuart@tvb.invalid>

"""

# Third party python libraries
import numpy

"""
import tvb.core.logger.logger as logger
LOG = logger.getLogger(__name__)

#Import from tvb.simulator modules:
import tvb.simulator.simulator as simulator
import tvb.simulator.models as models
import tvb.simulator.coupling as coupling
import tvb.simulator.integrators as integrators
import tvb.simulator.noise as noise
import tvb.simulator.monitors as monitors

import tvb.basic.datatypes.connectivity as connectivity
import tvb.basic.datatypes.surfaces as surfaces
"""

from tvb.simulator.lab import *

##----------------------------------------------------------------------------##
##-                      Perform the simulation                              -##
##----------------------------------------------------------------------------##

#TODO: Configure this so it actually generates an interesting timeseries.
#      Start with a local_coupling that has a broader footprint than the default.

LOG.info("Configuring...")
#Initialise a Model, Coupling, and Connectivity.
oscilator = models.Generic2dOscillator()
white_matter = connectivity.Connectivity()
white_matter.speed = numpy.array([4.0])

white_matter_coupling = coupling.Linear(a=2**-9)

#Initialise an Integrator
hiss = noise.Additive(nsig = numpy.array([2**-16,]))
heunint = integrators.HeunStochastic(dt=0.06103515625, noise=hiss) #TODO: Make dt as big as possible to shorten run time... (resrtictions of integral multiples to get desired monitor period.)

#Initialise a Monitor with period in physical time
what_to_watch = monitors.TemporalAverage(period=0.48828125) #2048Hz => period=1000.0/2048.0

#Initialise a surface
local_coupling_strength = numpy.array([0.0115])

grey_matter = surfaces.LocalConnectivity(cutoff = 60.0)
grey_matter.equation.parameters['sigma1'] = 10.0
grey_matter.equation.parameters['sigma2'] = 20.0
grey_matter.equation.parameters['amp1'] = 1.0
grey_matter.equation.parameters['amp2'] = 0.5

default_cortex = surfaces.Cortex(local_connectivity=grey_matter,
                                 coupling_strength=local_coupling_strength)

#Initialise a Simulator -- Model, Connectivity, Integrator, and Monitors.
sim = simulator.Simulator(model = oscilator, connectivity = white_matter, 
                          coupling = white_matter_coupling, 
                          integrator = heunint, monitors = what_to_watch, 
                          surface = default_cortex)

sim.configure()

#Clear initial transient
LOG.info("Inital run to clear transient...")
for _ in sim(simulation_length=125):
    pass
LOG.info("Finished inital run to clear transient.")


#Perform the simulation
tavg_data = []
tavg_time = []
LOG.info("Starting simulation...")
for tavg in sim(simulation_length=8125):
    if not tavg is None:
        tavg_time.append(tavg[0][0]) #TODO:The first [0] is a hack for single monitor
        tavg_data.append(tavg[0][1]) #TODO:The first [0] is a hack for single monitor

LOG.info("Finished simulation.")


##----------------------------------------------------------------------------##
##-                     Save the data to a file                              -##
##----------------------------------------------------------------------------##

#Make the list a numpy.array.
LOG.info("Converting result to array...")
TAVG = numpy.array(tavg_data)

#Save it
FILE_NAME = "demo_data_surface_8.125s_2048Hz.npy"
LOG.info("Saving array to %s..." % FILE_NAME)
numpy.save(FILE_NAME, TAVG)

LOG.info("Done.")

###EoF###