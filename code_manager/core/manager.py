import logging

from code_manager.core.installation import Installation
from code_manager.core.fetcher import Fetcher
from code_manager.core.configuration import ConfigurationAware

from code_manager.core.debgrapher import DebGrapher
from code_manager.core.cache_container import CacheContainer
from code_manager.utils.utils import flatten
from code_manager.utils.logger import debug_red


class Manager(ConfigurationAware):

    install = False
    build = False
    fetching = False

    def __init__(self):

        self.install_queue = list()

        self.installation = Installation()
        self.cache = CacheContainer()
        self.fetcher = Fetcher()
        self.depender = DebGrapher()

        self._setup_all()

    def _setup_all(self):
        self.installation.load_installer()
        self.cache.load_cache()

    def _invoke(self):
        pass

    def _invoke_build(self):
        pass

    def _invoke_install(self):
        pass

    def fetch_package(self, package):
        with self.cache as cache:
            if cache.is_fetched(package):
                debug_red("The package '%s' is already fetched", package)
                return None
            if self.fetcher.download(package, package) is None:
                debug_red("The fetching of '%s' failed.", package)
                return None
            else:
                cache.set_fetched(package, True)
                cache.set_root(package, package)
            return 0

    def fetch_group(self, group):
        for pack in self.packages_list[group]:
            self.fetch_package(pack)

    def fetch_thing(self, thing):
        if thing in self.packages_list.keys():
            logging.info("'%s' is a group. Fetching all packages in it.", thing)
            self.fetch_group(thing)
        elif thing in flatten(self.packages_list.values()):
            logging.info("'%s' is a package. Fetching it.", thing)
            self.fetch_package(thing)
        else:
            logging.info("There is no thing with name '%s'", thing)

    def fetch(self, thing):
        if isinstance(thing, list):
            for thingy in thing:
                self.fetch_thing(thingy)
        elif isinstance(thing, str):
            self.fetch_thing(thing)
        else:
            logging.critical("Can't install %s. It's \
            no string nor list", thing)

    def _install_thing(self, thing):

        if thing in self.packages_list.keys():
            logging.debug(
                r"\`%s\` is a group. Installing all packages in it.", thing)
            self.install_queue = (
                self.install_queue + self.config["packages_list"][thing])

        elif thing in flatten(self.packages_list.values()):
            logging.debug(r"\`%s\` is a package. Installing it.", thing)
            self.install_queue.append(thing)

        else:
            logging.critical("There is no thing with name %s", thing)

    def install_thing(self, thing, install=True, fetch=False, build=False):
        if install:
            self.install = True
            self.fetching = True
            self.build = True
        elif build:
            self.install = False
            self.fetching = True
            self.build = True
        elif fetch:
            self.install = False
            self.fetching = True
            self.build = False

        if isinstance(thing, list):
            for name in thing:
                self._install_thing(name)
        else:
            self._install_thing(thing)

        if self.install_queue:
            self._setup_all()
            self._invoke()
