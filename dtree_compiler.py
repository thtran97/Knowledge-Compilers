class Node:
    def __init__(self, node_id = None, left_child = None, right_child = None, clause = None):
        self.node_id = None
        self.left_child = None
        self.right_child = None
        self.clauses = None
        self.atoms = None
        self.separators = None
        
        if node_id is not None:
            self.node_id = node_id
        if left_child is not None:
            self.left_child = left_child
        if right_child is not None:
            self.right_child = right_child
        if clause is not None:
            # This implies this node is a leaf
            self.clauses = [clause]
            self.atoms = [abs(l) for l in clause]
            if len(clause) == 0:
                self.clause_key = [1]
            else:
                self.clause_key = [0]
        if self.left_child is not None and self.right_child is not None:
            # In case of internal node
            # atoms(t) = atoms(t_left) union atoms(t_right)
            self.clauses = self.left_child.clauses + self.right_child.clauses 
            self.atoms = list(set(self.left_child.atoms).union(self.right_child.atoms))
            self.separators = list(set(self.left_child.atoms).intersection(self.right_child.atoms))
            self.clause_key = self.left_child.clause_key + self.right_child.clause_key
        
        # self.cache = None
        self.lit_key = 0

    
    def is_leaf(self):
        return self.left_child is None and self.right_child is None

    def is_full_binary(self):
        if self.is_leaf():
            return True
        elif self.left_child is None and self.right_child is not None:
            return False
        elif self.left_child is not None and self.right_child is None:
            return False
        else:
            return (self.left_child.is_full_binary() and self.right_child.is_full_binary())

    def get_counter(self):
        counter = {}
        for clause in self.clauses:
            for literal in clause:
                if literal in counter:
                    counter[literal] += 1
                else:
                    counter[literal] = 1
        return counter

    def pick_most(self):
        '''
        Pick a variable with the most occurences in separator
        '''
        counter = self.get_counter()
        sep_counter = {s:0 for s in self.separators}
        for key in counter.keys():
            if abs(key) in self.separators:
                sep_counter[abs(key)] += counter[key]
        sort_counter = sorted(sep_counter, key=sep_counter.get, reverse=True)
        # print(sep_counter)
        return sort_counter[0]

    def print_info(self, leaf, output_file=None):
        if output_file is not None:
            out = open(output_file, 'a')

        if self.is_leaf():
            if output_file is not None:
                out.write('L {0}\n'.format(self.node_id))
                out.close()
            else:
                print('L ', self.node_id)
            leaf.append(self.node_id)
        else:
            leaf = self.left_child.print_info(leaf, output_file)
            leaf = self.right_child.print_info(leaf, output_file)
            left_child_pos = self.left_child.node_id
            right_child_pos = self.right_child.node_id
            if self.left_child.node_id in leaf:
                left_child_pos = leaf.index(self.left_child.node_id)
            if self.right_child.node_id in leaf:
                right_child_pos = leaf.index(self.right_child.node_id)
            if output_file is not None:
                out.write('I {0} {1}\n'.format(left_child_pos, right_child_pos))
                out.close()
            else:
                print('I ', left_child_pos, right_child_pos)
        return leaf

class Dtree_Compiler:
    
    def __init__(self, clausal_form):
        self.node_id = 0
        self.clausal_form = clausal_form

    def compose(self, list_tree):
        assert len(list_tree) > 0
        if len(list_tree) == 1:
            composed_node = list_tree[0]
        elif len(list_tree) == 2:
            composed_node = Node(node_id=self.node_id, left_child=list_tree[0], right_child=list_tree[1])
            self.node_id += 1
        else:
            right_composed_node = self.compose(list_tree[1:])
            composed_node = Node(node_id=self.node_id, left_child=list_tree[0], right_child=right_composed_node)
            self.node_id += 1 
        return composed_node

    def el2dt(self, ordering):
        '''
        Construct a dtree accoding to given ordering of atoms
        '''
        sigma = []
        for clause in self.clausal_form:
            leaf = Node(node_id=self.node_id, clause=clause)
            self.node_id += 1
            sigma.append(leaf)
        
        for lit in ordering:
            T = []
            for node in sigma: 
                if lit in node.atoms:
                    T.append(node)
            if len(T) > 0:
                composed_node = self.compose(T)
                sigma = list(set(sigma)^set(T))
                sigma.append(composed_node) 

        return self.compose(sigma)

    
