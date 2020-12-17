import copy
class BDD:
    def __init__(self, var, low, high):
        self.var = var
        self.low = low
        self.high = high
        self.explore_id = 0

    def is_sink(self):
        return self.low is None and self.high is None

    def _print_info(self, current_id, rank, output_file=None):

        if self.explore_id > 0:
            return current_id, rank

        if self.is_sink():
            if output_file is not None:
                out = open(output_file, 'a')
                if self.var == True:
                    out.write('     {} [label="True", color=green, shape=square];\n'.format(current_id+1))
                elif self.var == False:
                    out.write('     {} [label="False", color=red, shape=square];\n'.format(current_id+1))
                out.close()
            else:
                print('{}-SINK : {}'.format(current_id+1,self.var))
        else:
            left_current_id, rank = self.low._print_info(current_id, rank, output_file)
            current_id, rank = self.high._print_info(left_current_id, rank, output_file)
            if output_file is not None:
                out = open(output_file, 'a')
                out.write('     {} [label="{}"];\n'.format(current_id+1, self.var))
                out.write('     {} -> {} [style=dotted];\n'.format(current_id+1, self.low.explore_id))
                out.write('     {} -> {};\n'.format(current_id+1, self.high.explore_id))
                out.close()
            else:
                print('{}-Var: {}'.format(current_id+1,self.var))
        self.explore_id = current_id+1
        if self.is_sink():
            rank[0].append(self.explore_id)
        else:
            rank[self.var].append(self.explore_id) 
        return current_id+1, rank
    
    def print_info(self, nvars, output_file=None):
        rank = [[] for i in range(nvars+1)]
        _, rank = copy.deepcopy(self)._print_info(0, rank, output_file)
        # for i in range(len(rank)):
        #     print(i, ': ', rank[i])
        return rank

class BDD_Compiler:
    def __init__(self, n_vars):
        self.n_vars = n_vars
        self.unique = {}
        self.cache = {}
        self.F_SINK = BDD(False, None, None)
        self.T_SINK = BDD(True, None, None)

    def bcp(self, formula, literal):
        modified = []
        for clause in formula:
            if literal in clause:
                continue
            elif -literal in clause:
                c = [x for x in clause if x != -literal]
                if len(c) == 0:
                    return -1 
                modified.append(c)
            else:
                modified.append(clause)
        return modified

    # def unit_propagation(self, formula):
    #     assignment = []
    #     unit_clauses = [c for c in formula if len(c) == 1]
    #     while len(unit_clauses) > 0:
    #         unit = unit_clauses[0]
    #         formula = self.bcp(formula, unit[0])
    #         assignment += [unit[0]]
    #         if formula == -1:
    #             return -1, []
    #         if not formula: 
    #             return formula, assignment
    #         unit_clauses = [c for c in formula if len(c) == 1]
    #     return formula, assignment

    def compute_key(self):
        return 0

    def get_nodes(self, var, low, high):
        if low == high:
            return low
        if (var, low, high) in self.unique: # and low == self.unique[i].low and high == self.unique[i].high:
            return self.unique[(var, low, high)]
        result = BDD(var, low, high)
        self.unique[(var, low, high)] = result
        return result

    def cnf2obdd(self, clausal_form, i):
        
        if clausal_form == -1:
            return self.F_SINK
        elif len(clausal_form) == 0:
            return self.T_SINK
        
        assert i <= self.n_vars+1

        # key = self.compute_key()
        # if key in self.cache:
        #     return self.cache[key]

        # print('pick ', -i)
        low = self.cnf2obdd(self.bcp(clausal_form, -i), i+1)
        # print('pick ', i)
        high = self.cnf2obdd(self.bcp(clausal_form, i), i+1)
        # print('We had result on node ', i)
        result = self.get_nodes(i, low, high)
        # self.cache[key] = result
        return result

    def compile(self, clausal_form):
        return self.cnf2obdd(clausal_form, 1)
        

        
        
