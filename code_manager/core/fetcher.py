import os
import subprocess
import logging
import re
import shutil

from contextlib import suppress

from code_manager.core.configuration import ConfigurationAware
from code_manager.utils.logger import debug_red
from code_manager.utils.process import execute_sanitized
from code_manager.utils.path_utils import move_tree


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
        # self.download_methods["wget"] = self._download_wget

        logging.debug('Fetchers: %s.', ','.join(self.download_methods.keys()))

        self.archive_extensions = ['.zip', '.tar.gz', '.tar.7z', '.tar.bz2']
        self.extract_queue = []

        # TODO: load the extra fetching functions

    def download(self, name, root):   # pylint: disable=R0201,R0915
        assert name is not None
        assert root is not None

        logging.debug('Trying download %s in folder %s', name, root)
        if name not in self.packages.keys():
            debug_red('The package %s is not in the package file.', name)
            return None

        package = self.packages[name]
        fetcher = package["fetch"]
        self.extract_queue = []

        if isinstance(fetcher, list):
            for fetch in fetcher:
                if self.download_methods[fetch](name, package, root) is None:
                    return None
        elif isinstance(fetcher, str):
            if self.download_methods[fetcher](name, package, root) is None:
                return None
        else:
            debug_red('The fetcher field of the package \'%s\' is invalid: %s', name, fetcher)
            return None

        self._try_extract(package)

        return 0

    def _try_extract(self, package):
        extract_node = package.get('extract', False)
        if extract_node:
            self.run_extract()

    def run_extract(self):
        # TODO: Better checks for file extensions
        for file_path in self.extract_queue:
            logging.info("Extracting: %s", file_path)

            shutil.unpack_archive(file_path, os.path.dirname(file_path))

            for ext in self.archive_extensions:
                if file_path.endswith(ext):
                    extr_dir = file_path[:-len(ext)] + '/'

            dest_dir = os.path.dirname(file_path)
            move_tree(extr_dir, dest_dir)
            shutil.rmtree(extr_dir)

    def get_available_fetcheres(self):
        # TODO: Implement pretty function for diplaying
        # how a package can be fetched
        pass

    def _download_git(self, name, package, root):   # pylint: disable=R0201,R0911
        assert name is not None
        assert root is not None
        assert package is not None

        logging.info('Trying to fetch with git.')

        if 'git' not in package.keys() or not isinstance(package['git'], dict):
            debug_red('Invalid git node for packag %s.', name)
            return None

        if 'url' not in package['git'].keys():
            debug_red('The git node of %s does not have urlf field.', name)
            return None

        git_node = package['git']
        url = git_node['url']
        # TODO: Do not join the root here but pass it from above
        path = os.path.join(self.code_dir, root)

        cmd = []
        cmd.extend([self.GIT_COMMAND, 'clone'])

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

            logging.debug('Checking out a git repository with %s ', ','.join(cmd))

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

        curl_node = package['curl']
        url = curl_node['url']
        path = os.path.join(self.code_dir, root)
        file_name = file_name = url.split('/')[-1]

        with suppress(OSError):
            os.makedirs(path)

        cmd = []

        cmd.append(self.CURL_COMMAND)

        if 'args' in curl_node.keys() and isinstance(curl_node['args'], str):
            cmd.append(curl_node['args'])

        cmd.append(url)

        if 'output' in curl_node.keys() and isinstance(curl_node['output'], str):
            cmd.append('-o')
            cmd.append(curl_node['output'])
            file_name = curl_node['output']
        else:
            cmd.append('-O')

        logging.debug('Fetching with curl and command: %s', cmd)
        if execute_sanitized('curl', cmd, path) is None:
            return None

        file_path = os.path.join(path, file_name)
        for ext in self.archive_extensions:
            if file_path.endswith(ext):
                self.extract_queue.append(file_path)
                break

        return 0

    # def _download_wget(self, name, package, root):   # pylint: disable=R0201
    #     os.system("wget {package['URL']} .")
