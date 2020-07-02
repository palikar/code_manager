import logging
import os
import shutil
import sys

from code_manager.core.cache_container import CacheContainer
from code_manager.core.command_container import CommandContainer
from code_manager.core.configuration import CofigurationResolver
from code_manager.core.configuration import ConfigurationAware
from code_manager.core.deb_dependency import Depender
from code_manager.core.debgrapher import DebGrapher
from code_manager.core.fetcher import Fetcher
from code_manager.core.installation import Installation
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
        self.dep_depender = Depender()
        self.resolver = CofigurationResolver()
        self.commands = CommandContainer()

        self._setup_all()

    def _setup_all(self):
        self.cache.load_cache()
        self.depender.verify_packages_tree()

        for pack in self.packages.keys():
            pack_root = os.path.join(self.code_dir, self._get_root(pack))
            self.resolver.variables['root_' + pack] = pack_root

    def _expand_node(self, node):
        return self.resolver.resolve_nodes(node)

    def _invoke(self):
        logging.info(
            'Invoking pipeline with: %s',
            ','.join(self.install_queue),
        )
        logging.debug('Configuration steps :')
        logging.debug('\tInstall:%s', self.install)
        logging.debug('\tBuild:%s', self.build)
        logging.debug('\tFetching:%s', self.fetching)

        self.depender.verify_package_list(self.install_queue)

        if self.install:
            self._invoke_install()

        if self.fetching:
            self._invoke_fetch()

        if self.build:
            self._invoke_build()

    def _do_fetch(self, pack, root=None, node=None):
        root = self._get_root(pack) if root is None else root
        root_dir = os.path.join(self.code_dir, root)

        with self.cache as cache:
            if cache.is_fetched(pack) and not self.force:
                logging.info("\'%s\' is already fetched", pack)
                return 0

            if os.path.exists(root_dir) and self.force:
                logging.info('Force mode. Removing folder: %s', root)
                shutil.rmtree(root_dir)

            if not cache.is_fetched(pack) or self.force:
                cache.set_fetched(pack, False)

                node = self._expand_node(
                    self.packages[pack],
                ) if node is None else node

                if self.fetcher.download(pack, root, node) is None:
                    logging.critical("The fetching of '%s' failed.", root)
                    cache.set_fetched(pack, True)
                    cache.set_root(pack, root_dir)

            else:
                logging.info("\'%s\' is already fetched", pack)

    def _invoke_fetch(self):
        for pack in self.install_queue:
            self._do_fetch(pack)

    def _invoke_build(self):

        self.installation.load_installer()

        broken = []
        for pack in self.install_queue:
            if self.cache.is_installed(pack):
                broken.append(pack)
        if broken:
            logging.critical(
                'The packages [%s] are not installed.', ','.join(broken),
            )

        for pack in self.install_queue:
            with self.cache as cache:
                cache.set_built(pack, False)
                node = self._expand_node(self.packages[pack])
                if self.installation.install(
                    pack, cache.get_root(pack), node,
                    update=True,
                ) == 0:
                    logging.info("\'%s\' was build", pack)
                    cache.set_built(pack, True)

    def _invoke_install(self):

        self.installation.load_installer()

        extended_queue = set(self.install_queue)
        for pack in self.install_queue:
            extended_queue.update(self.depender.get_deep_dependencies(pack))
        logging.debug('Extended queue: %s', ','.join(extended_queue))

        ordered_packages = self.depender.get_build_order(list(extended_queue))
        logging.debug('Build order: [ %s ]', ','.join(ordered_packages))

        self._check_install_nodes(ordered_packages)

        for pack in ordered_packages:
            root = self._get_root(pack)
            node = self._expand_node(self.packages[pack])

            self._do_fetch(pack, root=root, node=node)

            if self.dep_depender.check(pack) != 0:
                raise SystemExit

            with self.cache as cache:
                # if the package is not installed - install it
                # installation means 'for the first time'
                if not cache.is_installed(pack):
                    logging.info("Trying to install \'%s\'", pack)
                    logging.debug('No missing debian packages.')
                    if self.installation.install(pack, cache.get_root(pack), node) == 0:
                        logging.info("\'%s\' was installed", pack)
                        cache.set_installed(pack, True)
                # if the package is installed, we want to update it
                # 'update' means 'install again'
                else:
                    logging.info("\'%s\' is already installed", pack)
                    logging.info("Trying to update \'%s\'", pack)
                    cache.set_built(pack, False)
                    if self.installation.install(
                        pack,
                        cache.get_root(pack),
                        node,
                        update=True,
                    ) == 0:
                        logging.info("\'%s\' was build", pack)
                        cache.set_built(pack, True)

    def _check_install_nodes(self, packages):
        for pack in packages:
            pack_node = self.packages[pack]
            if 'install' not in pack_node.keys():
                continue
            installer = pack_node['install']
            if not isinstance(installer, str) and not isinstance(installer, list):
                logging.critical(
                    'Can\'t install %s.\
Installation node is nor a list, nor a string.', pack,
                )
                sys.exit(1)

    def _install_thing(self, thing):

        if thing in self.packages_list.keys():
            logging.debug(
                r'\`%s\` is a group. Installing all packages in it.', thing,
            )
            self.install_queue = (
                self.install_queue + self.config['packages_list'][thing]
            )

        elif thing in flatten(self.packages_list.values()):
            logging.debug(r'\`%s\` is a package. Installing it.', thing)
            self.install_queue.append(thing)

        else:
            self.install_queue.append(thing)

    def get_cache(self):
        return self.cache

    def install_thing(self, thing, install=True, fetch=False, build=False, force=False):
        assert thing is not None

        if install:
            self.install = True
            self.fetching = False
            self.build = False

        if build:
            self.install = False
            self.fetching = False
            self.build = True

        if fetch:
            self.install = False
            self.fetching = True
            self.build = False

        self.force = force

        if isinstance(thing, list):
            for name in thing:
                self._install_thing(name)
        else:
            self._install_thing(thing)

        if self.install_queue:
            self._invoke()

    def get_cache_content(self):
        cache_content = []
        for pack in self.packages.keys():
            if self.cache.in_cache(pack):
                cache_content.append({
                    'name': pack,
                    'fetched': self.cache.is_fetched(pack),
                    'built': self.cache.is_built(pack),
                    'installed': self.cache.is_installed(pack),
                    'root': self.cache.get_root(pack),
                })
        return cache_content

    def get_group_packages(self, group):
        if group not in self.packages_list.keys():
            return []
        return self.packages_list[group]

    def get_groups(self):
        return list(self.packages_list.keys())

    def get_fetchers(self):
        return self.fetcher.get_available_fetcheres()

    def remove_package(self, packs):
        if packs is None:
            return
        for pack in packs:
            if self.cache.in_cache(pack):
                logging.info("\'%s\' is not a packcage", pack)

            with self.cache as cache:
                logging.info("Removing package: \'%s\'", pack)
                root = cache.get_root(pack)
                if os.path.exists(root):
                    shutil.rmtree(root)
                cache.set_fetched(pack, False)
                cache.set_root(pack, '')
                cache.set_built(pack, False)
                cache.set_installed(pack, False)

    def rebuild_cache(self, asume_installed=True):

        for pack, _ in self.packages.items():
            root = self._get_root(pack)
            pack_root = os.path.join(self.code_dir, root)

            if asume_installed and os.path.exists(pack_root) and os.path.isdir(pack_root):
                logging.debug(
                    'Assuming \'%s\' is installed in \'%s\'', pack, pack_root,
                )
                with self.cache:
                    self.cache.set_built(pack, True)
                    self.cache.set_fetched(pack, True)
                    self.cache.set_installed(pack, True)
                    self.cache.set_root(pack, root)
                continue

            if os.path.exists(os.path.join(pack_root, '.code_manager_cache')):
                with self.cache:
                    logging.debug('Rebuilding cache for package \'%s\'', pack)
                    self.cache.rebuild(pack, pack_root)

    def run_command(self, command, args, thing=None, prim_args=None):
        self.commands.load_commands()

        if thing in self.packages.keys():
            queue = [thing]
        elif thing in self.packages_list.keys():
            queue = self.config['packages_list'][thing]
        else:
            queue = self.packages.keys()

        for pack in queue:

            if not self.cache.is_fetched(pack):
                continue

            root = os.path.join(self.code_dir, self._get_root(pack))
            self.commands.execute_command(command, args, pack, root)
        return 0
