import os


class Downloader:

    def __init__(self):
        self.download_methods = dict()
        self.download_methods["git"] = self.download_git
        self.download_methods["curl"] = self.download_curl
        self.download_methods["wget"] = self.download_wget

    def download(self, name, config):   # pylint: disable=R0201
        package = config["packages"][name]
        method = package["download"]
        self.download_methods[method](package)

    def download_git(self, package):   # pylint: disable=R0201
        print(f"Using git and cloning from {package['URL']}")
        print(f"Cloning into {os.path.abspath('.')}")
        url = package['URL']
        print(f"Command: git clone {url} .")
        os.system(f"git clone {url} .")

    def download_curl(self, package):   # pylint: disable=R0201
        print(f"Using curl and downloading from {package['URL']}")
        print(f"Cloning into {os.path.abspath('.')}")
        print(f"Command: curl -LOs {package['URL']} .")
        os.system(f"curl -LOs {package['URL']} .")

    def download_wget(self, package):   # pylint: disable=R0201
        print(f"Using wget and downloading from {package['URL']}")
        print(f"Cloning into {os.path.abspath('.')}")
        print(f"Command: wget {package['URL']} .")
        os.system(f"wget {package['URL']} .")
