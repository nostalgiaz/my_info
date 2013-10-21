(function (mapData) {
  "use strict";

  var h = 540
    , w = 1080
    , vis
    , xy
    , path
    , countries
    , i
    , mapCoords
    ;

  vis = d3.select("#map").append("svg:svg").attr("width", w).attr("height", h);
  xy = d3.geo.equirectangular().scale(150).translate([w / 2, h / 2]);
  path = d3.geo.path().projection(xy);
  countries = vis.append('svg:g').attr('id', 'countries');

  countries.selectAll('path')
    .data(countries_data.features)
    .enter()
    .append('svg:path')
    .attr('d', path)
    .attr('fill', 'rgba(184,138,0,0.2)')
    .attr('stroke-width', 1);

  d3.geo.path();

  for (i in mapData) {
    mapCoords = xy([mapData[i].long, mapData[i].lat]);
    mapData[i].lat = mapCoords[0];
    mapData[i].long = mapCoords[1];
  }

  vis.selectAll("circle")
    .data(mapData)
    .enter().append("svg:circle")
    .attr("cx", function (d) {
      return d.lat
    })
    .attr("cy", function (d) {
      return d.long
    })
    .attr("stroke-width", "none")
    .attr("fill", function () {
      return "rgb(255,148,0)"
    })
    .attr("fill-opacity", .5)
    .attr("r", function (d) {
      return d.counter / 2;
    });

})(window.myInfo.mapData);
