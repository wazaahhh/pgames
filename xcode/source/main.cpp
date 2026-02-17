#include <iostream>
#include <fstream>
//#include <cstdlib>
#include <stdlib.h>
#include <time.h>
#include <iterator>
#include <vector>
#include <cmath>

#include <boost/program_options.hpp>

#define STRINGIFY(a) #a

namespace po = boost::program_options;


using namespace std;

// Build and parameters for populating the grid
int l;// = 49;
int h;// = 49;
vector< vector<int> > grid;//(l, vector<int>(h));

string grid_load_filename;

float grid_density;// = 0.50;
float init_coop_level;// = 0.50;
int cooperators,defectors,empty;

// Set up neighborhood
int numNeighbors;// = 4;
vector<int> nghb_h;//(numNeighbors);
vector<int> nghb_l;//(numNeighbors);


// Players
int focal_player_l,focal_player_h;
int player2_l,player2_h;

// Prisoner's Dilemma Constants and Variables
float T;// = 1.3;
float R;// = 1.0;
float P;// = 0.1;
float S;// = 0.0;

int strategy_focal_player;
float payoff_focal_player;

// Strategy update parameters
string update_style = "Dirk"; // warning : I've commented out the Fermi update function

float noise;// = 0.000;
float imitation_likelihood;
//float imitation_r;// = 1- imitation_likelihood;
float reset_strategy_likelihood;// = noise;

float fermi_temperature;// = 0.1;

// Migration parameters
int migration_range;// = 5;
float random_migration;// = 0;
float expell_likelihood;// = 0.01;

int n_migration_sites;// = (2*migration_range + 1)*(2*migration_range + 1) - 1;
vector<int> migration_array_l;//(n_migration_sites);
vector<int> migration_array_h;//(n_migration_sites);

// Simulation Parameters;

int verbose;// = 1;
int iterations;
int save_grids;

int MCS;// = l*h*iterations;//static_cast<const int>(l)*static_cast<const int>(h)*static_cast<const int>(iterations);

vector<int> rand_steps_l;//(MCS);
vector<int> rand_steps_h;//(MCS);
int current_step;
int count_changes = 1;

int chosen_migration_site;

ofstream output_all_mv;
ofstream output_summary;
ofstream output_grid_states;
string summary;

bool fileExists(string fileName)
{
    ifstream infile(fileName);
    return infile.good();
}


void prepare_parameters() {
    MCS = l*h*iterations;
    grid.resize(l, vector<int>(h));
    rand_steps_l.resize(MCS);
    rand_steps_h.resize(MCS);
    nghb_h.resize(numNeighbors);
    nghb_l.resize(numNeighbors);
    n_migration_sites = (2*migration_range + 1)*(2*migration_range + 1) - 1;
    migration_array_l.resize(n_migration_sites);
    migration_array_h.resize(n_migration_sites);
    }

// Output;

void open_output_files(){
    char Buffer[500];
    string str;
    int length = 0;
    length += sprintf(Buffer+length, "iter_%d",iterations);
    length += sprintf(Buffer+length, "_l_%d",l);
    length += sprintf(Buffer+length, "_h_%d",h);
    length += sprintf(Buffer+length, "_d_%0.3f", grid_density);
    length += sprintf(Buffer+length, "_cl_%0.3f",init_coop_level);
    length += sprintf(Buffer+length, "_ns_%d",numNeighbors);
    length += sprintf(Buffer+length, "_il_%0.3f",imitation_likelihood);
    length += sprintf(Buffer+length, "_q_%0.3f",reset_strategy_likelihood);
    length += sprintf(Buffer+length, "_M_%d",migration_range);
    length += sprintf(Buffer+length, "_m_%0.3f",random_migration);
    length += sprintf(Buffer+length, "_s_%0.4f",expell_likelihood);
    

    str.assign(Buffer, Buffer + length);

    int k = 0;
    string filename_output_all_mv = "results/allmoves/" + str + "_" + to_string(k) + ".csv";
    string filename_output_summary = "results/summary/" + str + "_" + to_string(k) + ".csv";
    string filename_configurations = "results/grids/" + str + "_" + to_string(k) + ".csv";
    
    while (fileExists(filename_output_summary)){
        k++;
        filename_output_all_mv = "results/allmoves/" + str + "_" + to_string(k) + ".csv";
        filename_output_summary = "results/summary/" + str + "_" + to_string(k) + ".csv";
        filename_configurations = "results/grids/" + str + "_" + to_string(k) + ".csv";
        }
    
    output_all_mv.open(filename_output_all_mv, ios::trunc); // open all moves output file;
    output_summary.open(filename_output_summary, ios::trunc); // open summary output file;
    output_summary << "simul_step,completion,coop_level,cooperators,defectors,empty\n";
    output_grid_states.open(filename_configurations, ios::trunc); // open configuration output file;
    }

string format_summary(){

    char Buffer[500];
    string str;
    int length = 0;
    
    length += sprintf(Buffer+length, "%d,",current_step);
    length += sprintf(Buffer+length, "%0.3f,",current_step/static_cast<float>(MCS));
    length += sprintf(Buffer+length, "%0.3f,",static_cast<float>(cooperators)/(cooperators + defectors));
    length += sprintf(Buffer+length, "%d,",cooperators);
    length += sprintf(Buffer+length, "%d,",defectors);
    length += sprintf(Buffer+length, "%d\n",empty);
    
    str.assign(Buffer, Buffer + length);
    
    return str;
    }



float rand01() {
	return (float)arc4random_uniform(100000)/100000;
	}


