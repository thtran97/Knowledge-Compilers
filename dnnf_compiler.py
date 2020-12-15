import numpy as np
import copy

class DNF_Node:
    def __init__(self, node_type, left_child=None, right_child=None, literal=None, conflict_atom=None):
        assert node_type == 'A' or node_type == 'O' or node_type == 'L'
        self.type = node_type # A, O or L
        self.left_child = left_child
        self.right_child = right_child 
        self.literal = literal
        self.conflict_atom = conflict_atom
        
        self.explore_id = None

        self.atoms = None
        self.models = None

        if self.type == 'L':
            assert self.literal is not None
            assert self.left_child is None
            assert self.right_child is None
            self.atoms = [abs(literal)]
        elif self.type == 'O' or self.type == 'A':
            assert self.literal is None
            assert self.left_child is not None 
            assert self.right_child is not None
            self.atoms = list(set(self.left_child.atoms).union(self.right_child.atoms))

    def count_node(self, current_id):
        if self.explore_id is not None:
            return current_id
        if self.type != 'L':    
            current_id = self.left_child.count_node(current_id)
            current_id = self.right_child.count_node(current_id)
        self.explore_id = current_id
        return current_id + 1

    def count_edge(self):
        if self.type == 'L':
            return 0
        else:
            return self.left_child.count_edge() + self.right_child.count_edge() + 2

    def collect_var(self):
        if self.type == 'L':
            return [abs(self.literal)]
        else:
            return list(set(self.left_child.collect_var()).union(self.right_child.collect_var()))
    
    def print_nnf(self, current_id, output_file=None):
        if output_file is not None:
            out = open(output_file,'a')

        if self.explore_id is not None:
            return current_id

        if self.type == 'L':
            if output_file is not None:
                out.write('L {}\n'.format(self.literal))    
                out.close() 
            else:
                print('{} L {}'.format(current_id, self.literal))
        else:
            current_id = self.left_child.print_nnf(current_id, output_file)
            current_id = self.right_child.print_nnf(current_id, output_file)
            if self.type == 'A':
                if output_file is not None:
                    out.write('A 2 {} {}\n'.format(self.left_child.explore_id, self.right_child.explore_id))
                    out.close()
                else:
                    print('{} A 2 {} {}'.format(current_id, self.left_child.explore_id, self.right_child.explore_id))    
            if self.type == 'O':
                if output_file is not None:
                    out.write('O {} 2 {} {}\n'.format(self.conflict_atom, self.left_child.explore_id, self.right_child.explore_id))
                    out.close()
                else:
                    print('{} O {} 2 {} {}'.format(current_id, self.conflict_atom, self.left_child.explore_id, self.right_child.explore_id))
        self.explore_id = current_id
        return current_id + 1

    def reset(self):
        self.explore_id = None
        if self.type != 'L':
            self.left_child.reset()
            self.right_child.reset()
    # '''
    # Queries and transformation
    # '''
    # def conditioning(self, instanciation):
    #     if self.explore_id != 1:
    #         assert type(self.literal) is not bool
    #         if self.type == 'L':
    #             if self.literal in instanciation:
    #                 self.literal = True
    #             elif -self.literal in instanciation:
    #                 self.literal = False
    #         else:
    #             self.left_child.conditioning(instanciation)
    #             self.right_child.conditioning(instanciation)
    #         self.explore_id = 1

    
    # def conjoin(self, instanciation):
    #     return DNF_Node(node_type='A', left_child=self.conditioning(instanciation), right_child=create_term_node(term=instanciation))

