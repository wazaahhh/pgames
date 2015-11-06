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
* *grids* is a .csv file with two columns : simul_step and a vector representing the state of the grid at a given simulation step. In most cases, on the initial and the last states are recorded, but there is an option to log the grid state every 100 changes. 
* *allmoves*: is a .csv file in which all changes are recorded. There are 7 types of ***changes*** with a variable number of column attributes. 
 
 
 
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
