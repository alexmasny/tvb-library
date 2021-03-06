# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2017, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
Prepare TVB settings to be grouped under various profile classes.

.. moduleauthor:: Lia Domide <lia.domide@codemart.ro>
"""
import os
import sys
from tvb.basic.config import stored
from tvb.basic.config.environment import Environment
from tvb.basic.config.settings import ClusterSettings, DBSettings, VersionSettings, WebSettings
from tvb.basic.config.utils import EnhancedDictionary, LibraryModulesFinder, LibraryImportError


class BaseSettingsProfile(object):

    TVB_CONFIG_FILE = os.path.expanduser(os.path.join("~", '.tvb.configuration'))

    DEFAULT_STORAGE = os.path.expanduser(os.path.join('~', 'TVB' + os.sep))
    FIRST_RUN_STORAGE = os.path.expanduser(os.path.join('~', '.tvb-temp'))

    LOGGER_CONFIG_FILE_NAME = "logger_config.conf"

    # Access rights for TVB generated files/folders.
    ACCESS_MODE_TVB_FILES = 0744

    ## Number used for estimation of TVB used storage space
    MAGIC_NUMBER = 9


    def __init__(self, web_enabled=True):

        self.manager = stored.SettingsManager(self.TVB_CONFIG_FILE)

        ## Actual storage of all TVB related files
        self.TVB_STORAGE = self.manager.get_attribute(stored.KEY_STORAGE, self.FIRST_RUN_STORAGE, unicode)
        self.TVB_LOG_FOLDER = os.path.join(self.TVB_STORAGE, "logs")
        self.TVB_TEMP_FOLDER = os.path.join(self.TVB_STORAGE, "TEMP")
        self.TVB_PATH = self.manager.get_attribute(stored.KEY_TVB_PATH, '')

        self.env = Environment()
        self.cluster = ClusterSettings(self.manager)
        self.web = WebSettings(self.manager, web_enabled)
        self.db = DBSettings(self.manager, self.DEFAULT_STORAGE, self.TVB_STORAGE)
        self.version = VersionSettings(self.manager, self.BIN_FOLDER)

        self.EXTERNALS_FOLDER_PARENT = os.path.dirname(self.BIN_FOLDER)
        if self.env.is_development():
            self.EXTERNALS_FOLDER_PARENT = os.path.dirname(self.EXTERNALS_FOLDER_PARENT)

        # The path to the matlab executable (if existent). Otherwise just return an empty string.
        value = self.manager.get_attribute(stored.KEY_MATLAB_EXECUTABLE, '', str) or ''
        if value == 'None':
            value = ''
        self.MATLAB_EXECUTABLE = value

        # Maximum number of vertices acceptable o be part of a surface at import time.
        self.MAX_SURFACE_VERTICES_NUMBER = self.manager.get_attribute(stored.KEY_MAX_NR_SURFACE_VERTEX, 300000, int)
        # Max number of ops that can be scheduled from UI in a PSE. To be correlated with the oarsub limitations
        self.MAX_RANGE_NUMBER = self.manager.get_attribute(stored.KEY_MAX_RANGE_NR, 2000, int)
        # Max number of threads in the pool of ops running in parallel. TO be correlated with CPU cores
        self.MAX_THREADS_NUMBER = self.manager.get_attribute(stored.KEY_MAX_THREAD_NR, 4, int)
        # The maximum disk space that can be used by one single user, in KB.
        self.MAX_DISK_SPACE = self.manager.get_attribute(stored.KEY_MAX_DISK_SPACE_USR, 5 * 1024 * 1024, int)

        ## Configure Traits
        self.TRAITS_CONFIGURATION = EnhancedDictionary()
        self.TRAITS_CONFIGURATION.interface_method_name = 'interface'
        self.TRAITS_CONFIGURATION.use_storage = True


    @property
    def BIN_FOLDER(self):
        """
        Return path towards tvb_bin location. It will be used in some environment for determining the starting point
        """
        try:
            import tvb_bin
            return os.path.dirname(os.path.abspath(tvb_bin.__file__))
        except ImportError:
            return "."


    @property
    def PYTHON_INTERPRETER_PATH(self):
        """
        Get Python path, based on current environment.
        """
        if self.env.is_mac_deployment():
            return os.path.join(os.path.dirname(sys.executable), "python")

        return sys.executable


    def prepare_for_operation_mode(self):
        """
        Overwrite PostgreSQL number of connections when executed in the context of a node.
        """
        self.db.MAX_CONNECTIONS = self.db.MAX_ASYNC_CONNECTIONS
        self.cluster.IN_OPERATION_EXECUTION_PROCESS = True


    def initialize_profile(self):
        """
        Make sure tvb folders are created.
        """
        if not os.path.exists(self.TVB_LOG_FOLDER):
            os.makedirs(self.TVB_LOG_FOLDER)

        if not os.path.exists(self.TVB_TEMP_FOLDER):
            os.makedirs(self.TVB_TEMP_FOLDER)

        if not os.path.exists(self.TVB_STORAGE):
            os.makedirs(self.TVB_STORAGE)


    def initialize_for_deployment(self):

        library_folder = self.env.get_library_folder(self.BIN_FOLDER)

        if self.env.is_windows_deployment():
            # Add self.TVB_PATH as first in PYTHONPATH so we can find TVB there in case of GIT contributors
            self.env.setup_python_path(self.TVB_PATH, library_folder, os.path.join(library_folder, 'lib-tk'))
            self.env.append_to_path(library_folder)
            self.env.setup_tk_tcl_environ(library_folder)

        if self.env.is_mac_deployment():
            # MacOS package structure is in the form:
            # Contents/Resorces/lib/python2.7/tvb . PYTHONPATH needs to be set
            # at the level Contents/Resources/lib/python2.7/ and the root path
            # from where to start looking for TK and TCL up to Contents/
            tcl_root = os.path.dirname(os.path.dirname(os.path.dirname(library_folder)))
            self.env.setup_tk_tcl_environ(tcl_root)

            self.env.setup_python_path(self.TVB_PATH, library_folder, os.path.join(library_folder, 'site-packages.zip'),
                                       os.path.join(library_folder, 'lib-dynload'))

        if self.env.is_linux_deployment():
            # Note that for the Linux package some environment variables like LD_LIBRARY_PATH,
            # LD_RUN_PATH, PYTHONPATH and PYTHONHOME are set also in the startup scripts.
            self.env.setup_python_path(self.TVB_PATH, library_folder, os.path.join(library_folder, 'lib-tk'))
            self.env.setup_tk_tcl_environ(library_folder)

            ### Correctly set MatplotLib Path, before start.
            mpl_data_path_maybe = os.path.join(library_folder, 'mpl-data')
            try:
                os.stat(mpl_data_path_maybe)
                os.environ['MATPLOTLIBDATA'] = mpl_data_path_maybe
            except:
                pass

        if self.TVB_PATH:
            # In case of contributor setup, we want to make sure that all dev files are loaded first, so
            # we need to reload all tvb related modules, since any call done with
            # 'python -m ...' will consider the current folder as the first to search in.
            sys.path = os.environ.get("PYTHONPATH", "").split(os.pathsep) + sys.path
            for key in sys.modules.keys():
                if (key.startswith("tvb.") and sys.modules[key] and not 'lab' in key and
                        not key.startswith("tvb.basic.profile") and not 'profile_settings' in key):
                    try:
                        reload(sys.modules[key])
                    except LibraryImportError:
                        pass




class LibrarySettingsProfile(BaseSettingsProfile):
    """
    Profile used when scientific library is used without storage and without web UI.
    """

    TVB_STORAGE = os.path.expanduser(os.path.join("~", "TVB" + os.sep))
    LOGGER_CONFIG_FILE_NAME = "library_logger.conf"


    def __init__(self):

        super(LibrarySettingsProfile, self).__init__(False)

        ## Configure Traits
        self.TRAITS_CONFIGURATION = EnhancedDictionary()
        self.TRAITS_CONFIGURATION.interface_method_name = 'interface'
        self.TRAITS_CONFIGURATION.use_storage = False


    def initialize_profile(self):
        """
        Make sure some warning are thrown when trying to import from framework.
        """
        super(LibrarySettingsProfile, self).initialize_profile()
        sys.meta_path.append(LibraryModulesFinder())




class TestLibraryProfile(LibrarySettingsProfile):
    """
    Profile for library unit-tests.
    """

    LOGGER_CONFIG_FILE_NAME = "library_logger_test.conf"

    def __init__(self):

        super(TestLibraryProfile, self).__init__()
        self.TVB_LOG_FOLDER = "TEST_OUTPUT"


class MATLABLibraryProfile(LibrarySettingsProfile):
    """
    Profile use library use from MATLAB.
    """

    LOGGER_CONFIG_FILE_NAME = None