void makeGrid() {
	/* Makes a grid of size l with equal number
	 of cooperators (value 1) and defectors (value 0). If grid_density is
	 less than 100%, then the some sites are emptied randmonly (value -1)
	 */
    
	for (int i = 0; i < l; i++) {
		for (int j = 0; j < h; j++) {
            if (rand01() < init_coop_level) grid[i][j] = 1;
            else grid[i][j] = 0;
            
			if (rand01() > grid_density) { // remove player from grid as a function of grid_density
				grid[i][j] = -1;
            }
        }
    }
}


void countCDE(){
	/* Performs a count of cooperators, defectors and empty sites.
	 If update = 1, cooperators, defectors, and empty variables are updated
	 If update = 0, assuming that if there is no update, then the then the only reason
	 for invoking this function is to print out the current state of cooperation and defection.
	 Regardless of the value of update, if verbose >=2, then the current state of cooperation and defection is printed out.
	 */
	
	//int c,d,e = 0; // initialize count variables;
    
	cooperators = 0;
	defectors = 0;
	empty = 0;
	
	for (int i = 0; i < l; i++){
		for (int j = 0; j < h; j++){
			if (grid[i][j] == 1) {
				cooperators++;
            }
			
			else if (grid[i][j] == 0) {
				defectors++;
            }
			
			else {
				empty++;
            }
        }
    }
	
    
	if (verbose >= 2){
		cout << "cooperators:" << cooperators << ", defectors:" << defectors << ", empty sites:" << empty << endl;
    }
    
}


void load_grid(){
    
    std::ifstream testFile(grid_load_filename, std::ios::binary);
    
    string cell;
    int cellInt;
    
    grid.resize(l, vector<int>(h));
    
    int i=0;
    
    while(getline(testFile,cell,',')){
        stringstream str(cell);
        str >> cellInt;
        //cout << i/h << " " << i%h << " " << cellInt << endl;
        //grid[i/h][i%h] = cellInt;
        grid[i%h][i/h] = cellInt;
        i++;
    }
    countCDE(); // update values for cooperators, defectors, and empty
}

void showGrid(int subset = 20) {
	/* Displays the grid on the command line
	 Note that the grid is large, the display won't be nice.
	 */
    
    int height;
    int length;
    
    if (subset == 0){
        height = h;
        length = l;
        }
    else {
        height = length = subset;
        }
    
    string character;
    
	for (int j = 0; j < height; j++){
		for (int i=0; i < length; i++) {
            if (grid[i][j] == -1) character = " ";
            else character = to_string(grid[i][j]);
            
            
            if (i+1==length){
                
				if (grid[0][j+1] < 0){
					cout << character << "\n";
					//cout << grid[i][j] << "\n";
				}
				else {
					cout << character << "\n ";
				}
            }
			else {
				if (grid[i+1][j] < 0){
					cout << character << "\t";
                }
				else {
					cout << character << "\t ";
                }
            }
        }
    }
	cout << endl;
}


void save_grid_state(){
    
    output_grid_states << current_step << ":[";
    
    for (int j = 0; j < h; j++){
		for (int i = 0; i < l; i++) {
            //output_grid_states << "(" << i << "," << j << "," << grid[i][j] << "),";
            output_grid_states << grid[i][j] << ",";
            }
        }
    output_grid_states << "]\n";
    }

void findNeighbors(int player_l, int player_h) {
	/*Find neighbors of a focal site:
	 If numNeighbors = 4, the 4 sites in direct contact are selected.
	 If numNeighbors = 8, the 8 sites around the focal site are selected.
	 This function is useful to compare payoffs between the focal player and her neighbors.
	 */
	
	//cout << "focal site: " << player_l << " " << player_h << " " << grid[player_l][player_h] << endl;
	//cout << player_l  << "," << player_h  << "\n" << endl;
    
	
	if ((numNeighbors != 4) && (numNeighbors != 8)){
		cout << "wrong neighborhood number" << endl;
    }
	
	if (numNeighbors==4){
		nghb_l[0] = player_l;
		nghb_h[0] = (player_h - 1 + h)%h;
        
		nghb_l[1] = (player_l - 1 + l)%l;
		nghb_h[1] = player_h;
		
		nghb_l[2] = (player_l + 1 + l)%l;
		nghb_h[2] = player_h;
		
		nghb_l[3] = player_l;
		nghb_h[3] = (player_h + 1 + h)%h;
        
    }
    
	
	/*
     cout << (player_h - 1 + h)%h  << "," << player_l << endl;
     cout << player_h << "," << (player_l - 1 + l)%l << endl;
     cout << player_h << "," << (player_l + 1 + l)%l << endl;
     cout << (player_h + 1 + h)%h << "," << player_l << endl;
     */
    
    /*
     cout << nghb_h[0]  << "," << nghb_l[0] << endl;
     cout << nghb_h[1] << "," << nghb_l[1] << endl;
     cout << nghb_h[2]<< "," << nghb_l[2] << endl;
     cout << nghb_h[3] << "," << nghb_l[3] << endl;
     */
    
	else if (numNeighbors==8){
		
		nghb_l[0] = (player_l - 1 + l)%l;
		nghb_h[0] = (player_h - 1 + h)%h;
		
        
		nghb_l[1] = player_l;
		nghb_h[1] = (player_h - 1 + h)%h;
        
		nghb_l[2] = (player_l + 1 + l)%l;
		nghb_h[2] = (player_h - 1 + h)%h;
		
		nghb_l[3] = (player_l - 1 + l)%l;
		nghb_h[3] = player_h;
        
		nghb_l[4] = (player_l + 1 + l)%l;
		nghb_h[4] = player_h;
		
		nghb_l[5] = (player_l - 1 + l)%l;
		nghb_h[5] = (player_h + 1 + h)%h;
		
		nghb_l[6] = player_l;
		nghb_h[6] = (player_h + 1 + h)%h;
        
		nghb_l[7] = (player_l + 1 + l)%l;
		nghb_h[7] = (player_h + 1 + h)%h;
        
		
    }
	
	if (verbose >= 2){
		for (int i=0; i < numNeighbors; i++) {
			cout << nghb_l[i]  << "," << nghb_h[i] << endl;
        }
    }
    
}


