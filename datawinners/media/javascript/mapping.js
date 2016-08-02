Map = function(geoJson) {
    var self = this;

    var map = new ol.Map({
        target: 'map',
        renderer: 'canvas',
        view: new ol.View({
            maxZoom: 19,
            minZoom: 2,
            zoom: 2,
            center: [0, 0]
        })
    });

    var popup = new ol.Overlay.Popup({
        insertFirst: false,
        panMapIfOutOfView: true
    });

    self.init = function(entityType) {
        map.addLayer(new ol.layer.Group({
            'title': 'Maps',
            layers: [
                new ol.layer.Tile({
                    title: 'OpenStreetMap',
                    type: 'base',
                    visible: true,
                    source: new ol.source.OSM()
                })
            ]
        }));
        map.addLayer(createVector(entityType));

        map.addControl(new ol.control.LayerSwitcher());
        map.addControl(new ol.control.ScaleLine());
        map.addControl(new ol.control.FullScreen());
        map.addControl(new ol.control.Zoom());
        map.addControl(new Geocoder('nominatim', {
            provider: 'osm',
            lang: 'km',
            placeholder: 'Search for ...',
            limit: 5
        }));
        map.addControl(new ol.control.Control({
            element: $("#filter-control")[0]
        }));

        map.on("pointermove", setCursor);

        map.addOverlay(popup);

        map.on("click", function(e) {
            map.forEachFeatureAtPixel(e.pixel, function (feature, layer) {
                showDetails(feature);
                return true;
            });
        });

        loadFilters();

        $("#filter-control>button").click(function() {
            $("#filters").toggle();
            $("#filters .filters-content").accordion();
        });

        $("#filters button.apply").click(applyFilters);
        $("#filters button.reset").click(function(){
            window.location.href = window.location.origin + window.location.pathname;
        });

        var geolocation = new ol.Geolocation({
            projection: 'EPSG:3857',
            tracking: true
        });

        geolocation.once('change', function(evt) {
            map.getView().setCenter(geolocation.getPosition());
            var pan = ol.animation.pan({source:geolocation.getPosition(), duration:1000});
            var zoom = ol.animation.zoom({resolution: map.getView().getResolution(), duration:3000});
            map.beforeRender(pan);
            map.beforeRender(zoom);
            map.getView().setResolution(map.getView().getResolution() / 512);
        });
    }

    var applyFilters = function() {
        var filters = [];
        $("#filters .filter-choices").each(function(){
            if($(this).find("input:checked").length > 0) {
                var question = $(this).attr("id");
                var answers = $(this).find("input:checked").map(function(elem){return this.id});
                filters.push(question + "=" + Array.prototype.join.call(answers));
            }
        })
        window.location.href = window.location.origin + window.location.pathname + "?" + filters.join("&");
    }

    var loadFilters = function() {
        var filters = window.location.search.slice(1).split("&").filter(String);
        $.each(filters, function(index, filter){
            var question = filter.split("=")[0];
            var answers = filter.split("=")[1].split(",");
            $.each(answers, function(index, answer){
                $("#filters").find("#" + question).find("#" + answer).attr("checked", "checked");
            });
        });
    }

    var getPopupTitle = function(properties) {
        return Object.keys(properties)
                .filter(function(key) {
                    return key === 'name';
                })
                .map(function(key) {
                    return properties[key].value;
                })[0];
    };

    var transformFeatureToDetails = function(properties) {
        return Object.keys(properties)
                .filter(function(key) {
                    return key !== 'name';
                })
                .map(function(key) {
                    return properties[key];
                })
                .filter(function(property) {
                   return property.value && property.label;
                });
    };

    var buildPopupHeader = function(title) {
        var popup = $('#popup');
        $('#popup h3').remove();
        var headerTemplate = $('#popup').contents()[1].nodeValue;
        return sprintf(headerTemplate, title);
    };

    var buildPopupContent = function(items) {
        var list = $("#popup ul");
        $('#popup ul li').remove();
        items.forEach(function(item){
            addItem(list, item.value, item.label);
        });
        return list;
    };

    var addItem = function(list, answer, question) {
        var template = list.contents()[1].nodeValue;
        list.append(sprintf(template, question, answer));
    };

    var sprintf = function(text) {
        var i=1, args=arguments;
        return text.replace(/%s/g, function(pattern){
            return (i < args.length) ? args[i++] : "";
        });
    };

    var showDetails = function(feature) {
        var title = getPopupTitle(feature.getProperties());
        var header = buildPopupHeader(title);

        var items = transformFeatureToDetails(feature.getProperties());
        var content = buildPopupContent(items)[0].outerHTML;
        popup.show(feature.getGeometry().getCoordinates(), header + content);
    };

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