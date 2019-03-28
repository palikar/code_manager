import os
import subprocess


class Depender:

    def __init__(self):
        pass

    def _available_packages(self):
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
                print(f"'{deb}' is already installed")
            else:
                print(f"{deb} is not there")
                self.install(deb)

    def install(self, deb):
        assert(deb is not None)

        print(f"Installing package \'{deb}\'")

        options = "--allow-unauthenticated  --allow-change-held-packages"

        return os.system(f"sudo apt-get install -y  {deb} {options}")
