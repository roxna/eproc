
// Declaring global variables OUTSIDE $(document).ready() for reference in analysis templates' js
var pieChartOptions, barChartOptions;
function pastelColors(){
    var r = (Math.round(Math.random()* 127) + 127).toString(16);
    var g = (Math.round(Math.random()* 127) + 127).toString(16);
    var b = (Math.round(Math.random()* 127) + 127).toString(16);
    return '#' + r + g + b;
}

$(document).ready(function(){    

	// Return with commas in between
    var numberWithCommas = function(x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    };

});