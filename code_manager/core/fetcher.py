import os
import subprocess
import logging
import re

from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.logger import debug_red


class Fetcher(ConfigurationAware):

    GIT_COMMAND = 'git'
    WGET_COMMAND = 'wget'
    CURL_COMMAND = 'curl'

    GIT_HTTPS_RE = re.compile(r'https:\/\/(.*?)\/(.*)')
    GIT_SSH_RE = re.compile(r'git@(.*?):(.*)')

    def __init__(self):

        self.download_methods = {}
        self.download_methods["git"] = self._download_git
        self.download_methods["curl"] = self._download_curl
        self.download_methods["wget"] = self._download_wget

        logging.debug('Fetchers: ' + str(list(self.download_methods.keys())))

        # TODO: load the extra fetching functions

    def download(self, name, root):   # pylint: disable=R0201
        logging.debug('Trying download %s in folder %s', name, root)
        if name not in self.packages.keys():
            debug_red('The package %s is not in the package file.', name)
            return None

        package = self.packages[name]
        fetcher = package["fetch"]

        if isinstance(fetcher, list):
            for fetch in fetcher:
                pass
        elif isinstance(fetcher, str):
            self.download_methods[fetcher](name, package, root)
        else:
            debug_red('The fetcher field of the package \'%s\' is invalid: %s', name, fetcher)
            return None

    def get_available_fetcheres(self):
        pass

    def _download_git(self, name, package, root):   # pylint: disable=R0201
        logging.info('Trying to fetch with git.')

        if 'git' not in package.keys() or not isinstance(package['git'], dict):
            debug_red('Invalid git node for packag %s.', name)
            return None

        if 'url' not in package['git'].keys():
            debug_red('The git node of %s does not have urlf field.', name)
            return None

        git_node = package['git']
        url = git_node['url']
        path = os.path.join(self.code_dir, root)

        cmd = []
        cmd.append(self.GIT_COMMAND)
        cmd.append('clone')

        if 'args' in git_node.keys() and isinstance(git_node['args'], str):
            cmd.append(git_node['args'])

        if self.git_ssh:
            logging.debug('Trying to use ssh with git')
            match = self.GIT_HTTPS_RE.match(url)
            if match:
                url = 'git@' + match.group(1) + ':' + match.group(2)
                cmd.append(url)
            elif self.GIT_SSH_RE.match(url) is not None:
                cmd.append(url)
            else:
                debug_red('Bad git url for %s: %s', name, url)
                return None
        else:
            logging.debug('Trying to use https with git')
            match = self.GIT_SSH_RE.match(url)
            if match:
                url = 'https://' + match.group(1) + '/' + match.group(2)
                cmd.append(url)
            elif self.GIT_HTTPS_RE.match(url) is not None:
                cmd.append(url)
            else:
                debug_red('Bad git url for %s: %s', name, url)
                return None

        if os.path.exists(path):
            debug_red('The given path already exists: %s', path)
            return None

        cmd.append(path)

        logging.debug('Fetching with git and command: %s', cmd)

        if subprocess.call(cmd) != 0:
            debug_red('The fetching failed!')
            return None

        # TODO: Mark somehow that the contents have been cloned but the step is not fully complete

        if 'checkout' in git_node.keys() and isinstance(git_node['checkout'], str):
            cmd = []
            cmd.append(self.GIT_COMMAND)
            cmd.append('checkout')
            cmd.append(git_node['checkout'])
            if subprocess.call(cmd) != 0:
                debug_red('The checkint out failed!')
                return None

        return 0

    def _download_curl(self, name, package, root):   # pylint: disable=R0201
        logging.info('Trying to fetch with curl.')

        if 'curl' not in package.keys() or not isinstance(package['curl'], dict):
            debug_red('Invalid curl node for packag %s.', name)
            return None

        if 'url' not in package['curl'].keys():
            debug_red('The git node of %s does not have urlf field.', name)
            return None

        curl_node = package['git']
        url = curl_node['url']
        path = os.path.join(self.code_dir, root)

        cmd = []

        cmd.append('cd')
        cmd.append(path)
        cmd.append('&&')

        cmd.append(self.CURL_COMMAND)

        if 'args' in curl_node.keys() and isinstance(curl_node['args'], str):
            cmd.append(curl_node['args'])

        cmd.append(url)

        if 'output' in curl_node.keys() and isinstance(curl_node['output'], str):
            cmd.append('-o')
            cmd.append(curl_node['output'])
        else:
            cmd.append('-O')

        cmd.append('&&')
        cmd.append('cd')
        cmd.append('-')

        logging.debug('Fetching with curl and command: %s', cmd)

        if subprocess.Popen(cmd, shell=True) != 0:
            debug_red('The fetching failed!')
            return None

        return 0

    def _download_wget(self, name, package, root):   # pylint: disable=R0201
        os.system(f"wget {package['URL']} .")