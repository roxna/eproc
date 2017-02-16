
// Declaring global variables OUTSIDE $(document).ready() for reference in analysis templates' js
var pieChartOptions, barChartOptions;
function pastelColors(){
    var r = (Math.round(Math.random()* 127) + 127).toString(16);
    var g = (Math.round(Math.random()* 127) + 127).toString(16);
    var b = (Math.round(Math.random()* 127) + 127).toString(16);
    return '#' + r + g + b;
}

$(document).ready(function(){   
	$(window).ready(function(){   

	// Return with commas in between
    var numberWithCommas = function(x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    };

    
    

    // PIE CHARTS used in spend_by_x.html	   
    pieChartOptions = {
        // tooltipTemplate: "<%= label %> ($<%= value %>)",
        // animation : false,
        // legendTemplate : '<ul class="legend">'
        //           +'<% for (var i=0; i<segments.length; i++) { %>'
        //             +'<li>'
        //             +'<span style=\"background-color:<%=segments[i].fillColor%>\"></span>'
        //             +'<% if (segments[i].label) { %><%= segments[i].label %> <% } %>'
        //           +'</li>'
        //         +'<% } %>'
        //       +'</ul>'
      };
	
	// BAR CHART used in industry_benchmarks.html
	barChartOptions = {
        scales: {
            xAxes: [{
                stacked: true,
                barPercentage: 0.7,
                categoryPercentage: 0.9,
                gridLines: {display: false},
            }],
            yAxes: [{      
            	stacked: true,
            }], 
        }, 
        barValueSpacing: 1.5,
    };
    });
});