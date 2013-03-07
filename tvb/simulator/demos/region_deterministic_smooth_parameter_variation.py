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
Demonstrate using the simulator at the region level, deterministic integration,
how to smoothly change a model parameter at run time.

``Run Time`` ~ 3 seconds

.. moduleauthor:: Paula Sanz Leon <Paula@tvb.invalid>

"""

# Third party python libraries
import numpy

"""
# Try and import from "The Virtual Brain"
from tvb.simulator.common import get_logger
LOG = get_logger(__name__)

#Import from tvb.simulator modules:
import tvb.simulator.simulator as simulator
import tvb.simulator.models as models
import tvb.simulator.coupling as coupling
import tvb.simulator.integrators as integrators
import tvb.simulator.monitors as monitors
import tvb.simulator.noise as noise

import tvb.basic.datatypes.connectivity as connectivity

from matplotlib.pyplot import *
"""

from tvb.simulator.lab import *

##----------------------------------------------------------------------------##
##-                      Perform the simulation                              -##
##----------------------------------------------------------------------------##

#rs.configure()
LOG.info("Configuring...")

#Initialise a Model, Coupling, and Connectivity.
oscilator = models.Generic2dOscillator()
white_matter = connectivity.Connectivity()
white_matter.speed = numpy.array([4.0])
white_matter_coupling = coupling.Linear(a=0.0154)

#Initialise an Integrator
heunint = integrators.HeunDeterministic(dt=2**-6)

#Initialise some Monitors with period in physical time
momo = monitors.Raw()
mama = monitors.TemporalAverage(period=2**-2)

#Bundle them
what_to_watch = (momo, mama)

#Initialise a Simulator -- Model, Connectivity, Integrator, and Monitors.
sim = simulator.Simulator(model = oscilator, connectivity = white_matter,
                          coupling = white_matter_coupling, 
                          integrator = heunint, monitors = what_to_watch)
sim.configure()
simulation_length = numpy.array([2**6, ])

# Define a model parameter as a function of time
equation = True
par_length = simulation_length[0] / sim.integrator.dt / mama.istep

# a) as an equally spaced range
if not equation:
    a = numpy.r_[0.0:4.2:par_length.astype(complex)]

# b) using an Equation datatype 
else:
    t = numpy.linspace((sim.integrator.dt * mama.istep) / 2, 
                        float(simulation_length[0]),              
                        par_length)
                         
    eqn_t = equations.Gaussian()
    eqn_t.parameters["amp"] = 4.2
    eqn_t.parameters["midpoint"] = simulation_length[0] / 2.0
    eqn_t.pattern = t
    a = eqn_t.pattern    

LOG.info("Starting simulation...")
#Perform the simulation

raw_data, raw_time = [], []
tavg_data, tavg_time = [], []


for raw, tavg in sim(simulation_length=float(simulation_length[0])):

    if not raw is None:
        raw_time.append(raw[0])
        raw_data.append(raw[1])
    
    if not tavg is None:
        tavg_time.append(tavg[0])
        tavg_data.append(tavg[1])
        
        # Change a model parameter at runtime
        sim.model.a = a[len(tavg_time)-1]

LOG.info("Finished simulation.")

##----------------------------------------------------------------------------##
##-               Plot pretty pictures of what we just did                   -##
##----------------------------------------------------------------------------##

#Plot defaults in a few combinations

#Make the lists numpy.arrays for easier use.
RAW = numpy.array(raw_data)
TAVG = numpy.array(tavg_data)

#Plot raw time series
figure(1)
plot(raw_time, RAW[:, 0, :, 0])
title("Raw -- State variable 0")

figure(2)
plot(raw_time, RAW[:, 1, :, 0])
title("Raw -- State variable 1")

#Plot temporally averaged time series + parameter
figure(3)
plot(tavg_time, TAVG[:, 0, :, 0])
plot(tavg_time, a, 'r', linewidth=2)
title("Temporal average")

#Show them
show()

###EoF###
