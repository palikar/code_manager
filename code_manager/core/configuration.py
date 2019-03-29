
from __future__ import (absolute_import, division, print_function)

class ConfigurationAware:

    @staticmethod
    def set_configuration(config, install_scripts_dir, cache_file, opt):
        ConfigurationAware.opt = opt
        ConfigurationAware.usr_dir = opt["Config"]["code"]
        ConfigurationAware.code_dir = opt["Config"]["usr"]
        
        ConfigurationAware.config = config
        
        ConfigurationAware.install_scripts_dir = install_scripts_dir
        
        ConfigurationAware.cache_file = cache_file
        

    
