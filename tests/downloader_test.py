import unittest

# from unittest.mock import patch
# from code_manager.core.downloader import Downloader


class TestDown(unittest.TestCase):
    pass
    # @patch('os.system')
    # def test_git(self, os_system):
    #     down = Downloader()
    #     url = "simple.com"
    #     config = dict()
    #     config['packages'] = dict()
    #     config['packages']['mock'] = dict()
    #     config['packages']['mock']['download'] = 'git'
    #     config['packages']['mock']['URL'] = url
    #     down.download('mock', config)
    #     os_system.assert_called_once_with(f'git clone {url} .')

    # @patch('os.system')
    # def test_curl(self, os_system):
    #     down = Downloader()
    #     url = "simple.com"
    #     config = dict()
    #     config['packages'] = dict()
    #     config['packages']['mock'] = dict()
    #     config['packages']['mock']['download'] = 'curl'
    #     config['packages']['mock']['URL'] = url
    #     down.download('mock', config)
    #     os_system.assert_called_once_with(f'curl -LOs {url} .')

    # @patch('os.system')
    # def test_wget(self, os_system):
    #     down = Downloader()
    #     url = "simple.com"
    #     config = dict()
    #     config['packages'] = dict()
    #     config['packages']['mock'] = dict()
    #     config['packages']['mock']['download'] = 'wget'
    #     config['packages']['mock']['URL'] = url
    #     down.download('mock', config)
    #     os_system.assert_called_once_with(f'wget {url} .')


if __name__ == '__main__':
    unittest.main()
