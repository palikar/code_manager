import os, sys

class Downloader:

    def __init__(self):
        self.download_methods = dict()
        self.download_methods["git"] = self.download_git
        self.download_methods["curl"] = self.download_curl
        self.download_methods["wget"] = self.download_wget


    def download(self, name, config):
        package = config["packages"][name]
        method = package["download"]
        self.download_methods[method](package)


    def download_git(self, package) :
        print(f"Using git and cloning from {package['URL']}")
        print(f"Cloning into {os.path.abspath('.')}")
        url = package['URL']
        os.system(f"git clone {url} .")

    def download_curl(self, package):
        print(f"Using curl and downloading from {package['URL']}")
        print(f"Downloading into {os.path.abspath('package_dir')}")
        os.system(f"curl -LOs {package['URL']} .")


    def download_wget(self, package):
        print(f"Using wget and downloading from {package['URL']}")
        print(f"Downloading into {os.path.abspath(package_dir)}")
        os.system(f"wget {package['URL']} .")        
