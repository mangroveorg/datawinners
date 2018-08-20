Map = function(fallbackLocation) {
    var self = this;
    var view = new ol.View({
            maxZoom: 19,
            minZoom: 3,
            zoom: 1,
            center: [0, 0]
        });
    view.on('change:center', function(event) {
        $('#map-center').val(event.target.get(event.key));
    });

    view.on('change:resolution', function(event) {
        $('#map-zoom').val(event.target.get(event.key));
    });

    var map = new ol.Map({
        target: 'map',
        renderer: 'canvas',
        view: view
    });
    var globalGeoJson = {};

    var popup = new ol.Overlay.Popup({
        insertFirst: false,
        panMapIfOutOfView: true
    });

    var layerGroup = function(title) {
        this.olGroup = new ol.layer.Group({
            'title': title
        });
        this.addLayer = function(layer) {
            var layers = this.olGroup.getLayers();
            layers.insertAt(layers.length, layer);
            this.olGroup.setLayers(layers);
        };
    };

    var addLayer = function(base, geoJsons, entityType) {
        geoJsons.forEach(function(geoJson){
            if (geoJson.group) {
                var group = new layerGroup(geoJson.group);
                base.addLayer(group.olGroup);
                addLayer(group, geoJson.data, entityType);
            } else {
                base.addLayer(createVector(geoJson.name, geoJson.data, geoJson.color, entityType));
            }
        })
    };

    self.init = function(entityType, geoJsons, mapboxApiKey) {
        map.addLayer(new ol.layer.Group({
            'title': 'Maps',
            layers: [
                new ol.layer.Tile({
                     title: 'Satellite',
                      type: 'base',
                      source: new ol.source.XYZ({
                        url: 'https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v9/tiles/256/{z}/{x}/{y}?access_token=' + mapboxApiKey,
                        attributions: [new ol.Attribution({
                            html: '© <a href=\'https://www.mapbox.com/about/maps/\'>Mapbox</a> © <a href=\'http://www.openstreetmap.org/copyright\'>OpenStreetMap</a>'
                        })]
                      })
                }),
                new ol.layer.Tile({
                    title: 'OpenStreetMap',
                    type: 'base',
                    visible: true,
                    source: new ol.source.OSM()
                })
            ]
        }));

        addLayer(map, geoJsons, entityType);

        map.addControl(new ol.control.LayerSwitcher());
        map.addControl(new ol.control.ScaleLine());
        map.addControl(new ol.control.Zoom());

        map.on("pointermove", setCursor);

        map.addOverlay(popup);

        map.on("click", function(e) {
            map.forEachFeatureAtPixel(e.pixel, function (feature, layer) {
                showDetails(feature);
                return true;
            });
        });

        loadFilters();

        $("#filters input").click(applyFilters);
        $("#filters select").change(applyFilters);

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

        geolocation.on('error', function(error) {
          if (fallbackLocation.center && fallbackLocation.resolution) {
            view.setCenter(fallbackLocation.center);
            map.getView().setResolution(fallbackLocation.resolution);
          }
          else{
           var vectorSource = new ol.source.Vector({
                features: (new ol.format.GeoJSON()).readFeatures(globalGeoJson, {featureProjection: 'EPSG:3857'})
            });
            map.getView().fit(vectorSource.getExtent(), map.getSize());
          }
        });

        $("#map").offset({top: $("#filter-control").height(), bottom: 0})
        map.updateSize();
    };

    var applyFilters = function() {
        var filters = [];
        $("#filters .filter-choices").each(function(){
            var question = $(this).attr("id");
            if($(this).find("input:checked").length > 0) {
                var answers = $(this).find("input:checked").map(function(elem){return this.id}).get();
                answers.forEach(function(answer){
                    filters.push(question + "=" + answer);
                });
            } else if($(this).find("select").length > 0) {
                var answer = $(this).find("select").val();
                filters.push(question + "=" + answer);
            }
        })
       
        window.location.href = window.location.origin + window.location.pathname + "?" + filters.join("&");
    };

    var loadFilters = function() {
        var filters = window.location.search.slice(1).split("&").filter(String);
        $.each(filters, function(index, filter){
            var question = filter.split("=")[0].replace(",", "\\,");
            var answers = filter.split("=")[1].split(",");
            $.each(answers, function(index, answer){
                var elem = $("#filters").find("#" + question)
                if(elem.find("input").length > 0) {
                    elem.find("#" + answer).attr("checked", "checked");
                } else if(elem.find("select").length > 0) {
                    elem.find("select").val(decodeURI(answer));
                }
            });
        });
    };

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
        //disable scrolling for outer element
        $('.ol-popup-content').on('touchstart', function(event) { event.preventDefault();});
        $('.ol-popup-content').on('touchmove', function(event) { event.preventDefault();});

        //stop scrolling event propagation from inner to outer element
        $('#pop-details').on('touchstart', function(event) { event.stopPropagation(); } );
        $('#pop-details').on('touchmove', function(event) { event.stopPropagation(); } );
    };

    var createVector = function(name, geoJson, color, entityType) {
        if (!fallbackLocation.center && !fallbackLocation.resolution){
            if ('features' in globalGeoJson) {
                if('features' in geoJson){
                    globalGeoJson.features.push.apply(globalGeoJson.features, geoJson.features);
                }
            }
            else{
                globalGeoJson = Object.assign(geoJson);
            }
        }
        var source = new ol.source.Vector({
            features: (new ol.format.GeoJSON()).readFeatures(geoJson, {featureProjection: 'EPSG:3857'})
        });

        var iconStyle = new ol.style.Style({
            image: new ol.style.Icon({
                src: '/media/images/map_marker.svg',
                color: color,
                anchor: [0.2, 0.7]
            })
        });

        $.ajax({url: '/media/images/map_marker.svg', success: function(response) {
            var layersTitle = $(".layer-switcher").find(".layer>label").filter(function() { return $(this).text().trim() == name });
            layersTitle.prepend(response.documentElement);
            layersTitle.find("path").attr("fill", color);
        }});

        var displayInLayerSwitcher = true;
        if (typeof(name) != "undefined"){
           if(name.toUpperCase() === entityType.toUpperCase()){
                displayInLayerSwitcher = false;
           }
        }

        return new ol.layer.Vector({
            name: name,
            title: name,
            source: source,
            style: iconStyle,
            displayInLayerSwitcher: displayInLayerSwitcher
        });
    };

    var setCursor = function (event) {
        var jTarget = $("#" + map.getTarget());
        if (map.hasFeatureAtPixel([event.originalEvent.offsetX, event.originalEvent.offsetY])) {
            jTarget.css("cursor", "pointer");
        } else {
            jTarget.css("cursor", "");
        }
    };
}