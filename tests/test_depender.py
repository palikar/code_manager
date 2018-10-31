import unittest
from unittest.mock import patch


from os import path
import code_manager as cm
from code_manager.deb_dependency import Depender


class TestDown(unittest.TestCase):


    @patch('code_manager.deb_dependency.Depender.install')
    @patch('code_manager.deb_dependency.Depender._available_packages',
        return_value=['mock', 'mocker'])
    def test_install_deb_packages(self, packs, install):
        deb = Depender()
        packages = ['mock', 'mocker', 'mojito']
        deb.install_deb_packages(packages)        
        install.assert_called_once_with('mojito')


    @patch('os.system',return_value=0)
    def test_install(self, system):
        deb = Depender()

        res = deb.install('mock')

        self.assertEqual(res, 0)
        system.assert_called_once()
        self.assertTrue('apt-get install' in system.call_args[0][0])
        self.assertTrue('mock' in system.call_args[0][0])
            
        

        

if __name__ == '__main__':
    unittest.main()
