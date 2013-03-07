# -*- coding: utf-8 -*-
#
#
# (c)  Baycrest Centre for Geriatric Care ("Baycrest"), 2013, all rights reserved.
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
Mark TVB-Simulator-Library as a Python import.
Mention dependencies for this package.
"""

import setuptools
import shutil


LIBRARY_VERSION = "1.0"

TVB_TEAM = "Stuart Knock, Marmaduke Woodman, Paula Sansz Leon"
CONTACT_EMAIL = "tvb.admin@thevirtualbrain.org"

TVB_INSTALL_REQUIREMENTS = ["networkx", "nibabel", "numpy", "numexpr", "scikit-learn", "scipy"]


setuptools.setup( name = 'tvb',
                  version = LIBRARY_VERSION,
                  packages = setuptools.find_packages(),
                  license = 'Not decided yet',
                  author = TVB_TEAM,
                  author_email = CONTACT_EMAIL,
                  include_package_data = True,
                  install_requires = TVB_INSTALL_REQUIREMENTS)
## Cleanup after EGG install.
shutil.rmtree('tvb.egg-info', True)


 