void explore_m_range(int player_l, int player_h){
	/* Explore migration range to find best sites. */
	
	int l_index;
	int h_index;
    
	int k = 0;
	for (int j= player_h - migration_range ; j < player_h + migration_range +1 ; j++) {
		for (int i = player_l - migration_range ; i < player_l + migration_range +1 ; i++){
			
			l_index = (i + l)%l;
			h_index = (j + h)%h;
			
			
			if ((l_index == player_l)&&(h_index == player_h)){
				continue;
            }
			
			migration_array_l[k] = l_index;
			migration_array_h[k] = h_index;
			k++;
		}
	}
    
	
	if (verbose >= 2){
		
		cout << "focal player: "
		<< player_l
		<< ","
		<< player_h
		<< " strategy: "
		<< grid[player_l][player_h]
		<< endl;
		
		k=0;
		for (int i = 0; i < n_migration_sites ; i++) {
			//cout << i << " (" << migration_array_l[i] << "," << migration_array_h[i] << ")" << endl;
			
			if ( (i-1) == (n_migration_sites-1)/2){
				cout << "X" << "," << "X" << "  ";
				k=1;
			}
			
			if ( (i + 1 + k)  % (2*migration_range +1) == 0){
				cout << migration_array_l[i] << "," << migration_array_h[i] << "(" << grid[ migration_array_l[i]][ migration_array_h[i]] << ")\n";
			}
			
			else {
				cout << migration_array_l[i] << "," << migration_array_h[i]  << "(" << grid[ migration_array_l[i]][ migration_array_h[i]] << ") ";
            }
			
            
			
        }
		cout << endl;
    }
	
}


float compute_migration_distance(float site_l, float site_h, float migration_site_l, float migration_site_h){
    // computes a simple distance between 2 sites
    
    return sqrt(pow(min(abs(site_l-migration_site_l), l-1-abs(site_l-migration_site_l)),2)+  pow(min(abs(site_h - migration_site_h), h-1-abs(site_h-migration_site_h)),2));
    }

float pDilemma(int strategy, int stragegy_nghb) {
	/* Implements the prisoners dilemma game between */
	
	float pd_payoff = 0;
	
	if ((strategy == 1) && (stragegy_nghb == 1)) {
		pd_payoff = R;
    }
	
	else if ((strategy == 0) && (stragegy_nghb == 1)) {
		pd_payoff = T;
    }
	
	else if ((strategy == 1) && (stragegy_nghb == 0)) {
		pd_payoff = S;
    }
	
	else if ((strategy == 0) && (stragegy_nghb == 0)) {
		pd_payoff = P;
    }
	
	else {
		cout << "error with input strategies" << endl;
		return -1;
    }
    
	return pd_payoff;
}


float payoff(int player_l, int player_h, int strategy){
	// Compute payoff from playing with neighbors
	
	//int strategy = grid[player_l][player_h];
	float sum_payoff = 0;
    
	findNeighbors(player_l,player_h); // Search for neighbors
	
	int strategy_nghb;
	
	for (int i=0; i < numNeighbors; i++) {
		
		strategy_nghb = grid[nghb_l[i]][nghb_h[i]];
		
		if (strategy_nghb != -1){
			
			sum_payoff += pDilemma(strategy, strategy_nghb);
			
			/*
             cout << nghb_l[i]
             << ","
             << nghb_h[i]
             << "  strategy :"
             << strategy_nghb
             << " payoff: "
             << payoff
             << endl;
             */
        }
    }
	
	//cout << "sum payoff: " << sum_payoff << endl;
	return sum_payoff;
}


int strategy_update_Fermi(float o_pay_off, float best_pay_off) {
	/*update strategy of focal player by trying to reproduce
	 the strategy of the best performing neighbor, using
	 Fermi Temperature*/
    
	if ((o_pay_off - best_pay_off) >= 0){
		/* If initial strategy has better payoff or
		 both strategies have same payoff, do nothing */
		//cout << " higher original payoff or same payoff: " << o_pay_off;
		return 0;
		
    }
	
	else {
		float f_temperature = 1./(1 + exp(o_pay_off - best_pay_off)/fermi_temperature);
				
		if (rand01() < f_temperature) {
			//cout << "update strategy" << endl;
			return 1;
        }
		else {
			//cout << "no update " << endl;
			return 0;
		}
        
    }
	
}


int strategy_update_Dirk(float o_pay_off, float best_pay_off){
	
	if ((o_pay_off < best_pay_off) and (rand01() <  imitation_likelihood)){
        //cout << o_pay_off << " " << best_pay_off << " " << rand01() << endl;
        return 2; // copy strategy
    }
	else if ((rand01() > imitation_likelihood) and (rand01() < reset_strategy_likelihood)){
		return 1; // cooperate
    }
    else if ((rand01() > imitation_likelihood ) and (rand01() > reset_strategy_likelihood) and (reset_strategy_likelihood > 0)){
		return 0; // defect
    }
    else {
        return -1; // do nothing
    }
}



