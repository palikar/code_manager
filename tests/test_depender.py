import unittest

# from unittest.mock import patch
# from code_manager.core.deb_dependency import Depender


class TestDown(unittest.TestCase):
    pass
    # @patch('code_manager.core.deb_dependency.Depender.install')
    # @patch('code_manager.core.deb_dependency.Depender._available_packages',
    #        return_value=['mock', 'mocker'])
    # def test_install_deb_packages(self, packs, install):
    #     deb = Depender()
    #     packages = ['mock', 'mocker', 'mojito']
    #     deb.install_deb_packages(packages)
    #     install.assert_called_once_with('mojito')

    # @patch('os.system', return_value=0)
    # def test_install(self, system):
    #     deb = Depender()

    #     with self.assertRaises(AssertionError):
    #         deb.install(None)

    #     res = deb.install('mock')

    #     self.assertEqual(res, 0)
    #     system.assert_called_once()
    #     self.assertIn('apt-get install', system.call_args[0][0])
    #     self.assertIn('mock', system.call_args[0][0])


if __name__ == '__main__':
    unittest.main()
