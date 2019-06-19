import unittest

# from unittest.mock import patch
from code_manager.core.debgrapher import DebGrapher


class TestDown(unittest.TestCase):

    def test_verify_packages(self):

        DebGrapher.packages_list = {}
        DebGrapher.packages_list['g1'] = ['mock', 'mocker', 'mockito']
        DebGrapher.packages_list['g2'] = ['mock2', 'mocker2', 'mockito2']

        deb = DebGrapher()

        self.assertEqual(deb.verify_package_list(['mock', 'mocker']), 0)
        self.assertEqual(deb.verify_package_list(['mock2', 'mocker2']), 0)
        self.assertEqual(deb.verify_package_list(['mockito']), 0)
        with self.assertRaises(SystemExit):
            deb.verify_package_list(['not_mock'])

    def test_get_packages(self):

        DebGrapher.packages_list = {}
        DebGrapher.packages_list['g1'] = ['mock', 'mocker', 'mockito']
        DebGrapher.packages_list['g2'] = ['mock2', 'mocker2', 'mockito2']

        deb = DebGrapher()

        self.assertListEqual(deb.get_packages(),
                             ['mock', 'mocker', 'mockito',
                              'mock2', 'mocker2', 'mockito2'])
        self.assertListEqual(deb.get_packages(group='g1'),
                             ['mock', 'mocker', 'mockito'])
        self.assertListEqual(deb.get_packages(group='g2'),
                             ['mock2', 'mocker2', 'mockito2'])

    def test_verify_graph_1(self):

        DebGrapher.packages_list = {}
        DebGrapher.packages_list['g1'] = ['mock1']
        DebGrapher.packages_list['g2'] = ['mock2']
        DebGrapher.packages = {}
        DebGrapher.packages['mock1'] = {}
        DebGrapher.packages['mock2'] = {}
        deb = DebGrapher()
        try:
            deb.verify_packages_tree()
        except SystemExit:
            self.fail("verify_packages_tree()\
raised SystemExit unexpectedly!")

    def test_verify_graph_2(self):
        DebGrapher.packages_list = {}
        DebGrapher.packages_list['g1'] = ['mock1', 'mocky']
        DebGrapher.packages_list['g2'] = ['mock2']
        DebGrapher.packages = {}
        DebGrapher.packages['mock1'] = {}
        DebGrapher.packages['mock2'] = {}
        deb = DebGrapher()
        with self.assertRaises(SystemExit):
            deb.verify_packages_tree()

    def test_verify_graph_3(self):
        DebGrapher.packages_list = {}
        DebGrapher.packages_list['g1'] = ['mock1']
        DebGrapher.packages_list['g2'] = ['mock2']
        DebGrapher.packages = {}
        DebGrapher.packages['mock1'] = {}
        DebGrapher.packages['mock2'] = {}
        DebGrapher.packages['mocky'] = {}
        deb = DebGrapher()
        with self.assertRaises(SystemExit):
            deb.verify_packages_tree()

    def test_verify_graph_4(self):
        DebGrapher.packages_list = {}
        DebGrapher.packages_list['g1'] = ['mock1']
        DebGrapher.packages_list['g2'] = ['mock2']
        DebGrapher.packages = {}
        DebGrapher.packages['mock1'] = {}
        DebGrapher.packages['mock1']['dependencies'] = ['mockito']
        DebGrapher.packages['mock2'] = {}
        deb = DebGrapher()
        with self.assertRaises(SystemExit):
            deb.verify_packages_tree()

    def test_get_dep(self):
        DebGrapher.packages_list = {}
        DebGrapher.packages_list['g1'] = ['mock1']
        DebGrapher.packages = {}
        DebGrapher.packages['mock1'] = {}
        DebGrapher.packages['mock1']['dependencies'] = ['mockito']
        DebGrapher.packages['mock2'] = {}
        deb = DebGrapher()
        self.assertListEqual(deb.get_dependencies('mock1'), ['mockito'])
        self.assertListEqual(deb.get_dependencies('mock2'), [])
        with self.assertRaises(SystemExit):
            deb.get_dependencies('mock3')

    def test_get_deep_dep(self):
        DebGrapher.packages_list = {}
        DebGrapher.packages_list['g1'] = ['mock1', 'mock2', 'mockito']
        DebGrapher.packages = {}
        DebGrapher.packages['mockito'] = {}
        DebGrapher.packages['mock1'] = {}
        DebGrapher.packages['mock1']['dependencies'] = ['mock2']
        DebGrapher.packages['mock2'] = {}
        DebGrapher.packages['mock2']['dependencies'] = ['mockito']
        deb = DebGrapher()
        self.assertListEqual(sorted(deb.get_deep_dependencies('mock1')),
                             sorted(['mock2', 'mockito']))

    def test_get_list_dep(self):
        DebGrapher.packages_list = {}
        DebGrapher.packages_list['g1'] = ['mock1', 'mock2', 'mockito']
        DebGrapher.packages = {}
        DebGrapher.packages['mockito'] = {}
        DebGrapher.packages['mock1'] = {}
        DebGrapher.packages['mock1']['dependencies'] = ['mock2']
        DebGrapher.packages['mock2'] = {}
        DebGrapher.packages['mock2']['dependencies'] = ['mockito']
        deb = DebGrapher()
        self.assertListEqual(sorted(deb.get_list_dependencies(['mock1', 'mock2'])),
                             sorted(['mock2', 'mockito']))

    def test_buld_order_1(self):
        DebGrapher.packages_list = {}
        DebGrapher.packages_list['g1'] = ['mock1', 'mock2', 'mockito']
        DebGrapher.packages = {}
        DebGrapher.packages['mockito'] = {}
        DebGrapher.packages['mock1'] = {}
        DebGrapher.packages['mock1']['dependencies'] = ['mock2']
        DebGrapher.packages['mock2'] = {}
        DebGrapher.packages['mock2']['dependencies'] = ['mockito']
        deb = DebGrapher()
        self.assertListEqual(
            deb.get_build_order(['mock1', 'mock2', 'mockito']),
            ['mockito', 'mock2', 'mock1'])

    def test_buld_order_2(self):
        DebGrapher.packages_list = {}
        DebGrapher.packages_list['g1'] = ['mock1', 'mock2', 'mockito']
        DebGrapher.packages = {}
        DebGrapher.packages['mockito'] = {}
        DebGrapher.packages['mockito']['dependencies'] = ['mock1']
        DebGrapher.packages['mock1'] = {}
        DebGrapher.packages['mock1']['dependencies'] = ['mock2']
        DebGrapher.packages['mock2'] = {}
        DebGrapher.packages['mock2']['dependencies'] = ['mockito']
        deb = DebGrapher()
        with self.assertRaises(SystemExit):
            deb.get_build_order(['mock1', 'mock2', 'mockito'])


if __name__ == '__main__':
    unittest.main()