void compare_payoff_with_nghbs(int player_l, int player_h, int update_strategies = 1){
	
	
    strategy_focal_player = grid[player_l][player_h];
	payoff_focal_player = payoff(player_l,player_h, strategy_focal_player);
	
	findNeighbors(player_l,player_h);
	
	//copy(begin(nghb_l), end(nghb_l), begin(nghbl));
	//int nghbh = nghb_h;
	
	
	float payoff_nghb;
	float strategy_nghb;
	float highest_payoff = payoff_focal_player;
	int win_strategy = strategy_focal_player;
	int win_nghb_l = player_l;
	int win_nghb_h = player_h;
	
	//vector<int> nghbl(numNeighbors];
	//vector<int> nghbh(numNeighbors];
	
    
    vector<int> nghbl(nghb_l);
	vector<int> nghbh(nghb_h);
	
    //copy(nghb_l, nghb_l + numNeighbors, nghbl);
	//copy(nghb_h, nghb_h + numNeighbors, nghbh);
	
	for (int i=0; i < numNeighbors; i++) {
		/* Parkour all neighbors to find the strategy with highest payoff */
		
		//cout << nghb_l[i] << "," << nghb_h[i] << " " << nghbl[i] << "," << nghbh[i] << endl;
		strategy_nghb = grid[nghbl[i]][nghbh[i]];
		
		if (strategy_nghb == -1) {
			//cout << "empty site" << endl;
			payoff_nghb = -1000; // assign an arbitrary small payoff
		}
		else {
			payoff_nghb = payoff(nghbl[i],nghbh[i],strategy_nghb);
		}
		
		if (payoff_nghb > highest_payoff){
			highest_payoff = payoff_nghb;
			win_nghb_l = nghbl[i];
			win_nghb_h = nghbh[i];
			win_strategy = strategy_nghb;
			//cout << highest_payoff << " " << win_strategy << " (" << win_nghb_l << "," << win_nghb_h << ") " << grid[win_nghb_l][win_nghb_h] << endl;
		}
	}
    
	
	if (update_strategies == 1){
		/* Attempt strategy update:
		 provides a binary value to determine if an update actually ocurred
		 (1 => update, 0 => no update) */
		int update_s;
		
		
		/* Choose update method */
		//if (update_style == "Fermi"){
		//	update_s = strategy_update_Fermi(payoff_focal_player, highest_payoff);
        //}
		//else if (update_style == "Dirk"){
        update_s = strategy_update_Dirk(payoff_focal_player, highest_payoff);
			//cout << "Dirk update " << update_s << endl;
        //}
        
        
		
		if ((update_s == 2) and (win_strategy != strategy_focal_player)){ //
			grid[player_l][player_h] = grid[win_nghb_l][win_nghb_h]; // update strategy
			
			//cout << grid[player_l][player_h] << endl;
			
			
            countCDE(); //recount current number of cooperators, defectors and empty sites.
			
			// write update to output_all_mv file
			output_all_mv  << current_step <<","
            << cooperators << ","
            << defectors << ","
            << empty << ","
            << "U" << ","
            << player_l << ","
            << player_h << ","
            << strategy_focal_player << ","
            << grid[win_nghb_l][win_nghb_h] << ","
            << payoff_focal_player << ","
            << highest_payoff
            << "\n";
            
            count_changes +=1;
            
			
			if (verbose >= 2){
				cout << "strategy updated for ("
				<< player_l
				<< ","
				<< player_h
				<< ")"
				<< " from "
				<< strategy_focal_player
				<< " to "
				<< win_strategy
				<< endl;
            }
        }
		
		else if ((update_s == 0) or (update_s == 1)){
			int old_strategy = grid[player_l][player_h];
			grid[player_l][player_h] = update_s;
            
            countCDE();
            
            output_all_mv  << current_step <<","
            << cooperators << ","
            << defectors << ","
            << empty << ","
            << "R" << ","
            << player_l << ","
            << player_h << ","
            << old_strategy << ","
            << grid[player_l][player_h]
            << "\n";
        
            count_changes +=1;
        }
        
        else {
            return;
        }
    }
    
}



