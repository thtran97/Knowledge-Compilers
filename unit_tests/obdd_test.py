import sys
sys.path.append('./')

from obdd_compiler import BDD_Compiler
from dimacs_parser import parse
from graph_utils import export_dot_from_bdd
clausal_form, nvars = parse('./instances/toto.cnf', verbose=True)

compiler = BDD_Compiler(nvars)
obdd = compiler.compile(clausal_form)
obdd.print_info(nvars)
export_dot_from_bdd('./instances/toto.dot', obdd, nvars)

print('End')
