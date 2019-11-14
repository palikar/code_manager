import subprocess
import logging

from code_manager.utils.lazy_property import lazy_property
from code_manager.core.configuration import ConfigurationAware


class Depender(ConfigurationAware):

    def __init__(self):
        pass

    def _available_packages(self):  # pylint: disable=R0201
        pkgs = subprocess.Popen(('dpkg-query', '--list'),
                                stdout=subprocess.PIPE)
        pkgs = subprocess.check_output(
            ('awk', '{print $2}'), stdin=pkgs.stdout, universal_newlines=True)
        pkgs = pkgs.split("\n")
        return list(map(lambda deb: deb.split(':')[0], pkgs))

    @lazy_property
    def debian_packages(self):
        return self._available_packages()

    def check(self, package):
        assert package is not None

        dependencies = self.packages[package].get('deb_packages', [])
        if not dependencies:
            return 0
        return self.install_deb_packages(dependencies)

    def install_deb_packages(self, packages):
        assert isinstance(packages, list)

        install_queue = []
        for deb in packages:
            if deb in self.debian_packages:
                logging.debug('\'%s\' is already installed', deb)
            else:
                logging.debug('\'%s\' is not installed', deb)
                install_queue.append(deb)
        return self.install(install_queue)

    def install(self, deb):  # pylint: disable=R0201
        assert deb is not None

        if not deb:
            return 0

        print('\n\tRun \'sudo apt-get install -y {}\'\n'.format(' '.join(deb)))
        return 1
        # options = "--allow-unauthenticated  --allow-change-held-packages"
        # return os.system("sudo apt-get install -y  {} {}".format(deb, options))
