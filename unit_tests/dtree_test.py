import sys
sys.path.append('./')

import numpy as np
from dimacs_parser import parse
from dtree_compiler import *
from graph_utils import *

clausal_form, nvars = parse('./instances/foo.cnf', True)
print(clausal_form)
dtree_compiler = Dtree_Compiler(clausal_form)
dtree = dtree_compiler.el2dt([2,3,4,1])
print(dtree.separators)
print(dtree.pick_most())
leaf = dtree.print_info([])
print(leaf)
assert dtree.separators == [1,4]
assert dtree.atoms == [1,2,3,4]
assert dtree.left_child.is_leaf()
assert dtree.is_full_binary()
for clause in clausal_form:
    assert clause in dtree.clauses
print('Exporting dtree file...')
export_dtree_file('./instances/my_dtree', dtree)
print('Exporting dtree dot file...')
export_dtree_dot('./instances/my_dtree')
print('End')