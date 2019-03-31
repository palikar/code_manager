import os 
import sys
import logging



def import_file(path, name, core_package = "code_manager"):
    if sys.version_info > (3, 5):
        # python 3.5 - 3.7
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            '{}.{}'.format(core_package, name), path)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
    elif sys.version_info >= (3, 3):
        # python 3.3 - 3.4
        from importlib.machinery import SourceFileLoader
        foo = SourceFileLoader('code_manager.{}'.format(name), path).load_module()
    else:
        # python 2
        import imp
        foo = imp.load_source('{0}.{1}'.format(core_package, name), path)
    return foo


def import_modules_from_folder(folder, module, handler):
    module_paths = [os.path.join(folder, f) for f in os.listdir(folder)
                    if
                    os.path.isfile(os.path.join(folder, f)) and
                    os.path.splitext(os.path.join(folder, f))[1] == '.py' and
                    not f.startswith('_')]
    for mod_path in module_paths:
        name = os.path.splitext(os.path.basename(mod_path))[0]
        mod = import_file(mod_path, name, core_package=module)
        handler(mod, mod_path)
