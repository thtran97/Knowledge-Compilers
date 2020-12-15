import sys
sys.path.append('./')

from graph_utils import *

nnf_test = './instances/foo.cnf.nnf'
export_nnf_dot(nnf_test)

dtree_test = './instances/foo_dtree'
export_dtree_dot(dtree_test)