class DNNF_Compiler:
    def __init__(self, dtree):
        self.dtree = dtree 
        self.cache = {}
        self.cache_lit = {}
        self.ddnnf = None

    '''
    These functions take a dtree as input
    Export a new dtree
    '''
    def bcp(self, dtree, literal):
        modified = copy.deepcopy(dtree)
        if modified.is_leaf():
            # print(literal)
            # print(dtree.clauses)
            if len(modified.clauses) == 0:
                return modified

            leaf_clause = modified.clauses[0]
            if literal in leaf_clause:
                modified.clauses = []
                modified.atoms = []
                modified.clause_key = [1]
                modified.lit_key += 2**(abs(literal)-1)
            elif -literal in leaf_clause:
                modified_clause = [l for l in leaf_clause if l != -literal]
                modified.clauses[0] = modified_clause
                if len(modified.clauses[0]) == 0:
                    modified.atoms = []
                    return -1 ## CONFLICT !!!
                modified.atoms = [abs(l) for l in modified.clauses[0]]
                modified.clause_key = [0]
                modified.lit_key += 2**(abs(literal)-1)
        else:
            modified.left_child = self.bcp(modified.left_child, literal)
            modified.right_child = self.bcp(modified.right_child, literal) 
            modified.atoms = list(set(modified.left_child.atoms).union(modified.right_child.atoms))
            modified.separators = list(set(modified.left_child.atoms).intersection(modified.right_child.atoms))
            modified.clauses = modified.left_child.clauses + modified.right_child.clauses 
            modified.clause_key = modified.left_child.clause_key + modified.right_child.clause_key
            modified.lit_key += 2**(abs(literal)-1)
        return modified

    # def pure_literals(dtree):
    #     counter = dtree.get_counter()
    #     pure_assignment = []
    #     for l in counter:
    #         if -l not in counter:
    #             pure_assignment.append(l)
        
    #     for l in pure_assignment:
    #         dtree = bcp(dtree, l)
    #     return dtree, pure_assignment
        
    def unit_propagation(self, dtree):
        modified = copy.deepcopy(dtree)
        unit_assignment = []
        unit_clauses = [c for c in modified.clauses if len(c) == 1]
        while len(unit_clauses) > 0: 
            unit = unit_clauses[0][0]
            modified = self.bcp(modified, unit)
            unit_assignment.append(unit)
            if modified == -1: 
                return -1, []
            elif len(modified.clauses) == 0:
                return modified, unit_assignment
            unit_clauses = [c for c in modified.clauses if len(c) == 1]
        return modified, unit_assignment

    '''
    Compose some subtree into a new tree with declared node type (O or A)
    i.e we do not compose leaves but only compose AND or OR of defined nodes
    '''
    def compose(self, node_type, list_tree, conflict=None):
        assert node_type != 'L'
        assert len(list_tree) > 0
        list_tree = [t for t in list_tree if t is not None]
        if len(list_tree) == 0:
            return None
        
        if len(list_tree) == 1:
            composed_node = list_tree[0]
        else:
            if conflict is not None:
                right_composed_node = self.compose(node_type, list_tree[1:], conflict[1:])
                composed_node = DNF_Node(node_type=node_type, left_child=list_tree[0], right_child=right_composed_node, conflict_atom=conflict[0])
            else:    
                right_composed_node = self.compose(node_type, list_tree[1:])
                composed_node = DNF_Node(node_type=node_type, left_child=list_tree[0], right_child=right_composed_node)
        return composed_node

    def create_term_node(self, term):
        if len(term) == 0:
            return None
        else: 
            leaves = []
            for literal in term:
                if literal not in self.cache_lit:
                    leaf_node = DNF_Node(node_type='L', literal=literal)
                    leaves.append(leaf_node)
                    self.cache_lit[literal] = leaf_node
                else:
                    leaves.append(self.cache_lit[literal])
            return self.compose(node_type='A', list_tree=leaves)

    def clause2ddnnf(self, dtree):
        if len(dtree.atoms) == 0:
            return None
        clause = dtree.clauses[0]
        assert len(clause) > 0
        nodes = []
        conflict = []

        for i in range(len(clause)):
            # li= [DNF_Node(node_type='L',literal=clause[i])]
            # not_lj = [DNF_Node(node_type='L',literal=-clause[j]) for j in range(i)]
            li, list_not_lj = [], []
            if clause[i] in self.cache_lit:
                li.append(self.cache_lit[clause[i]])
            else: 
                li.append(DNF_Node(node_type='L',literal=clause[i]))
                self.cache_lit[clause[i]] = li[0]

            for j in range(i):
                if -clause[j] in self.cache_lit:
                    not_lj = self.cache_lit[-clause[j]]
                else:
                    not_lj = DNF_Node(node_type='L', literal=-clause[j])
                    self.cache_lit[-clause[j]] = not_lj
                list_not_lj.append(not_lj)

            choice = self.compose(node_type='A', list_tree=li+list_not_lj)
            nodes.append(choice)   
            conflict.append(clause[i])
        return self.compose(node_type='O', list_tree=nodes, conflict=conflict)


    def cnf2aux(self, dtree):
        if dtree.is_leaf():
            return self.clause2ddnnf(dtree)
        else:
            l_key = dtree.lit_key
            c_key = 0
            for i, v in enumerate(dtree.clause_key):
                c_key += v*(2**i) 
            if l_key in self.cache and c_key in self.cache[l_key]:
                print('Using cache !')
                return self.cache[l_key][c_key]
            else:
                r = self.cnf2ddnnf(dtree)
                if r != False and r is not None:
                    if self.cache is None:
                        self.cache = {}
                    if l_key not in self.cache:
                        self.cache[l_key] = {}
                    self.cache[l_key][c_key] = r
                return r
    '''
    Core function of compiler
    '''
    def cnf2ddnnf(self, dtree): 
        # if dtree.is_leaf():
        #     return clause2ddnnf(dtree)    
        dtree, unit_assignment = self.unit_propagation(dtree)
        if dtree == -1: 
            return False
        term_node = self.create_term_node(unit_assignment)
        sep = dtree.separators
        if sep is None or len(sep) == 0 : 
            left_node = self.cnf2aux(dtree.left_child)
            right_node = self.cnf2aux(dtree.right_child)
            return self.compose(node_type='A',list_tree=[term_node, left_node ,right_node])
        else:
            v = dtree.pick_most()
            print('Pick ', v)
            p = self.cnf2ddnnf(self.bcp(dtree, v))
            if not p:
                return self.cnf2ddnnf(self.bcp(dtree,-v))
            print('Pick ', -v)
            n = self.cnf2ddnnf(self.bcp(dtree, -v))
            if not n:
                return self.cnf2ddnnf(self.bcp(dtree,v))
            
            if v in self.cache_lit:
                v_node = self.cache_lit[v]
            else:
                v_node = DNF_Node('L',literal=v)
                self.cache_lit[v] = v_node
            if -v in self.cache_lit:
                not_v_node = self.cache_lit[-v]
            else:
                not_v_node = DNF_Node('L',literal=-v)
                self.cache_lit[-v] = not_v_node
            p_node = self.compose(node_type='A', list_tree=[v_node, p])
            n_node = self.compose(node_type='A', list_tree=[not_v_node, n])
            t_node = DNF_Node(node_type='O', left_child=p_node, right_child=n_node, conflict_atom=abs(v))
            # t_node = compose(node_type='O', list_tree=[p_node, n_node])
            return self.compose(node_type='A', list_tree=[term_node, t_node])

    def compile(self):
        self.ddnnf = self.cnf2ddnnf(self.dtree)
        return copy.deepcopy(self.ddnnf)

    '''
    Queries and transformation
    '''

    def conditioning(self, dnnf, instanciation):
        if dnnf.explore_id is None:
            assert type(dnnf.literal) is not bool
            if dnnf.type == 'L':
                if dnnf.literal in instanciation:
                    dnnf.literal = True
                elif -dnnf.literal in instanciation:
                    dnnf.literal = False
            else:
                dnnf.left_child = self.conditioning(dnnf.left_child, instanciation)
                dnnf.right_child = self.conditioning(dnnf.right_child, instanciation)
            dnnf.explore_id = 1
        return dnnf

    def conjoin(self, dnnf, instanciation):
        return DNF_Node(node_type='A', left_child=self.simplify(self.conditioning(dnnf, instanciation)), right_child=self.create_term_node(instanciation))

    def simplify(self, dnnf): 
        if dnnf.type == 'L':
            return dnnf            
        elif dnnf.type == 'O':
            dnnf.left_child = self.simplify(dnnf.left_child)
            dnnf.right_child = self.simplify(dnnf.right_child)
            if dnnf.left_child.literal == True:
                return dnnf.left_child
            elif dnnf.right_child.literal == True:
                return dnnf.right_child
            elif dnnf.left_child.literal == False:
                return dnnf.right_child
            elif dnnf.right_child.literal == False:
                return dnnf.left_child
            else:
                return dnnf
        elif dnnf.type == 'A':
            dnnf.left_child = self.simplify(dnnf.left_child)
            dnnf.right_child = self.simplify(dnnf.right_child)
            if dnnf.left_child.literal == True and dnnf.right_child.literal == True:
                return dnnf.left_child
            elif dnnf.left_child.literal == False:
                return dnnf.left_child
            elif dnnf.right_child.literal == False:
                return dnnf.right_child
            else:
                return dnnf

    def is_sat(self, dnnf):
        if dnnf.type == 'L':
            if dnnf.literal == False:
                return False
            else: 
                return True

        elif dnnf.type == 'O':
            return self.is_sat(dnnf.left_child) or self.is_sat(dnnf.right_child)

        elif dnnf.type == 'A':
            return self.is_sat(dnnf.left_child) and self.is_sat(dnnf.right_child)
    
    def project(self, dnnf, atoms):
        if dnnf.type == 'L':
            if type(dnnf.literal) is not bool:
                if abs(dnnf.literal) not in atoms:
                    dnnf.literal = True
        else: 
            dnnf.left_child = self.project(dnnf.left_child, atoms)
            dnnf.right_child = self.project(dnnf.right_child, atoms)
        return dnnf

    def MCard(self, dnnf):
        if dnnf.type ==  'L':
            if type(dnnf.literal) is bool:
                if dnnf.literal == True:
                    return 0
                else:
                    return np.inf
            else:
                if dnnf.literal > 0:
                    return 0
                else: 
                    return 1
        elif dnnf.type == 'O':
            return min(self.MCard(dnnf.left_child), self.MCard(dnnf.right_child))
        elif dnnf.type == 'A':
            return self.MCard(dnnf.left_child) + self.MCard(dnnf.right_child)

    def minimize(self, dnnf):
        if dnnf.type == 'L':
            return dnnf
        elif dnnf.type == 'A':
            dnnf.left_child = self.minimize(dnnf.left_child)
            dnnf.right_child = self.minimize(dnnf.right_child)
            if dnnf.left_child is None:
                return dnnf.right_child
            elif dnnf.right_child is None:
                return dnnf.left_child
            return dnnf
        elif dnnf.type == 'O':
            mcard = self.MCard(dnnf)
            left_mcard = self.MCard(dnnf.left_child)
            right_mcard = self.MCard(dnnf.right_child)
            if left_mcard != mcard and right_mcard != mcard:
                return None
            elif left_mcard == mcard and right_mcard != mcard:
                return self.minimize(dnnf.left_child)
            elif left_mcard != mcard and right_mcard == mcard:
                return self.minimize(dnnf.right_child)
            else:
                dnnf.left_child = self.minimize(dnnf.left_child)
                dnnf.right_child = self.minimize(dnnf.right_child)
                return dnnf

    def create_trivial_node(self, atom):
        if atom in self.cache_lit:
            p = self.cache_lit[atom]
        else:
            p = DNF_Node('L',literal=atom)
            self.cache_lit[atom] = p
        if -atom in self.cache_lit:
            n = self.cache_lit[-atom]
        else:
            n = DNF_Node('L',literal= -atom)
            self.cache_lit[-atom] = n
        return DNF_Node('O', left_child=p, right_child=n, conflict_atom=abs(atom))

    def smooth(self, dnnf):
        if dnnf.type == 'L':
            pass
        elif dnnf.type == 'A':
            dnnf.left_child = self.smooth(dnnf.left_child)
            dnnf.right_child = self.smooth(dnnf.right_child)
        elif dnnf.type == 'O':    
            atoms = dnnf.atoms
            not_atoms_left = list(set(dnnf.left_child.atoms)^set(atoms))
            not_atoms_right = list(set(dnnf.right_child.atoms)^set(atoms))
            if len(not_atoms_left) > 0:
                print('Left node is not smooth')
                trivial_nodes = [self.create_trivial_node(l) for l in not_atoms_left]
                dnnf.left_child = self.compose(node_type='A', list_tree=[dnnf.left_child]+trivial_nodes)
                dnnf.left_child.atoms = atoms
            if len(not_atoms_right) > 0:
                print('Right node is not smooth')
                trivial_nodes = [self.create_trivial_node(l) for l in not_atoms_right]
                dnnf.right_child = self.compose(node_type='A', list_tree=[dnnf.right_child]+trivial_nodes)
                dnnf.right_child.atoms = atoms
            dnnf.left_child = self.smooth(dnnf.left_child)
            dnnf.right_child = self.smooth(dnnf.right_child)
        return dnnf    

    def enumerate_models(self, dnnf):
        if dnnf.type == 'L':
            if type(dnnf.literal) is bool:
                if dnnf.literal == True:
                    return [[]]
                else:
                    return []
            else:
                return [[dnnf.literal]]
        elif dnnf.type == 'O':
            return self.union_models(self.enumerate_models(dnnf.left_child), self.enumerate_models(dnnf.right_child))
        elif dnnf.type == 'A':
            return self.multiply_models(self.enumerate_models(dnnf.left_child), self.enumerate_models(dnnf.right_child))

    def union_models(self, l1, l2):
        l = l1.copy()
        for item in l2:
            if item not in l1:
                l.append(item)
        return l

    def multiply_models(self, l1, l2):
        l = []
        for item_A in l1:
            for item_B in l2:
                l.append(list(set(item_A).union(item_B)))
        return l

