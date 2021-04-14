function populateFilter() {
  // option for the user to filter the region in other to see the change
  const url = "api/values/region";

  d3.json(url).then(function(response) {
    
    var filerOptions = ["All"];
    filerOptions = filerOptions.concat(response);
    
    d3.select("#sel-filter-region")
    .selectAll("option")
    .data(filerOptions)
    .enter()
    .append("option")
    .text(d => d);

    // refresh the data after option been selected
      d3.select("#sel-filter-region").on("change", refreshCharts);
    });
  }

  function refreshCharts(event) {
  // get the selected option
  var selectedValue = d3.select(event.target).property('value');
  
  // chart will refresh after select option
  buildRegionPieChart(selectedValue);
  buildRegionByStateBarChart(selectedValue);
}

function buildRegionPieChart(selectedRegion) {
  // filter by the region
  var url = "api/count_by/region/brewery_type";
  if (selectedRegion != undefined) {
    url = `api/count_by/region/brewery_type?region=${selectedRegion}`;
  }
  
  d3.json(url).then(function(response) {
    // extract the labels and values from the json response
    var data = [{
      labels: response.map(d => d.brewery_type),
      values: response.map(d => d.total),
      type: 'pie'
    }];
    
    var layout = {
      height: 400,
      width: 500
    };
    
    Plotly.newPlot('state-region-plot', data, layout);

  });
}


function buildRegionByStateBarChart(selectedRegion) {
  var url = "api/count_by/region/state";
  if (selectedRegion != undefined) {
    url = `api/count_by/region/state?region=${selectedRegion}`;
  }

  d3.json(url).then(function(response) {

    // Using the group method in d3
    var grouped_data = d3.group(response, d => d.region)
  
    var traces = Array();

    // iterating over each group and create a trace for each group
    grouped_data.forEach(element => {      
      traces.push({
        x: element.map(d => d.state),
        y: element.map(d => d.total),
        name: element[0].region,
        type: 'bar'
      });
    });
    
    var layout = {
      barmode: 'stack',
      height: 400,
      width: 500
    };
    
    Plotly.newPlot('region-by-state-plot', traces, layout);
  });
}

// Upon intial load of the page setup
// the visualisations and the select filter
populateFilter();
buildRegionPieChart();
buildRegionByStateBarChart();
