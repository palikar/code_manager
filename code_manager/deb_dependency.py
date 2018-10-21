import os, sys
import subprocess




class Depender:

    def __init__(self):
        pass




    def install_deb_packages(self, packages):
        for deb in packages:
            pkgs = subprocess.Popen(('dpkg-query', '--list'), stdout=subprocess.PIPE)
            pkgs = subprocess.check_output(
                ('awk', '{print $2}'), stdin=pkgs.stdout,universal_newlines=True)
            pkgs = pkgs.split("\n")
            pkgs = list(map(lambda deb: deb.split(':')[0], pkgs))
            if deb in pkgs:
                print(f"'{deb}' is already installed")
            else:
                print(f"{deb} is not there")
                self.install(deb)
                
    def install(self, deb):
        print(f"Installing {deb}")

        do_not_use = "--allow-downgrades --allow-remove-essential"
        options = "--allow-unauthenticated  --allow-change-held-packages"
        
        os.system(f"sudo apt-get install -y  {deb} {options}")
