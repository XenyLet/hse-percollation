## hse-percollation
Repo for percollation task during HSE course. Model is implemented as described in article https://arxiv.org/abs/cond-mat/0005264

## Installation
1. Unpack archive
2. Install conda env or packets via pip (`conda env -f conda-env.yml` or `pip install -r requirements.txt`

## Run single experiment
Run main.py with following arguments:
- `-t` - type of percollation model. Alowed values are "NODE" or "BOND"
- `-s` - side size. Model field is square with side size s. Allowed values: [1; 99]
Optional args are
- `--vis` - turn on visualization of random nodes activation and clusters merging. If set, pause between elements activation is determined by `-p` arg
- `-p` (>0) - pause between activations in seconds, float. Set to something near 0 to speedup modelling 


## Percollation-vs-mesh-size experiment
In this experiment one can check dependency between mesh side size and number of active elements required for percollation
****
### Run
Change theese constants in code as needed:
```python
MESH_SIZES = list(range(5, 41, 5)) 
EXPERIMENTS_PER_SIZE = 1             
PROCESSES = 6                       
GUESS_POLYNOM_DEGREE = 2
``` 
- `MESH_SIZES` - list of mesh side lengths
- `EXPERIMENTS_PER_SIZE` - number of experiment reruns (with same mesh_size-percollation_type pair). Higher numbers increase accuracy
- `PROCESSES` - number of processes for multiprocessing experiments run
- `GUESS_POLYNOM_DEGREE` - at the end we guess that Percollation depends on mesh size as square-degree polynom

Then launch `percollation-vs-mesh_size.py`. 
