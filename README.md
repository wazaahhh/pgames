# pgames
Public good game agent-based simulations


# Storage

All simulations files are stored as compressed json files (.json.zlib) on S3. The simulation parameters are embedded in the filename, e.g.:

iter_200_l_50_h_50_d_0.500_cl_0.500_ns_4_il_1.000_q_0.000_M_5_m_0.000_s_0.0000_0_5936d.json

with 

* iter : iterations
* l : grid length
* h : grid height
* d : grid density
* cl : initial cooperation level
* ns : neighbors to play with
* il : (strategy) imitation likelihood
* q : likelihood of reset strategy
* M : migration range
* m : probability of random migration
* s : probability of property violation

Simulations performed for  visualization purposes (grids = 50 x 50, 200 iterations) have the same format. As for now, only simulations files produced for the purpose of visualization can be downloaded.

# File format
The json file is a dictionary with three keys: 

* *summary* is a .csv file with the following columns: simul_step,completion,coop_level,cooperators,defectors,empty. A line is produced every 100 changes in the simulation (regardless of the number of iterations necessary for these 100 changes).

```
simul_step,completion,coop_level,cooperators,defectors,empty
0,0.000,0.484,628,670,1202
187,0.000,0.482,625,673,1202
449,0.001,0.473,614,684,1202
669,0.001,0.468,608,690,1202
899,0.002,0.463,601,697,1202

```

* *grids* is a .csv file with two columns : simul_step and a vector representing the state of the grid at a given simulation step. In most cases, on the initial and the last states are recorded, but there is an option to log the grid state every 100 changes. 

```
0:[0,-1,-1,-1,0,-1,-1,-1,1,0, ... ]
187:[0,-1,-1,-1,0,-1,-1,-1,1,0, ... ] 
449:[0,-1,-1,-1,0,-1,-1,-1,-1,-1, ... ]  
669:[0,-1,-1,-1,0,0,-1,-1,-1,-1, ... ]
899:[-1,-1,-1,-1,0,0,-1,-1,-1,-1, ... ]
1095:[-1,-1,-1,-1,0,0,-1,-1,-1,1,1,-1, ... ]
1296:[-1,-1,-1,-1,0,0,-1,-1,-1,1,1,-1,-1,... ]
1496:[-1,-1,-1,-1,0,0,-1,-1,-1,1,1,-1,... ]
1736:[-1,-1,1,1,0,0,-1,-1,-1,1,1,-1,-1,1, ... ]
```

* *allmoves*: is a .csv file in which all changes are recorded. There are 7 types of ***changes*** with a variable number of column attributes. 
 
```
51,628,670,1202,M,9,27,8,29,1,2,2.23607
55,628,670,1202,M,7,2,3,6,0,2.5,5.65685
56,628,670,1202,M,22,23,21,21,1,2,2.23607
58,628,670,1202,M,2,39,2,38,0,1.1,1
59,628,670,1202,M,14,38,14,36,0,1.3,2
59,629,669,1202,U,14,36,0,1,2.8,3
60,629,669,1202,M,46,31,46,28,1,2,3
62,629,669,1202,M,18,45,18,44,0,1.3,1
64,629,669,1202,M,13,6,13,9,0,1.4,3
``
 
## Description of *allmoves*  columns:

The 4 first columns are common to all types of ***changes*** : *iteration*,*number of cooperators*, *number of defectors*, *number of non empty sites* (should be invariable and the sum of the 2 formers). 

The 5th column is the type of ***change***, 

Change Symbol | Description
------------- | ----------- 
U | strategy update 
R | reset strategy
M | success-driven mobility
RM| random migration
E| success-driven property violation (Expell)
FM| forced mobility
RE| random property violation expell

with their own attributes as additional columns. The following tables provide an ordered description of each additional column:

* Strategy update (U):

Column | Attribute Description
------------- | ----------- 
Col. 1 | coordinate x 
Col. 2 | coordinate y
Col. 3 | old strategy
Col. 4 | new strategy
Col. 5 | old payoff
Col. 6 | new (highest expected) payoff


* Strategy reset (R):

Column | Attribute Description
------------- | ----------- 
Col. 1 | coordinate x 
Col. 2 | coordinate y
Col. 3 | old strategy
Col. 4 | new strategy


* Success-driven mobility (M), random migration (RM), success-driven property violation (E), forced mobility (FM), and random property violation expell (RE):

Column | Attribute Description
------------- | ----------- 
Col. 1 | coordinate x 
Col. 2 | coordinate y
Col. 3 | new coordinate x
Col. 4 | new coordinate y
Col. 5 | strategy (unchanged but logged to ease data analysis)
Col. 6 | payoff increase (respectively decrease in unfavorable cases of forced move)
Col. 7 | migration shortest distance