void compare_payoff_m_range(int player_l, int player_h, float random_migration_likelihood, float expell, int force_migrate){
	
    
    strategy_focal_player = grid[player_l][player_h];
    int sfp = grid[player_l][player_h];
    payoff_focal_player = payoff(player_l,player_h, strategy_focal_player);
	explore_m_range(player_l,player_h);
	
    float pf;
	float best_pay_off;
	
    float migration_payoff[n_migration_sites];
    float migration_distance[n_migration_sites];
    float distance; //migration distance
	float shortest_distance = 1000; // shortest migration distance
    
    
	int index;
    
    int mv_destination_l;
    int mv_destination_h;
    
    string migration_type;
	
    
    vector<int> sites_empty;
	vector<int>::iterator it_e;
	
	vector<int> sites_occupied;
	vector<int>::iterator it_o;

	vector<int> best_sites_empty;
	vector<int>::iterator it_bse;
	
	vector<int> better_sites_empty;
	vector<int>::iterator it_rse;
    
    vector<int> better_sites_empty_payoff;
	vector<int>::iterator it_rsep;
	
	vector<int> best_sites_occupied;
	vector<int>::iterator it_bso;

    vector<int> worse_sites_empty;
	vector<int>::iterator it_wse;
    
    vector<int> worse_sites_empty_payoff;
	vector<int>::iterator it_wsep;
    
    
	if (verbose >=2) cout << "(" << player_l << "," << player_h << ") " << "orig. strategy : " << strategy_focal_player << "  orig. payoff : " << payoff_focal_player << endl;

	
	if (force_migrate == 1) best_pay_off = -10;// assign an arbitrary small value to force migration to make sure a "better" spot can be found
	else best_pay_off = payoff_focal_player + 0.0001; // added a small value to ensure that only sites with higher payoff are selected

    
	for (int q=0; q < n_migration_sites; q++){
        /* compute payoff on all possible migration sites */
        
        grid[player_l][player_h] = -1; //nasty hack to compute payoff assuming that the player has already left the site
        
		migration_payoff[q] = payoff(migration_array_l[q], migration_array_h[q],strategy_focal_player);
        migration_distance[q] = compute_migration_distance(player_l, player_h,migration_array_l[q] ,migration_array_h[q]);
		
        grid[player_l][player_h] = strategy_focal_player; // follow up nasty hack: restore original strategy because at this point is unclear whether the player will move
        
        if (migration_payoff[q] > best_pay_off) {
            // find the highest possible payoff among all sites
            best_pay_off = migration_payoff[q];
            }
    }
    
    
	//cout << "\n";
    
	for (int j=0; j < n_migration_sites; j++) {
        
        //cout << "("<< migration_array_l[j] << "," << migration_array_h[j] << ")" << strategy_focal_player << " " << payoff(migration_array_l[j], migration_array_h[j],strategy_focal_player) << endl;

        if (grid[migration_array_l[j]][migration_array_h[j]] == -1){
            //find all EMPTY sites
            it_e = sites_empty.end();
            sites_empty.insert(it_e,j); // add site index to sites_empty vector

            }
        
        
        if (grid[migration_array_l[j]][migration_array_h[j]] > -1){
            //find all OCCUPIED sites
            it_o = sites_occupied.end();
            sites_occupied.insert(it_o,j); // add site index to sites_occupied vector
            
        }
        
        
		if (migration_payoff[j] == best_pay_off) {
            //find all EMPTY sites with HIGHEST payoff (there might be multiple ones)
			if (grid[migration_array_l[j]][migration_array_h[j]] == -1){
				it_bse = best_sites_empty.end();
				best_sites_empty.insert(it_bse,j); // add site index to best_sites_empty vector
            }
			else {
                // find all OCCUPIED sites with highest payoff (there might be multiple ones)
				it_bso = best_sites_occupied.end();
				best_sites_occupied.insert(it_bso,j); // add site index to best_sites_occupied vector
            }
        }
		else if ((grid[migration_array_l[j]][migration_array_h[j]] == -1) and (migration_payoff[j] < best_pay_off) and (migration_payoff[j] > payoff_focal_player)){
            // find all EMPTY sites with HIGHER payoff
			it_rse = better_sites_empty.end();
			better_sites_empty.insert (it_rse,j); // add site index to better_sites_empty vector
            
            it_rsep = better_sites_empty_payoff.end();
			better_sites_empty_payoff.insert(it_rsep,j); // add site index to better_sites_empty vector
        }

        else if ((grid[migration_array_l[j]][migration_array_h[j]] == -1) and (migration_payoff[j] <= payoff_focal_player) and (force_migrate == 1)){
            // find all EMPTY sites with LOWER payoff
			it_wse = worse_sites_empty.end();
			worse_sites_empty.insert(it_wse,j); // add site index to better_sites_empty vector
            
            it_wsep = worse_sites_empty_payoff.end();
			worse_sites_empty_payoff.insert(it_wsep,j); // add site index to better_sites_empty vecto
        }

        
        
		if (verbose >= 2){
			cout << j
			<< " ("
			<< migration_array_l[j]
			<< ","
			<< migration_array_h[j]
			<< ") "
			<< grid[migration_array_l[j]][migration_array_h[j]]
			<< "  payoff: " << pf << endl;
		}
        
	}
    
    float rand_migration = rand01(); // draw a uniform random variable for random migration likelihood
    float rand_expell = rand01();
    
    if (rand_migration < random_migration_likelihood) {  // random relocation
    
        if ((sites_occupied.size() > 0) and (rand_expell < expell)) {  // with property violation
            //int size = sites_occupied.size();
            //int r_site = arc4random_uniform(static_cast<int>(sites_occupied.size()));
            index = sites_occupied[arc4random_uniform(static_cast<int>(sites_occupied.size()))];

            
            migration_type = "RE";
            
            mv_destination_l = migration_array_l[index];
            mv_destination_h = migration_array_h[index];

            shortest_distance = compute_migration_distance(player_l, player_h,mv_destination_l,mv_destination_h);
            
            
            //cout << "RE "<< index << " ("<< mv_destination_l<< "," << mv_destination_h << ") "<< endl;
            
            //cout << "E "<< size << " " << r_site << " "<< index << " ("<< mv_destination_l<< "," << mv_destination_h << ") "<< endl;
            
            grid[player_l][player_h] = -1; // clear old site first to allow relocation of the expelled player to this site
            //cout << "expell: cleared site: (" << player_l << "," << player_h << ") " << grid[player_l][player_h] << "\n";
            compare_payoff_m_range(mv_destination_l,mv_destination_h,0,0,1); // force migration (recursive function)
            grid[mv_destination_l][mv_destination_h] = sfp; // move agent (i.e., copy strategy from old to new site)
            countCDE(); // count cooperators, defectors and empty sites
            
            
        }
        else if ((sites_empty.size() > 0) and (rand_expell > expell)){ // without property violation
            //int size = sites_empty.size();
            //int r_site = arc4random_uniform(static_cast<int>(sites_empty.size()));
            index = sites_empty[arc4random_uniform(static_cast<int>(sites_empty.size()))];
            
    
            migration_type = "RM";
            
            mv_destination_l = migration_array_l[index];
            mv_destination_h = migration_array_h[index];
            
            shortest_distance = compute_migration_distance(player_l, player_h,mv_destination_l,mv_destination_h);
            
            //cout << "M "<< size << " " << r_site << " "<< index << " ("<< mv_destination_l<< "," << mv_destination_h << ") "<< endl;
            
            
            if (verbose >= 2) cout << "best empty site: "<< "(" << mv_destination_l << "," << mv_destination_h << ") " << shortest_distance << "\n"<< endl;
            
            grid[mv_destination_l][mv_destination_h] = strategy_focal_player;
            grid[player_l][player_h] = -1;
            countCDE(); // count cooperators, defectors and empty sites

            
        }
        
        else return;
    }

    else if ((best_sites_empty.size() > 0) and (rand_migration < (1 - random_migration_likelihood))){
            /* find closest EMPTY site with highest payoff AND shortest dist*/
        //shortest_distance = 1000;
        for (int i=0; i < best_sites_empty.size(); i++) {
            distance = compute_migration_distance(player_l, player_h,migration_array_l[best_sites_empty[i]], migration_array_h[best_sites_empty[i]]);
            
            if (distance < shortest_distance){
                shortest_distance = distance;
                chosen_migration_site = i;
                }
        }
    
        index = best_sites_empty[chosen_migration_site];
        
        if (force_migrate == 1) migration_type = "FM";
        else migration_type = "M";
    
        mv_destination_l = migration_array_l[index];
        mv_destination_h = migration_array_h[index];
        
        
        if (verbose >= 2) cout << "best empty site: "<< "(" << mv_destination_l << "," << mv_destination_h << ") " << shortest_distance << "\n"<< endl;
        
        grid[mv_destination_l][mv_destination_h] = strategy_focal_player;
        grid[player_l][player_h] = -1;
        countCDE(); // count cooperators, defectors and empty sites
    }
    
    
    else if ((best_sites_empty.size() == 0) and (best_sites_occupied.size() > 0) and (rand_expell < expell)){
        /* find closest OCCUPIED site with highest payoff (if no empty site with similar payoff is available */
        //shortest_distance = 1000;
        for (int i=0; i < best_sites_occupied.size(); i++) {
            distance = compute_migration_distance(
                player_l, player_h,
                migration_array_l[best_sites_occupied[i]], migration_array_h[best_sites_occupied[i]]
                );
        
            if (distance < shortest_distance){
                shortest_distance = distance;
                chosen_migration_site = i;
            }
        }
    
        index = best_sites_occupied[chosen_migration_site];
        migration_type = "E";
    
        mv_destination_l = migration_array_l[index];
        mv_destination_h = migration_array_h[index];
    
        grid[player_l][player_h] = -1; // clear old site first to allow relocation of the expelled player to this site
        //cout << "expell: cleared site: (" << player_l << "," << player_h << ") " << grid[player_l][player_h] << "\n";
        compare_payoff_m_range(mv_destination_l,mv_destination_h,0,0,1); // force migration (recursive function)
        grid[mv_destination_l][mv_destination_h] = sfp; // move agent (i.e., copy strategy from old to new site)
        countCDE(); // count cooperators, defectors and empty sites
    }
    
    else if ((better_sites_empty.size() > 0) and (rand_migration < (1 - random_migration_likelihood))) {
        /* Find the best available site with higher payoff, if all sites with highest payoff are occupied and the property violation step has not occurred (resp. if the player is forced to move)*/
        best_pay_off = payoff_focal_player;
        
        for (int i=0; i < better_sites_empty.size(); i++) {
            distance = compute_migration_distance(player_l, player_h,migration_array_l[better_sites_empty[i]], migration_array_h[better_sites_empty[i]]);
    
            if (distance < shortest_distance){
                shortest_distance = distance;
                chosen_migration_site = i;
            }
        }
        
        index = better_sites_empty[chosen_migration_site];
        
        
        if (force_migrate == 1) migration_type = "FM";
        else migration_type = "M";
        
        mv_destination_l = migration_array_l[index];
        mv_destination_h = migration_array_h[index];
        
        shortest_distance = compute_migration_distance(player_l, player_h,mv_destination_l, mv_destination_h);
        
        if (verbose >= 2 and force_migrate==1) cout << "better empty site: "<< "(" << mv_destination_l << "," << mv_destination_h << ") " << shortest_distance << "\n"<< endl;
        
        
        grid[mv_destination_l][mv_destination_h] = strategy_focal_player;
        grid[player_l][player_h] = -1;
        countCDE(); // count cooperators, defectors and empty sites
    }
    
    else if ((worse_sites_empty.size() > 0) and (rand_migration < (1 - random_migration_likelihood))) {
        
        for (int i=0; i < worse_sites_empty.size(); i++) {
            distance = compute_migration_distance(player_l, player_h,migration_array_l[worse_sites_empty[i]], migration_array_h[worse_sites_empty[i]]);
            
            if (distance < shortest_distance){
                shortest_distance = distance;
                chosen_migration_site = i;
            }
        }
        
        index = worse_sites_empty[chosen_migration_site];
        
        
        if (force_migrate == 1) migration_type = "FM";
        else migration_type = "M";
        
        mv_destination_l = migration_array_l[index];
        mv_destination_h = migration_array_h[index];
        
        shortest_distance = compute_migration_distance(player_l, player_h,mv_destination_l, mv_destination_h);
        
        if (verbose >= 2 and force_migrate==1) cout << "worse empty site: "<< "(" << mv_destination_l << "," << mv_destination_h << ") " << shortest_distance << "\n"<< endl;
        
        
        grid[mv_destination_l][mv_destination_h] = strategy_focal_player;
        grid[player_l][player_h] = -1;
        countCDE(); // count cooperators, defectors and empty sites
    }

    
    else {
        /*
        if (force_migrate==1) {
            cout << current_step << "  blah" << endl;
            cout << worse_sites_empty.size() << " " << rand_migration <<endl;
            verbose = 2;
            explore_m_range(player_l, player_h);
            verbose = 1;
            
        }
        */
        return;
    }


    // write update to output_all_mv file
    output_all_mv  << current_step <<","
    << cooperators << ","
    << defectors << ","
    << empty << ","
    << migration_type << ","
    << player_l << ","
    << player_h << ","
    << mv_destination_l << ","
    << mv_destination_h << ","
    << grid[mv_destination_l][mv_destination_h] << ","
    << payoff(mv_destination_l, mv_destination_h,grid[mv_destination_l][mv_destination_h]) - payoff(player_l, player_h, grid[mv_destination_l][mv_destination_h]) << ","
    << shortest_distance
    << "\n";
    
    count_changes +=1;
    
    focal_player_l = mv_destination_l;
    focal_player_h = mv_destination_h;

    }


