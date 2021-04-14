// Create a map object with options
var myMap = L.map("map-id", {
    center: [37.0902, -95.7129],
    zoom: 4,
});

// Adding tile layer to the map
L.tileLayer("https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
    attribution: "© <a href='https://www.mapbox.com/about/maps/'>Mapbox</a> © <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a> <strong><a href='https://www.mapbox.com/map-feedback/' target='_blank'>Improve this map</a></strong>",
    tileSize: 512,
    maxZoom: 18,
    zoomOffset: -1,
    id: "mapbox/streets-v11",
    accessToken: API_KEY
}).addTo(myMap);

// Grab the data with d3
d3.json("/api", function (response) {

    // Log the data
    console.log(response);

    // Create a new marker cluster group
    var markers = L.markerClusterGroup();

    // Loop through data
    for (var i = 0; i < response.length; i++) {

        // Set the data location property to a variable
        var brewery = response[i];

        // Add a new marker to the cluster group and bind a pop-up with the brewery's name and type
        var newMarker = L.marker([brewery.Coordinates[0], brewery.Coordinates[1]]);
        newMarker.bindPopup("<h3>" + brewery.Name + "<h3><h3>Brewery type: " + brewery.Type + "</h3>");

        // Add the new marker to the markers array
        markers.addLayer(newMarker);

    }

    // Add our marker cluster layer to the map
    myMap.addLayer(markers);

});
