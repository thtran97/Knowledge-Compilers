import sys
sys.path.append('./')

from graph_utils import *
import unittest

class TestGraphUtils(unittest.TestCase):
    def test_export_nnf(self):
        nnf_test = './instances/foo.cnf'
        export_nnf_dot(nnf_test)

    def test_export_dtree(self):
        dtree_test = './instances/my_dtree'
        export_dtree_dot(dtree_test)

if __name__ == '__main__':
    unittest.main()