import unittest
from unittest.mock import patch

from code_manager.installer import Installer


class TestDown(unittest.TestCase):

    def test_install_noinstall(self):
        inst = Installer(
            "user_dir_mock", "install_scripts_mock", noinstall=True)
        self.assertEqual(
            inst.install(None, None, reinstall=True), 0)
        self.assertEqual(
            inst.install(None, None, reinstall=False), 0)

    @patch('code_manager.installer.Installer.install_with_script')
    def test_install_script(self, fun):
        inst = Installer(
            "user_dir_mock", "install_scripts_mock", noinstall=False)
        config = dict()
        config['packages'] = dict()
        config['packages']['mock'] = dict()
        config['packages']['mock']['install'] = 'script'
        inst.install('mock', config['packages']['mock'], reinstall=True)
        fun.assert_called_once_with(
            'mock', config['packages']['mock'], reinstall=True)
        fun.reset_mock()
        inst.install('mock', config['packages']['mock'], reinstall=False)
        fun.assert_called_once_with(
            'mock', config['packages']['mock'], reinstall=False)

    @patch('code_manager.installer.Installer.install_with_command')
    def test_install_command(self, fun):
        inst = Installer(
            "user_dir_mock", "install_scripts_mock", noinstall=False)
        config = dict()
        config['packages'] = dict()
        config['packages']['mock'] = dict()
        config['packages']['mock']['install'] = 'command'
        inst.install('mock', config['packages']['mock'], reinstall=True)
        fun.assert_called_once_with('mock',
                                    config['packages']['mock'], reinstall=True)
        fun.reset_mock()
        inst.install('mock', config['packages']['mock'], reinstall=False)
        fun.assert_called_once_with(
            'mock', config['packages']['mock'], reinstall=False)

    @patch('code_manager.installer.Installer.install_with_cmake')
    def test_install_cmake(self, fun):
        inst = Installer(
            "user_dir_mock", "install_scripts_mock", noinstall=False)
        config = dict()
        config['packages'] = dict()
        config['packages']['mock']  = dict()
        config['packages']['mock']['install'] = 'cmake'
        inst.install('mock', config['packages']['mock'], reinstall=True)
        fun.assert_called_once_with(
            'mock', config['packages']['mock'], reinstall=True)
        fun.reset_mock()
        inst.install('mock', config['packages']['mock'], reinstall=False)
        fun.assert_called_once_with(
            'mock', config['packages']['mock'], reinstall=False)

    @patch('os.system')
    def test_install_with_script(self, os):
        inst = Installer(
            "user_dir_mock", "install_scripts_mock", noinstall=False)
        config = dict()
        config['packages'] = dict()
        config['packages']['mock'] = dict()
        config['packages']['mock']['install'] = 'script'

        with self.assertRaises(AssertionError):
            self.assertEqual(inst.install_with_script(None, None), -1)
        with self.assertRaises(AssertionError):
            self.assertEqual(inst.install_with_script('mock', None), -1)
        with self.assertRaises(AssertionError):
            self.assertEqual(
                inst.install_with_script(None, config['packages']['mock']), -1)

        with self.assertRaises(AssertionError):
            inst.install_with_script('mock', config['packages']['mock'])

        config['packages']['mock']['script'] = 'mock_script'
        inst.install_with_script('mock', config['packages']['mock'])

        os.assert_called_once()


    @patch('os.system')
    def test_install_with_setup_py(self, os):
        inst = Installer(
            "user_dir_mock", "install_scripts_mock", noinstall=False)
        config = dict()
        config['packages'] = dict()
        config['packages']['mock'] = dict()
        config['packages']['mock']['install'] = 'setup.py'

        with self.assertRaises(AssertionError):
            self.assertEqual(inst.install_with_setup_py(None, None), -1)
        with self.assertRaises(AssertionError):
            self.assertEqual(inst.install_with_setup_py('mock', None), -1)
        with self.assertRaises(AssertionError):
            self.assertEqual(inst.install_with_setup_py(
                None, config['packages']['mock']), -1)

        with self.assertRaises(AssertionError):
            inst.install_with_script('mock', config['packages']['mock'])

        inst.install_with_setup_py('mock', config['packages']['mock'])
        os.assert_called_once()

    @patch('os.system')
    @patch('os.chdir')
    def test_install_with_cmake(self, chdir, os):
        inst = Installer(
            "user_dir_mock", "install_scripts_mock", noinstall=False)

        config = dict()
        config['packages'] = dict()
        config['packages']['mock'] = dict()
        config['packages']['mock']['install'] = 'cmake'
        config['packages']['mock']['cmake_args'] = '-make_arg'
        config['packages']['mock']['make_args'] = '-cmake_arg'

        with self.assertRaises(AssertionError):
            self.assertEqual(inst.install_with_cmake(None, None), -1)
        with self.assertRaises(AssertionError):
            self.assertEqual(inst.install_with_cmake('mock', None), -1)
        with self.assertRaises(AssertionError):
            self.assertEqual(inst.install_with_cmake(
                None, config['packages']['mock']), -1)

        inst.install_with_cmake('mock', config['packages']['mock'])
        os.assert_called_once()

        self.assertIn('cmake', os.call_args[0][0])
        self.assertIn('DCMAKE_INSTALL_PREFIX', os.call_args[0][0])
        self.assertIn('-make_arg', os.call_args[0][0])
        self.assertIn('-cmake_arg', os.call_args[0][0])
        self.assertIn('make install', os.call_args[0][0])

    @patch('os.system')
    @patch('os.chdir')
    def test_install_with_command(self, chdir, os):
        inst = Installer(
            "user_dir_mock", "install_scripts_mock", noinstall=False)

        config = dict()
        config['packages'] = dict()
        config['packages']['mock'] = dict()
        config['packages']['mock']['install'] = 'command'
        config['packages']['mock']['command'] = 'mock_command'

        with self.assertRaises(AssertionError):
            self.assertEqual(inst.install_with_command(None, None), -1)
        with self.assertRaises(AssertionError):
            self.assertEqual(inst.install_with_command('mock', None), -1)
        with self.assertRaises(AssertionError):
            self.assertEqual(inst.install_with_command(
                None, config['packages']['mock']), -1)

        inst.install_with_command('mock', config['packages']['mock'])
        os.assert_called_once()

        self.assertIn('mock_command', os.call_args[0][0])


if __name__ == '__main__':
    unittest.main()
