import os
import unittest

from code_manager.utils.utils import flatten
from code_manager.utils.utils import merge_two_dicts
from code_manager.utils.utils import sanitize_input_variable
from code_manager.utils.utils import recursive_items


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

    def test_sanitize_input_variable(self):
        self.assertEqual(os.environ['HOME'], sanitize_input_variable('~'))
        self.assertEqual(os.environ['PATH'], sanitize_input_variable('$PATH'))

    def test_recursive_items(self):
        test_dict = {
            "key1": "item1",
            "key_1": {
                "key2": "item2",
                "key3": "item3",
                "key_2": {
                    "key4": "item4",
                    "key5": "item5"
                }
            },
            "key_3": {
                "key6": "item6",
                "key7": "item7"
            }
        }
        items = []
        for i in range(1, 8):
            items.append(('key{}'.format(i), 'item{}'.format(i)))

        gen_items = []
        for i in recursive_items(test_dict):
            gen_items.append(i)

        self.assertListEqual(items, gen_items)


if __name__ == '__main__':
    unittest.main()
