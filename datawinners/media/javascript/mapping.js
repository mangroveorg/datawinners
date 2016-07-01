function init_map2() {
    var count_click_on_map = 0;
    var nbr_listened_layer = 0;

    var view = new ol.View({
        maxZoom: 21,
        minZoom : 2,
        zoom: 2,
        center: [0, 0]
    });

    var base_map = new ol.layer.Group({
        'title': 'Maps',
        layers: [
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

    var map = new ol.Map({
        target: 'map',
        renderer: 'canvas',
        view: view
    });

    map.addLayer(base_map);
    map.addLayer(create_layer_vector(entity_type, '/media/images/pin_entity_1.png'));

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

    function create_layer_vector(name, image_url) {
        nbr_listened_layer++;

        var source = new ol.source.Vector({
            features: (new ol.format.GeoJSON()).readFeatures(geo_json, {featureProjection: 'EPSG:3857'})
        });

        var vector = new ol.layer.Vector({
            name: name,
            title: '<img src="' + image_url + '">' + name,
            source: source
        });

        var tooltip = [];
        source.forEachFeature(function(currentFeature){
            add_icon_toFeature(currentFeature, image_url);
            currentFeature.setId(currentFeature.get('short_code')['value']);
            tooltip[currentFeature.get('short_code')['value']] = new ol.Overlay.Popup({insertFirst: false});
            map.addOverlay(tooltip[currentFeature.get('short_code')['value']]);
        });

        var selected_features = [];
        map.on("click", function(e) {
            var listen_clicked_layer = false;
            count_click_on_map++;
            map.forEachFeatureAtPixel(e.pixel, function (feature, layer) {
                if(layer.get("name") == name){//avoid to listen other layer
                    listen_clicked_layer = true;
                    selected_features.push(feature);
                }
            });

            if(listen_clicked_layer && selected_features.length > 0) {
                var one_feature = selected_features[0];
                var coord = one_feature.getGeometry().getCoordinates();
                var popup_container = get_tooltip_content_from(one_feature);
                tooltip[one_feature.get('short_code')['value']].show(coord, popup_container);
                selected_features = [];
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