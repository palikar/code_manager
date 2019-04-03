import unittest
import os
import tempfile
import json
from code_manager.merge_packages_lists import merge_package_file


class TestDown(unittest.TestCase):

    def test_merging(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        input1 = os.path.join(dir_path, "data", "packages1.json")
        input2 = os.path.join(dir_path, "data", "packages2.json")
        outfile_path = tempfile.mkstemp()[1]
        print(outfile_path)
        merge_package_file([input1, input2], outfile_path)

        try:
            contents = json.load(open(outfile_path))

            self.assertIn(['package1'], contents['packages_list'])
            self.assertIn(['package2'], contents['packages_list'])

            self.assertIn('package1', contents['packages'].keys())
            self.assertIn('package2', contents['packages'].keys())

            self.assertIn(['mock1', 'mock2'], contents['debian_packages'])
            self.assertIn(['mock3', 'mock4'], contents['debian_packages'])

        finally:
            os.remove(outfile_path)


if __name__ == '__main__':
    unittest.main()
