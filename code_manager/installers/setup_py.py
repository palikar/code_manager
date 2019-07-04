from code_manager.core.installation import BasicInstaller
from code_manager.core.configuration import ConfigurationAware


class SetupPyInstaller(BasicInstaller, ConfigurationAware):

    name = 'setup.py'
    manditory_attr = []

    def __init__(self):
        BasicInstaller.__init__(self)

    def execute(self, name):
        assert name is not None

        setup_file = os.path.join(self.root, 'setup.py')

        if not os.path.isfile('setup.py'):
            debug_red('There isn\'t a setup.py file at the root of the package %s.', name)
            return None

        setup_command = ['python']
        setup_command.append('setup.py')

        self.append_optional('setup_args', setup_command)
        
        setup_command.append('install')
        setup_command.append('--prefix')
        setup_command.append(self.usr_dir)

        self.append_optional('setup_install_args', setup_command)

        logging.debug('Running setup.py with: %s', ' '.join(setup_command))

        print("setup.py output =================>\n")
        child = subprocess.Popen(setup_command,
                                 cwd=build_dir)

        _ = child.communicate()[0]
        ret_code = child.returncode
        print("\n<================= setup.py output ")

        if ret_code != 0:
            debug_red('Running setup.py failed')
            return None

        
        return 0

    def update(self, name):
        return 0


ExportedClass = SetupPyInstaller
