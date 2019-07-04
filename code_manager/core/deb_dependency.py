import os
import subprocess


class Depender:

    def __init__(self):
        pass

    def _available_packages(self):  # pylint: disable=R0201
        pkgs = subprocess.Popen(('dpkg-query', '--list'),
                                stdout=subprocess.PIPE)
        pkgs = subprocess.check_output(
            ('awk', '{print $2}'), stdin=pkgs.stdout, universal_newlines=True)
        pkgs = pkgs.split("\n")
        return list(map(lambda deb: deb.split(':')[0], pkgs))

    def install_deb_packages(self, packages):
        pkgs = self._available_packages()
        for deb in packages:
            if deb in pkgs:
                print("'{}' is already installed".format(deb))
            else:
                print("{} is not there".format(deb))
                self.install(deb)

    def install(self, deb):  # pylint: disable=R0201
        assert deb is not None

        print("Installing package \'{}\'".format(deb))

        options = "--allow-unauthenticated  --allow-change-held-packages"

        return os.system("sudo apt-get install -y  {} {}".format(deb, options))