void oneStep(){
	/*Performs one step of the simulation:
	 a: compare payoffs with those of neighbors
	 b: update strategy (not implemented yet)
	 c: explore migration range M
     */
    
	focal_player_l = rand_steps_l[current_step];
	focal_player_h = rand_steps_h[current_step];
	strategy_focal_player = grid[focal_player_l][focal_player_h];
	
	if ((strategy_focal_player != -1) and migration_range > 0){
        compare_payoff_m_range(focal_player_l, focal_player_h,random_migration,expell_likelihood,0);
        compare_payoff_with_nghbs(focal_player_l,focal_player_h,1);
    }
    else if ((strategy_focal_player != -1) and migration_range == 0){
        compare_payoff_with_nghbs(focal_player_l,focal_player_h,1);
    }
    
	if (verbose >= 2){
		cout << "( " << focal_player_l << "," << focal_player_h << ") " << strategy_focal_player << endl;
    }
}


void randomSteps(){
	// Generate random grids (randSteps_l and randSteps_h) of size MCS
	//srand ( time(NULL) ); //initialize the random seed
	for(int i=0; i < MCS; i++){
		rand_steps_l[i] = arc4random_uniform(l);
		rand_steps_h[i] = arc4random_uniform(h);
	}
}

void simulate(){
	
	randomSteps();
	countCDE();
    summary = format_summary();
    output_summary << summary;
    save_grid_state();
    //showGrid();
    
    int coop_count;
    
    if (verbose > 0) cout << "(start) " << 0/static_cast<float>(MCS)*100 << "% " << static_cast<float>(cooperators)/(cooperators + defectors)*100 << "%\tcooperators: " << cooperators << ", defectors:" << defectors << ", empty sites:" << empty << endl;
	if (verbose >= 2) showGrid();
	
	for (int i=0; i<MCS; i++) {
		
		if ((count_changes)%25 == 0) {
			countCDE();
            coop_count = cooperators;
            
            summary = format_summary();
            output_summary << summary;
            if (save_grids > 0) {
                save_grid_state();
                }
            
			if (verbose > 0) cout << summary;
			else if (verbose >= 2) showGrid();
            
            count_changes += 1; // just to make sure the same grid does not show up again if no change occurs
			
        }
		if ((cooperators == 0) or (defectors == 0)){
            countCDE();
            
            summary = format_summary();
            output_summary << summary;
            save_grid_state();
            
            if (verbose > 0) cout << summary;
            
			if (verbose >= 2) showGrid();
            break;
        }
		
		if (i+1 == MCS){
            countCDE();
             summary = format_summary();
            output_summary << summary;
            save_grid_state();
			if (verbose > 0) cout << summary;
            if (verbose >= 2) showGrid();
			break;
        }
        
		current_step = i;
		oneStep();
    }
	output_all_mv.close(); // close output_all_mv file;
    output_summary.close(); // close output summary file;
    output_grid_states.close(); // close grid state file;
};


