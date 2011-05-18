var map, layer, styleMap;
OpenLayers.ProxyHost = "proxy.cgi?url=";

function init() {
    map = new OpenLayers.Map({
        div: "map",
        projection: new OpenLayers.Projection("EPSG:900913"),
        displayProjection: new OpenLayers.Projection("EPSG:4326"),
        units: "m",
        maxResolution: 156543.0339,
        maxExtent: new OpenLayers.Bounds(
            -20037508, -20037508, 20037508, 20037508
        )
    });

    var g = new OpenLayers.Layer.Google("Google Layer", {
        sphericalMercator: true
    });
    map.addLayers([g]);

    var user_location = [
                    { latitude: 47.670553,
                      longitude: 9.588479},
                    { latitude: 47.65197522925437,
                      longitude: 9.47845458984375 },
                    { latitude: 47.594996,
                      longitude: 9.600708},
                    { latitude: 47.794996,
                      longitude: 9.400708},
                    { latitude: 47.564996,
                      longitude: 9.300708}
                    ]


    for (var i=0; i<user_location.length; i++) {
       var points = new OpenLayers.Geometry.Point(
                user_location[i].longitude, user_location[i].latitude
            );
        points.transform(map.displayProjection, map.getProjectionObject());
        user_location[i] = new OpenLayers.Feature.Vector(
            points,{
                type: 10 + parseInt(5 * Math.random())
            }
        );
    }

    // Create a styleMap to style your features for two different
    // render intents.  The style for the 'default' render intent will
    // be applied when the feature is first drawn.  The style for the
    // 'select' render intent will be applied when the feature is
    // selected.
    var myStyles = new OpenLayers.StyleMap({
        "default": new OpenLayers.Style({
            pointRadius: "${type}", // sized according to type attribute
            fillColor: "#ff0000",
            strokeColor: "#ff0000",
            strokeWidth: 2,
            graphicZIndex: 1,
            fillOpacity:0.6,
            strokeOpacity:0.6
        }),
        "select": new OpenLayers.Style({
            fillColor: "#66ccff",
            strokeColor: "#3399ff",
            graphicZIndex: 2
        })
    });

    // Create a vector layer and give it your style map.
    var points = new OpenLayers.Layer.Vector("Points", {
        styleMap: myStyles,
        rendererOptions: {zIndexing: true}
    });
    points.addFeatures(user_location);
    map.addLayers([points, g]);

    // Create a select feature control and add it to the map.
    var select = new OpenLayers.Control.SelectFeature(points, {hover: true});
    map.addControl(select);
    select.activate();

    //Intial focus point on the map, defined by the first data received
    var focus = new OpenLayers.LonLat(9.588479, 47.670553);
    focus.transform(map.displayProjection, map.getProjectionObject())
    map.setCenter(focus,8);

    
}
window.onload = init;
