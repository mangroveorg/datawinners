Map = function(geoJson) {
    var self = this;

    var map = new ol.Map({
        target: 'map',
        renderer: 'canvas',
        view: new ol.View({
            maxZoom: 21,
            minZoom : 2,
            zoom: 2,
            center: [0, 0]
        })
    });

    var popup = new ol.Overlay.Popup({
        insertFirst: false,
        panMapIfOutOfView: false
    });

    self.init = function(entityType) {
        var baseLayer = new ol.layer.Group({
            'title': 'Maps',
            layers: [
                new ol.layer.Tile({
                    title: 'OpenStreetMap',
                    type: 'base',
                    visible: true,
                    source: new ol.source.MapQuest({
                        layer: 'osm'
                    })
                }),
                new ol.layer.Tile({
                    title: 'Satellite',
                    type: 'base',
                    visible: false,
                    source: new ol.source.MapQuest({
                        layer: 'sat'
                    })
                })
            ]
        });

        map.addLayer(baseLayer);
        map.addLayer(createVector(entityType));

        map.addControl(new ol.control.LayerSwitcher());
        map.addControl(new ol.control.ScaleLine());
        map.addControl(new ol.control.FullScreen());
        map.addControl(new ol.control.ZoomSlider());
        map.addControl(new ol.control.OverviewMap());

        map.on("pointermove", setCursor);

        map.addOverlay(popup);

        map.on("click", function(e) {
            map.forEachFeatureAtPixel(e.pixel, function (feature, layer) {
                showDetails(feature);
            });
        });
    }

    var showDetails = function(feature) {
        var html = $("#popup").html()
            .replace("{entity}", feature.getProperties()["name"]["value"])
            .replace("{entity_type}", feature.getProperties()["entity_type"]["value"])
            .replace("{geo_code}", feature.getProperties()["geo_code"]["value"])
            .replace("{entity_code}", feature.getProperties()["short_code"]["value"]);
        popup.show(feature.getGeometry().getCoordinates(), html);
    }

    var createVector = function(name, iconStyle) {
        var source = new ol.source.Vector({
            features: (new ol.format.GeoJSON()).readFeatures(geoJson, {featureProjection: 'EPSG:3857'})
        });

        var defaultIconSource = '/media/images/pin_entity_1.png';
        var defaultIconStyle = new ol.style.Style({
            image: new ol.style.Icon({
                anchor: [0.55, 0.8],
                anchorXUnits: 'fraction',
                anchorYUnits: 'fraction',
                src: defaultIconSource
            })
        });

        var iconSource = iconStyle ? iconStyle.getImage().getSrc() : defaultIconSource;
        return new ol.layer.Vector({
            name: name,
            title: '<img src="' + iconSource  + '">' + name,
            source: source,
            style: iconStyle || defaultIconStyle
        });
    }


    var setCursor = function (event) {
        var jTarget = $("#" + map.getTarget());
        if (map.hasFeatureAtPixel([event.originalEvent.offsetX, event.originalEvent.offsetY])) {
            jTarget.css("cursor", "pointer");
        } else {
            jTarget.css("cursor", "");
        }
    }
}