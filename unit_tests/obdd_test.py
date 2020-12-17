import sys
sys.path.append('./')

from obdd_compiler import BDD_Compiler
from dimacs_parser import parse
from graph_utils import export_dot_from_bdd

clausal_form, nvars = parse('./instances/toto.cnf', verbose=True)

# Using separator as key
print('================================================')
print('Using separator as key')
compiler = BDD_Compiler(nvars, clausal_form)
obdd = compiler.compile(key_type='separator')
obdd.print_info(nvars)

# Using cutset as key
print('================================================')
print('Using cutset as key')
compiler = BDD_Compiler(nvars, clausal_form)
obdd = compiler.compile(key_type = 'cutset')
obdd.print_info(nvars)

# Export dot file
export_dot_from_bdd('./instances/toto.dot', obdd, nvars)
print('End')
