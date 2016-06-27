function init_map2() {
    "use strict";
    var project_id = $('#project_id').html();
    var label_idn = $('#map_identification_number').text();
    console.debug("label " + label_idn);
    var geo_url = '/get_geojson/';
    var layers = [];
    var count_click_on_map = 0;
    var nbr_listened_layer = 0;
    var selected_layers = [];//manage multiple layers

    var view = new ol.View({
      // make sure the view doesn't go beyond the 22 zoom levels of Google Maps
      maxZoom: 21,
      minZoom : 2,
      //maxResolution : 156543.0339,
      //  maxExtent: [-20037508, -20037508, 20037508, 20037508],
      //  units: "m",
        zoom: 2
    });
    view.setCenter([0, 0]);

    var Base_map = new ol.layer.Group({
                'title': 'Maps',
                layers: [
                    new ol.layer.Tile({
                        title: 'Water color',
                        type: 'base',
                        visible: false,
                        source: new ol.source.Stamen({
                            layer: 'watercolor'
                        })
                    }),
                    new ol.layer.Tile({
                        title: 'Toner',
                        type: 'base',
                        visible: false,
                        source: new ol.source.Stamen({
                            layer: 'toner'
                        })
                    }),
                    //new ol.layer.Tile({
                    //    title: 'OpenStreetMap',
                    //    type: 'base',
                    //    visible: true,
                    //    source: new ol.source.OSM()
                    //}),
                    new ol.layer.Tile({
                        title: 'OpenStreetMap',
                        type: 'base',
                        visible: true,
                        source: new ol.source.MapQuest({layer: 'osm'})
                    }),
                    new ol.layer.Tile({
                        title: 'Satellite',
                        type: 'base',
                        visible: false,
                        source: new ol.source.MapQuest({layer: 'sat'})
                    })
                ]
            });
    layers.push(Base_map);

    var image_url = '/media/images/pin_entity_1.png';
    layers.push(create_layer_vector(entity_type, image_url, geo_url + entity_type));

    var map = new ol.Map({
      target: 'map',
      renderer: 'canvas',
      view: view,
      layers: layers
    });

    map.addControl(new ol.control.LayerSwitcher());
    map.addControl(new ol.control.ScaleLine());
    map.addControl(new ol.control.FullScreen());
    map.addControl(new ol.control.ZoomSlider());
    map.addControl(new ol.control.OverviewMap());

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
                url: url,
                format: new ol.format.GeoJSON({
                    projection: "EPSG:3857"
                })
            });

        var vector = new ol.layer.Vector({
            title: name,
            name: name,
            source: source
        });

        source.on('change', function(evt){//Wait ajax is finished before getting features
            if(source.getState() === 'ready' && !really_ready){
                really_ready = true;
                var features = source.getFeatures();
                var tooltip = [];
                source.forEachFeature(function(currentFeature){
                    add_icon_toFeature(currentFeature, image);
                    currentFeature.setId(currentFeature.get('short_code')['value']);//for comparison
                    tooltip[currentFeature.get('short_code')['value']] = new ol.Overlay.Popup({insertFirst: false});
                    map.addOverlay(tooltip[currentFeature.get('short_code')['value']]);
                });


                var selected_features = [];//manage multiple features
                    map.on("click", function(e) {
                        var listen_clicked_layer = false;
                        count_click_on_map++;
                        map.forEachFeatureAtPixel(e.pixel, function (feature, layer) {
                            if(layer.get("name") == name){//avoid to listen other layer
                                listen_clicked_layer = true;

                                selected_features.push(feature);

                            }
                        });


                        if(listen_clicked_layer && selected_features.length > 0){
                            var one_feature = selected_features[0];
                            var coord = one_feature.getGeometry().getCoordinates();
                            var popup_container = get_tooltip_content_from(one_feature);
                            tooltip[one_feature.get('short_code')['value']].show(coord, popup_container);
                            selected_features = [];
                        }else{
                            selected_layers = [];
                        }

                    });
            }
        });

        return vector;
    }

    function add_icon_toFeature(feature, image){
        var iconStyle = new ol.style.Style({
          image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
            anchor: [0.55, 0.8],//[0.35, 0.7]
            anchorXUnits: 'fraction',
            anchorYUnits: 'fraction',//or pixels
            //opacity: 0.75,
            src: image
          }))
        });

        feature.setStyle(iconStyle);
    }

    function get_tooltip_content_from(feature){
        var type = feature.getGeometry().getType();
        var obj_prop = feature.getProperties(), prop;
        var popup_content = "", popup_head = "", popup_gps = "";
        for(prop in obj_prop){
            if(prop !== "geometry"){
                if(prop === "name"){
                    popup_head = ''
                        +'<p class = "p_head" title="' + obj_prop[prop]['label']+'">'
                        + join(obj_prop[prop]['value']," ") + "</p><hr/>";
                    popup_head +=  '<p>' + obj_prop["entity_type"]['value']
                        + ' <code class="p_short_code" title="'
                        + obj_prop["short_code"]['label']+'">'
                        + obj_prop["short_code"]['value'] + '</code></p>';
                }else if(prop === "geo_code"){
                    popup_gps =   '<p><code class="p_geo_code" title="'+obj_prop[prop]['label']+'">'
                        + join(obj_prop[prop]['value'], ", ") +'</code><p/>';
                }else if (prop === "entity_type" || prop === "short_code"){
                    //just a control
                }else{
                    if(obj_prop[prop] !== false){//avoid false value (for reporter)
                        popup_content +=   '<p title="'+obj_prop[prop]['label']+'">';
                        popup_content +=   join(obj_prop[prop]['value'], " ") + "</p>" ;
                    }
                }
            }
        }
        popup_content = popup_gps + popup_content;
        return ('<div>'+ popup_head + '<p>'+ popup_content +'</p></div>');
    }
    function join(my_array, separator){//if we want to join array before
        if(Array.isArray(my_array)){
            return my_array.join(separator);
        }else{
            return my_array;
        }
    }
}