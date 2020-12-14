# Knowledge compilers

This repo is my Python-reimplementation of some known compilers.


### Core functions 

#### 1. cnf2ddnnf

- [X] dtree compiler : Compile a very simple and naive dtree from clausal form
- [X] d-DNNF compiler : Compiler to d-DNNF based on a dtree 

    - [x] Decision i.e. BCP
    - [x] Unit propagation => collect all implied literals 
    - [x] Undo decide => backtrack
    - [x] Recursive DPLL
    - [x] Compute separator of dtree t
    - [x] Recursive compiler 
    - [x] Key and cache ?

In this first version, I reimplemented a very simple complier which compile from CNF to d-DNNF. This implementations is based on the work described in [1]. 

#### 2. cnf2obdd

***In progress***


### References

- [1] A. Darwiche, “New advances in compiling cnf to decomposable negation normal form,” Front. Artif. Intell. Appl., vol. 110, pp. 318–322, 2004. 

- [2] A. Darwiche, “Decomposable negation normal form,” J. ACM, vol. 48, no. 4, pp. 608–647, 2001, doi: 10.1145/502090.502091.

- [3] A. Darwiche, “On the tractable counting of theory models and its application to truth maintenance and belief revision,” J. Appl. Non-Classical Logics, vol. 11, no. 1–2, pp. 11–34, 2001, doi: 10.3166/jancl.11.11-34.

- [4] A. Darwiche, “A compiler for deterministic, decomposable negation normal form,” Proc. Natl. Conf. Artif. Intell., pp. 627–634, 2002.

- [5] J. Huang and A. Darwiche, “Using DPLL for efficient OBDD construction,” Proc. ofthe Seventh Int. Conf. Theory Appl. ofSatisfiability Test., 2004, doi: 10.1007/11527695_13.