void testing(){
    /*
	cout << "1. Test Make Grid\n" << endl;
	makeGrid();
	showGrid();
	countCDE();
	cout << "cooperators:	" << cooperators << ", defectors:" << defectors << ", empty sites:" << empty << endl;
    
     cout << "\n2. Test Find Neighbors" << endl;
     int player_l = 4;
     int player_h = 9;
     cout << "focal player: " << player_l << "," << player_h << endl;
     findNeighbors(player_l,player_h);
     
     
     cout << "\n3. Test Prisoners' Dilemma" << endl;
     
     pDilemma(0,0);
     cout << payoff_focal_player << endl;
     
     cout << "\n4. Test One Step Simmulation" << endl;
     randomSteps();
     current_step = 10;
     oneStep();
     
     
     cout << "\n5. Test explore Migration Range" << endl;
     current_step = 10;
     randomSteps();
     focal_player_l = rand_steps_l[current_step];
     focal_player_h = rand_steps_h[current_step];
     
     explore_m_range(focal_player_l,focal_player_h);
     cout << endl;
     
     cout << "\n6. Test compare payoffs migration range" << endl;
     compare_payoff_m_range(focal_player_l,focal_player_h);
     */
    
    /*
     cout << "\n7. Test Fermi Update" << endl;
     strategy_update_Fermi(4, 6.);
     */

    /*
    cout << "\n8. Test Migration distance" << endl;
    cout << compute_migration_distance(12, 17, 47, 3) << endl;
    */
    
    cout << "\n5. Test Whole Simulation" << endl;
    simulate();
    cout << MCS << " done" << endl;

    /*
     
     char str[10];
     
     //Creates an instance of ofstream, and opens example.txt
     ofstream a_file ( "example.txt" , ios::trunc);
     // Outputs to example.txt through a_file
     
     for (int i=0; i < 100000; i++) {
     a_file << "This text will now be inside of example.txt\n";
     }
     // Close the file stream explicitly
     
     a_file.close();
     //Opens for reading the file
     
     
     string line;
     ifstream b_file ( "example.txt" );
     while (std::getline(b_file, line)){
     cout << line;
     }
     //Reads one string from the file
     b_file >> str;
     //Should output 'this'
     cout<< str <<"\n";
     //cin.get();    // wait for a keypress
     // b_file is closed implicitly here
     */
    }



