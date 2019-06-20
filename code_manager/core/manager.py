import logging

from code_manager.core.installation import Installation
from code_manager.core.fetcher import Fetcher
from code_manager.core.configuration import ConfigurationAware

from code_manager.core.debgrapher import DebGrapher
from code_manager.core.cache_container import CacheContainer
from code_manager.utils.utils import flatten


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
        self.depender.verify_packages_tree()

    def _invoke(self):
        logging.info('Invoking installation with: %s',
                     ','.join(self.install_queue))
        logging.info('Steps configuration:')
        logging.info('\tInstall:%s', self.install)
        logging.info('\tBuild:%s', self.build)
        logging.info('\tFetching:%s', self.fetching)

        self.depender.verify_package_list(self.install_queue)

        if self.install:
            self._invoke_install()

        if self.fetching:
            self._invoke_fetch()

        if self.fetching:
            self._invoke_build()

    def _invoke_fetch(self):
        for pack in self.install_queue:
            with self.cache as cache:

                if not cache.is_fetched(pack):
                    if self.fetcher.download(pack, pack) is None:
                        logging.critical("The fetching of '%s' failed.", pack)
                    cache.set_fetched(pack, True)
                else:
                    logging.info("\'%s\' is already fetched", pack)

    def _invoke_build(self):
        pass

    def _invoke_install(self):
        extended_queue = set(self.install_queue)
        for pack in self.install_queue:
            extended_queue.update(self.depender.get_deep_dependencies(pack))
        logging.debug('Extended queue: %s', ','.join(extended_queue))

        ordered_packages = self.depender.get_build_order(list(extended_queue))
        logging.debug('Build order: %s', ','.join(ordered_packages))

        self._check_install_nodes(ordered_packages)

        for pack in ordered_packages:
            with self.cache as cache:

                if not cache.is_fetched(pack):
                    if self.fetcher.download(pack, pack) is None:
                        logging.critical("The fetching of '%s' failed.", pack)
                    cache.set_fetched(pack, True)
                else:
                    logging.info("\'%s\' is already fetched", pack)

                if not cache.is_installed(pack):
                    if self.installation.install(pack) == 0:
                        logging.info("\'%s\' was installed", pack)
                        cache.set_installed(pack, True)
                else:
                    logging.info("\'%s\' is already installed", pack)
                    # TODO: Update\Build the package here

                cache.set_built(pack, True)

    def _check_install_nodes(self, packages):
        for pack in packages:
            pack_node = self.packages[pack]
            if 'install' not in pack_node.keys():
                continue
            installer = pack_node['install']
            if not isinstance(installer, str) and not isinstance(installer, list):
                logging.critical('Can\'t install %s.\
Installation node is nor a list, nor a string.', pack)
                exit(1)

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
            self.install_queue.append(thing)

    def install_thing(self, thing, install=True, fetch=False, build=False):
        if install:
            self.install = True
            self.fetching = False
            self.build = False
        elif build:
            self.install = False
            self.fetching = False
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
            # self._setup_all()
            self._invoke()
