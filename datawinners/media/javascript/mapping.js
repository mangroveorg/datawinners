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

    add_layer(gettext('Datasenders'), '/media/images/pin_datasender.png', geo_url);

    var legends = new OpenLayers.Control.LayerSwitcher({ascending: false});
    map.addControl(legends);
    map.addLayers(layers);
    var proj = new OpenLayers.Projection("EPSG:4326");
    var point = new OpenLayers.LonLat(73.6962890625, 26.941659545381516);
    point.transform(proj, map.getProjectionObject());
    map.setCenter(point, 2);
    legends.maximizeControl();

}


