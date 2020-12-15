import sys 
sys.path.append('./')

from dimacs_parser import parse
from dtree_compiler import Dtree_Compiler

from dnnf_compiler import *
from graph_utils import *
import copy


cnf_file = './instances/foo.cnf'
clausal_form, nvars = parse(cnf_file, verbose=True)

dt_compiler = Dtree_Compiler(clausal_form.copy())
dtree = dt_compiler.el2dt([2,3,4,1])
dnnf_compiler = DNNF_Compiler(dtree)
dnnf = dnnf_compiler.compile()
print('Exporting nnf file...')
export_nnf_file('./instances/my_dnnf', dnnf)
print('Exporting dtree dot file...')
export_nnf_dot('./instances/my_dnnf')
dnnf.reset()

a = dnnf_compiler.create_trivial_node(5)

dnnf_smooth = copy.deepcopy(dnnf)
dnnf_smooth = dnnf_compiler.smooth(dnnf_smooth)
dnnf_smooth.reset()
print('Exporting smooth nnf file...')
export_nnf_file('./instances/my_dnnf_smooth', dnnf_smooth)
print('Exporting dot file...')
export_nnf_dot('./instances/my_dnnf_smooth')

dnnf_conditioning = copy.deepcopy(dnnf)
dnnf_conditioning = dnnf_compiler.conditioning(dnnf_conditioning,[1,2])
dnnf_conditioning.reset()
print('Exporting condintioning nnf file...')
export_nnf_file('./instances/my_dnnf_conditioning', dnnf_conditioning)
print('Exporting dot file...')
export_nnf_dot('./instances/my_dnnf_conditioning')

dnnf_conditioning.reset()
dnnf_simplified = dnnf_compiler.simplify(dnnf_conditioning)
# dnnf_simplified.reset()
print('Exporting simplified nnf file...')
export_nnf_file('./instances/my_dnnf_simplified', dnnf_simplified)
print('Exporting dot file...')
export_nnf_dot('./instances/my_dnnf_simplified')

dnnf_conjoin = copy.deepcopy(dnnf)
dnnf_conjoin = dnnf_compiler.conjoin(dnnf_conjoin,[1,2])
dnnf_conjoin.reset()
print('Exporting conjoin nnf file...')
export_nnf_file('./instances/my_dnnf_conjoin', dnnf_conjoin)
print('Exporting dot file...')
export_nnf_dot('./instances/my_dnnf_conjoin')

print('Instance is sat or not? ', dnnf_compiler.is_sat(dnnf))

dnnf_project = copy.deepcopy(dnnf)
dnnf_project = dnnf_compiler.project(dnnf_project,[1,2])
dnnf_project = dnnf_compiler.simplify(dnnf_project)
dnnf_project.reset()
print('Exporting projecting nnf file...')
export_nnf_file('./instances/my_dnnf_project', dnnf_project)
print('Exporting dot file...')
export_nnf_dot('./instances/my_dnnf_project')

print('Computing Min Card ... result = ', dnnf_compiler.MCard(dnnf))

dnnf_min = copy.deepcopy(dnnf_smooth)
dnnf_min = dnnf_compiler.minimize(dnnf_min)
print('Exporting min nnf file...')
export_nnf_file('./instances/my_dnnf_min', dnnf_min)
print('Exporting dot file...')
export_nnf_dot('./instances/my_dnnf_min')
print('End')

print('Enumerating all models ....')
models = dnnf_compiler.enumerate_models(dnnf)
for x in models:
    print(x)

print('Enumerating all models with smooth version ....')
models = dnnf_compiler.enumerate_models(dnnf_smooth)
for x in models:
    print(x)