int main(int ac, char* av[])
    {
        try {
            string config_file;
            
            
            // Declare a group of options that will be
            // allowed only on command line
            po::options_description generic("Generic options");
            generic.add_options()
            ("version,v", "print version string")
            ("help", "produce help message")
            ("config,c", po::value<string>(&config_file)->default_value("pgame.cfg"),
             "name of a file with configuration.")
            ;
            
            // Declare a group of options that will be
            // allowed both on command line and in
            // config file
            po::options_description config("Configuration");
            config.add_options()
            ("verbose", po::value<int>(&verbose)->default_value(0),"verbose 0 to 3 (default 0)")
            ("iterations,i", po::value<int>(&iterations)-> default_value(200),"number of iterations")
            ("grid_length,l",po::value<int>(&l)-> default_value(50),"grid length")
            ("grid_height,h",po::value<int>(&h)-> default_value(50),"grid heigth")
            ("grid_density,d",po::value<float>(&grid_density) -> default_value(0.5),"grid density (between 0 and 1)")
            ("load_grid,g", po::value<string>(&grid_load_filename),
             "name of a file with initial grid configuration.")
            ("save_grids", po::value<int>(&save_grids),
             "save intermediary grids.")
            ("init_coop_level",po::value<float>(&init_coop_level) -> default_value(0.5),"cooperation level at initialization (between 0 and 1)")
            ("neighbors,n",po::value<int>(&numNeighbors)-> default_value(4),"set 4 or 8 neighbors to play with")
            ("migration_range,M",po::value<int>(&migration_range) -> default_value(5),"migration range (M >= 1)")
            ("imitation_likelihood,r",po::value<float>(&imitation_likelihood)-> default_value(0),"probability r to imitate best neighbor (between 0 and 1)")
            ("reset_strategy_likelihood,q",po::value<float>(&reset_strategy_likelihood)-> default_value(0),"probability q to reset strategy (between 0 and 1). Cooperate with probability q and to defect with probability 1-q")
            ("random_migration,m",po::value<float>(&random_migration)-> default_value(1),"random migration (m between 0 and 1)")
            ("expell_likelihood,s",po::value<float>(&expell_likelihood)-> default_value(0),"expell_likelihood (between 0 and 1)")
            ("temptation,T",po::value<float>(&T)-> default_value(1.3),"temptation payoff (c.f., game theory to tune this parameter)")
            ("reward,R",po::value<float>(&R)->default_value(1.0),"cooperation reward payoff(c.f., game theory to tune this parameter)")
            ("punishment,P",po::value<float>(&P)->default_value(0.1),"reciprocator payoff (c.f., game theory to tune this parameter)")
            ("sucker,S",po::value<float>(&S)->default_value(0.0),"sucker payoff (c.f., game theory to tune this parameter)")
            ;
            
            // Hidden options, will be allowed both on command line and
            // in config file, but will not be shown to the user.
            
            po::options_description hidden("Hidden options");
            hidden.add_options()
            ;
            
            po::options_description cmdline_options;
            cmdline_options.add(generic).add(config).add(hidden);
            
            po::options_description config_file_options;
            config_file_options.add(config).add(hidden);
            
            po::options_description visible("Allowed options");
            visible.add(generic).add(config);
            
            po::positional_options_description p;
            //p.add("input-file", -1);
            
            po::variables_map vm;
            store(po::command_line_parser(ac, av).
                  options(cmdline_options).positional(p).run(), vm);
            notify(vm);
            
            ifstream ifs(config_file.c_str());
            if (!ifs)
            {
                cout << "can not open config file: " << config_file << "\n";
                return 0;
            }
            else
            {
                store(parse_config_file(ifs, config_file_options), vm);
                notify(vm);
            }
            
            if (vm.count("help")) {
                cout << visible << "\n";
                return 0;
            }
            
            if (vm.count("version")) {
                cout << "Property Game, version 1.0\n";
                return 0;
            }
            
        }
        catch(exception& e)
        {
            cout << e.what() << "\n";
            return 1;
        }
        
        prepare_parameters();

        
        if (fileExists(grid_load_filename)) {
            cout << "loading grid from " << grid_load_filename << endl;
            load_grid();
            //showGrid();
            //cout << format_summary()<< endl;
        }
        else {
            cout << "generating new grid" << endl;
            makeGrid();
        }
        
        open_output_files();
        //testing();
        
        simulate();
        return 0;
    }







