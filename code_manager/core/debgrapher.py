import logging



from code_manager.core.configuration import ConfigurationAware
from code_manager.core.cache_container import CacheContainer
from code_manager.utils.utils import flatten
from code_manager.utils.logger import debug_red


class DebGrapher(ConfigurationAware):


    def __init__(self):
        pass



    def packages(self, group=''):
        if group == '':
            pass
        else:
            pass

    def verify_package_list(self, package_names):
        pass

    def verify_packages_graph(self):
        # check if the builders are here
        # check if all dependencies are here
        pass


    def get_dependencies(self, package):
        pass

    def get_deep_dependencies(self, package):
        pass

    def generate_build_order(self, packages):
        pass

    

    
