import unittest

from code_manager.utils import flatten
from code_manager.utils import merge_two_dicts


class TestDown(unittest.TestCase):

    def test_flatten(self):
        arr = [[1, 2, 3], [4], 5, 6, [7, 8, [9]]]
        res = flatten(arr)
        self.assertEqual(res, [1, 2, 3, 4, 5, 6, 7, 8, 9])

    def test_merging_dlicts(self):
        dic1 = dict()
        dic2 = dict()
        dic1['val1'] = 'a'
        dic2['valb'] = 'b'
        res_should = dict()
        res_should['val1'] = 'a'
        res_should['valb'] = 'b'
        res = merge_two_dicts(dic1, dic2)
        self.assertDictEqual(res, res_should)


if __name__ == '__main__':
    unittest.main()
