function init_map() {
    "use strict";
    var project_id = $('#project_id').html();
    var map = new OpenLayers.Map({
        div: "map",
        projection: new OpenLayers.Projection("EPSG:900913"),
        displayProjection: new OpenLayers.Projection("EPSG:4326"),
        units: "m",
        maxResolution: 156543.0339,
        theme: null,
        maxExtent: new OpenLayers.Bounds(
            -20037508, -20037508, 20037508, 20037508
        ),
        controls: [
            new OpenLayers.Control.Navigation({dragPan: new OpenLayers.Control.DragPan()}),
            new OpenLayers.Control.PanZoomBar()

        ]
    });
    var layers = [];
    layers.push(new OpenLayers.Layer.Google("Google Layer", {
        sphericalMercator: true,
        displayInLayerSwitcher: false
    }));

    function add_layer(name, image, url) {
        name = '<img src="' + image + '">' + name;
        layers.push(new OpenLayers.Layer.Vector(name, {
            strategies: [new OpenLayers.Strategy.Fixed()],
            projection: new OpenLayers.Projection("EPSG:4326"),
            protocol: new OpenLayers.Protocol.HTTP({
                url: url,
                format: new OpenLayers.Format.GeoJSON()
            }),
            styleMap: new OpenLayers.StyleMap({
                "default": {
                    externalGraphic: image,
                    graphicWidth: 48, graphicHeight: 43,
                    graphicXOffset:-14, graphicYOffset:-37,  //tip of pin in icon is at 14,6 offset y is height - tipY
                    pointRadius: 8}
            })
        }));
    }
    var geo_url = '/get_geojson/' + project_id;

    for (var i = 0; i < entity_types.length; i++) {
        var entity_type = entity_types[i];
        var image_url = '/media/images/pin_entity_' + (i%10 + 1) + ".png";
        add_layer(entity_type, image_url, geo_url + "/" + entity_type)
    }

    add_layer(pgettext('datasender short','Data Senders'), '/media/images/pin_datasender.png', geo_url);

    var legends = new OpenLayers.Control.LayerSwitcher({ascending: false});
    map.addControl(legends);
    map.addLayers(layers);
    var proj = new OpenLayers.Projection("EPSG:4326");
    var point = new OpenLayers.LonLat(73.6962890625, 26.941659545381516);
    point.transform(proj, map.getProjectionObject());
    map.setCenter(point, 2);
    legends.maximizeControl();

}


