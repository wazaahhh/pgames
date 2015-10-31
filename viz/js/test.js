
//Width and height
var w = 900;
var h = 500;
var padding = 70;


var width = 500
    , dict = {"-1": "empty", "0": "defector", "1": "cooperator" }
    , world = blinkengrid()
    , grid_size = 50 // default, based on Thomas' datasets
    , anim = {
    	fwd:   true,
        pause: false,
        index: 1
    }
    , iters
    //, ager_progress = slider()
    , coords = d3.scale.linear()
            .domain([0,grid_size])
            .range([0,width])
    , fontfile = "font.csv"
    ;
    

var data;

var grid
    , cell_count = 49 // default based on Thomas' abm automata
    , coords = d3.scale.linear()
                .range([0, width])
                .domain([0, cell_count])
 

// Load data from local file
d3.json("viztestdic.json", function(error, json) {
  	if (error) return console.warn(error);
	data = json.grids.t0;
	console.log("json successfully loaded");
	
	/*
	var printGrid = data.forEach(function(d,i) {
		row = Math.floor(i / grid_size);
		col = Math.floor(i % grid_size);
		console.log(row,col);
		});
	*/


});

d3.select("#viz").call(world);
console.log("hello world");


