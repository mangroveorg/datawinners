OpenLayers.ProxyHost = "proxy.cgi?url=";

DW.map_loader = function() {
    this.layer;
    this.styleMap;
    this.myStyles;
    this.map = new OpenLayers.Map({
                div: "map",
                projection: new OpenLayers.Projection("EPSG:900913"),
                displayProjection: new OpenLayers.Projection("EPSG:4326"),
                units: "m",
                maxResolution: 156543.0339,
                theme : null,
                maxExtent: new OpenLayers.Bounds(
                    -20037508, -20037508, 20037508, 20037508
                ),
                controls: [
                    new OpenLayers.Control.PanZoomBar()
                ]
    });
    this.user_location = [
                            { latitude: 47.670553,
                              longitude: 9.588479},
                            { latitude: 47.65197522925437,
                              longitude: 9.47845458984375 },
                            { latitude: 47.594996,
                              longitude: 9.600708},
                            { latitude: 47.794996,
                              longitude: 9.400708},
                            { latitude: 47.564996,
                              longitude: 9.300708},
                            { latitude: 47.564996,
                              longitude: 9.430708},
                            { latitude: 47.564996,
                              longitude: 9.730708}
                            ]
    this._init();
    this._styleMap();
    this._drawMap();
}
DW.map_loader.prototype = {
    _init : function(){
        var map = this.map,
        self = this;

            var g = new OpenLayers.Layer.Google("Google Layer", {
            sphericalMercator: true
            });
            map.addLayers([g]);

            //Creating geometric points from latitude and longitude, converting it to vector to add it on the map
            for (var i=0; i<self.user_location.length; i++) {
               var points = new OpenLayers.Geometry.Point(
                        self.user_location[i].longitude, self.user_location[i].latitude
                    );
                points.transform(map.displayProjection, map.getProjectionObject());
                self.user_location[i] = new OpenLayers.Feature.Vector(
                    points,{
                        type: 13 + parseInt(5 * Math.random())
                    }
                );
            }
    },
    _styleMap : function(){

            // Create a styleMap to style your vector maps.
             this.myStyles = new OpenLayers.StyleMap({
                "default": new OpenLayers.Style({
                    pointRadius: "${type}", // sized according to type attribute
                    fillColor: "#ff0000",
                    strokeColor: "#ff0000",
                    strokeWidth: 2,
                    graphicZIndex: 1,
                    fillOpacity:0.7,
                    strokeOpacity:0.7
                }),
                "select": new OpenLayers.Style({
                    fillColor: "#66ccff",
                    strokeColor: "#3399ff",
                    graphicZIndex: 2
                })
            });

    },
    _drawMap : function(){

            // Create a vector layer and give it your style map.
            var myStyles = this.myStyles,
                map = this.map,
                self = this,
             points = new OpenLayers.Layer.Vector("Points", {
                styleMap: myStyles,
                rendererOptions: {zIndexing: true}
            });
            points.addFeatures(self.user_location);
            map.addLayers([points]);

            // Create a select feature control and add it to the map.
            var select = new OpenLayers.Control.SelectFeature(points, {hover: true});
            map.addControl(select);
            select.activate();

            //Intial focus point on the map, defined by the first data received, (right now its hard coded)
            var focus = new OpenLayers.LonLat(9.588479, 47.670553);
            focus.transform(map.displayProjection, map.getProjectionObject())
            map.setCenter(focus,9);
    }

}

$(document).ready(function(){

    new DW.map_loader();

});