function init_map2() {
    "use strict";
    var exampleLoc = ol.proj.transform([131.044922, -25.363882], 'EPSG:4326', 'EPSG:3857');
    var project_id = $('#project_id').html();
    var geo_url = '/get_geojson/' + project_id;
    var layers = [];
    var count_click_on_map = 0;
    var nbr_listened_layer = 0;
    var selected_layers = [];//manage multiple layers

    var view = new ol.View({
      // make sure the view doesn't go beyond the 22 zoom levels of Google Maps
      maxZoom: 21
    });
    view.setCenter([0, 0]);
    view.setZoom(1);

    layers.push(new ol.layer.Tile({source: new ol.source.MapQuest({layer: 'osm'})}));
    for (var i = 0; i < entity_types.length; i++) {
        var entity_type = entity_types[i];
        var image_url = '/media/images/pin_entity_' + (i%10 + 1) + ".png";
        layers.push(create_layer_vector(entity_type, image_url,geo_url + "/" + entity_type));
    }
    layers.push(create_layer_vector(pgettext('datasender short','Data Senders'),"/media/images/pin_datasender.png",geo_url));

    var map = new ol.Map({
      target: 'map',
      renderer: 'canvas',
      view: view,
      layers: layers
    });

    var my_tooltip = $('<img src="/media/images/pin_entity_1.png">')
        .css({marginTop: '-100%', marginLeft: '-30%', cursor: 'pointer'})//marginTop: '-200%', marginLeft: '-50%',
            //.tooltip({title: 'Hello, world!', trigger: 'click'});
            //
            //;

    var pin = new ol.Overlay({
        position: exampleLoc,
        element: my_tooltip[0]
      });

    var popup = new ol.Overlay.Popup({insertFirst: false});
    map.addOverlay(popup);

    my_tooltip.click(function(evt) {
        var prettyCoord = ol.coordinate.toStringHDMS(ol.proj.transform(exampleLoc, 'EPSG:3857', 'EPSG:4326'), 2);
        popup.show(exampleLoc, '<div><h2>Coordinates</h2><p>' + prettyCoord + '</p></div>');
    });

    map.addOverlay(pin);

    //#### define pointer style
    var cursorHoverStyle = "pointer";
    var target = map.getTarget();
    var jTarget = typeof target === "string" ? $("#"+target) : $(target);
    map.on("pointermove", function (event) {
        var mouseCoordInMapPixels = [event.originalEvent.offsetX, event.originalEvent.offsetY];
        var hit = map.forEachFeatureAtPixel(mouseCoordInMapPixels, function (feature, layer) {
            return true;
        });
        if (hit) {
            jTarget.css("cursor", cursorHoverStyle);
        } else {
            jTarget.css("cursor", "");
        }
    });

    function create_layer_vector(name, image, url) {
        nbr_listened_layer++;
        name = '<img src="' + image + '">' + name;
        var really_ready = false;
        var source = new ol.source.Vector({
            //features: new ol.format.GeoJSON().readFeatures(url)
                url: url,
                format: new ol.format.GeoJSON({
                    projection: "EPSG:3857"
                })
            });

        var vector = new ol.layer.Vector({
            name: name,
            source: source
        });

        source.on('change', function(evt){//Wait ajax is finished before getting features
            if(source.getState() === 'ready' && !really_ready){
                really_ready = true;
                console.debug("source ok : " + source.getFeatures());
                var features = source.getFeatures();
                console.debug("features.length : " + features.length);

                var tooltip = [];
                source.forEachFeature(function(currentFeature){
                    add_icon_toFeature(currentFeature, image);
                    tooltip[currentFeature] = new ol.Overlay.Popup({insertFirst: false});
                    map.addOverlay(tooltip[currentFeature]);
                });


                var selected_features = [];//manage multiple features
                    map.on("click", function(e) {
                        var listen_clicked_layer = false;
                        //count_click_on_map++;
                        //console.debug("click : " + count_click_on_map);
                        //var is_first_layer = (count_click_on_map % nbr_listened_layer) == 0;//the last clicked layer is the top layer on the map
                        //console.debug("click : " + count_click_on_map + "| " + is_first_layer);
                        map.forEachFeatureAtPixel(e.pixel, function (feature, layer) {
                            if(layer.get("name") == name){//avoid to listen other layer
                                listen_clicked_layer = true;
                                count_click_on_map++;
                                console.debug("click : " + count_click_on_map);
                                selected_features.push(feature);
                                //selected_layers.push(layer);
                                console.debug("Layer : " + layer.get("name"));
                            }
                        });

                        if(listen_clicked_layer && selected_features.length > 0){
                            var one_feature = selected_features[0];
                            var type = one_feature.getGeometry().getType();
                            var coord = one_feature.getGeometry().getCoordinates();

                            tooltip[one_feature].show(coord, '<div><h2>' + type + '</h2><p>Coord : ' + coord + '</p></div>');
                            selected_features = [];
                        }

                    });
            }
        });


        //for(var i=0; i< features.length; i++) {
        //    var currentFeature = features[i];
        //    add_icon_toFeature(currentFeature, image);
        //
        //}



        return vector;
    }

    function add_icon_toFeature(feature, image){
        var iconStyle = new ol.style.Style({
          image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
            anchor: [0.35, 0.7],//[0.35, 0.7]
            anchorXUnits: 'fraction',
            anchorYUnits: 'fraction',//or pixels
            opacity: 0.75,
            src: image
          }))
        });

        feature.setStyle(iconStyle);
    }
}