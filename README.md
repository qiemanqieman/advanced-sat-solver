# <center>advanced-sat-solver</center>
## Description
A pure-python implemented SAT solver using CDCL equipped with several techniques, 
including VSIDS, LRB, CHB, MLR, UCB, NiVER and so on.

## Tested Environment
- Python 3.10

## Usage
```python main.py [-h] [-a {VSIDS,ERMA,RSR,LRB,CHB}] [-r {MLR}] [-b {UCB}] [-p {NiVER,lighter-NiVER,li-NiVER-withPLE}] [-i INPUT] [-discount D] [-alpha A] [-batch B]``` \
`python main.py` to run the solver with default settings.`python main.py -h` for more details. \
`python gui.py` to run with GUI.\
`python test.py` to generate test results in .csv file format.

### Arguments
``` 
  -h, --help            show this help message and exit
  --discount D          discount coefficient for decaying, default 0.95
  --alpha A             step-size coefficient for algorithms based on ERMA, default 0.4
  -batch A              batch parameter used in LRB algorithm, default 10
  -a {VSIDS,ERWA,RSR,LRB,CHB}, --assignment-algorithm {VSIDS,ERWA,RSR,LRB,CHB}
                        Case-insensitive, heuristic branching algorithm for assigning next literal, default VSIDS
  -i INPUT, --input INPUT
                        specify the CNF file needed to be solved, default and1.cnf
  -r {MLR}, --restart-policy {MLR}
                        specify the restart policy, default to be None
  -p {NiVER,lighter-NiVER,li-NiVER-withPLE}, --preprocess-policy {NiVER,lighter-NiVER,li-NiVER-withPLE}
                        specify the preprocess policy, default to be None
  -b {UCB}, --bandit {UCB}
                        specify the heuristic changing policy, default to be None
                  
```

### Example
```python main.py -a LRB -i ./examples/bmc-1.cnf```
![img.png](results/rsr-bmc-1.png)

## Test results during implementation
The following are just phased test results for our own reference during implementation. 
If you want to see the final experiment results, please refer to the file results/timeTestResult.csv.
### without restart
| File                      | VSIDS  | ERMA   | RSR    | LRB    | CHB    |
|---------------------------|--------|--------|--------|--------|--------|
| bcm-1.cnf                 | 8.546s | 10.34s | 4.101s | 19.47s | 25.24s |
| bcm-2.cnf                 | 0.089s | 0.085s | 0.127s | 0.052s | 0.085s |
| bcm-7.cnf                 | 0.260s | 0.210s | 0.215s | 0.214s | 0.332s |
| good-16-vars.cnf          | 3.259s | 2.934s | 3.012s | 3.067s | 2.970s |
| bad-12-vars.cnf (`UNSAT`) | 3.866s | 2.704s | 3.558s | 2.991s | 1.507s |

### with restart(MLR)

| File                      | VSIDS  | ERMA   | RSR    | LRB    | CHB    |
|---------------------------|--------|--------|--------|--------|--------|
| bcm-1.cnf                 | 56.45s | 45.21s | 40.33s | 30.19s | 54.91s |
| bcm-2.cnf                 | 0.091s | 0.164s | 0.136s | 0.052s | 0.635s |
| bcm-7.cnf                 | 0.253s | 0.212s | 0.247s | 0.221s | 1.570s |
| good-16-vars.cnf          | 2.397s | 2.493s | 2.432s | 2.536s | 2.582s |
| bad-12-vars.cnf (`UNSAT`) | 3.182s | 3.412s | 3.367s | 3.385s | 2.496s |

### preprocess(NiVER)
(VSIDS + MLR)

| File                      | with lighter-NiVER         | without preprocess |
|---------------------------|----------------------------|--------------------|
| bcm-1.cnf                 | 3.91s(pre) + 10.62s(cdcl)  | 57.50s             |
| bcm-2.cnf                 | 0.35s + 0.059s             | 0.080s             | 
| bcm-7.cnf                 | 1.968s + 0.035s            | 0.289s             |

## Further reading
Some links for the details of all kinds of algorithms used
in this project.

### ERMA & RSR & LRB
Full paper can be read [online ](https://link.springer.com/chapter/10.1007/978-3-319-40970-2_9)


### CHB
Full paper can be downloaded from [here](https://dl.acm.org/doi/10.5555/3016100.3016385)

### MLR (machine learning-based restart)
Full paper can be read [online](https://link.springer.com/chapter/10.1007/978-3-319-94144-8_6)

### UCB (Upper Confidence Bound)
Full paper can be downloaded from [here](https://drops.dagstuhl.de/opus/volltexte/2021/15311/)

### NiVER (Non Increasing Variable Elimination Resolution)
Full paper can be downloaded from [here](http://www.satisfiability.org/SAT04/programme/118.pdf)