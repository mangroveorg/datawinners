DW.MappingEditor = function(entityType, filters, details, specials) {
    var self = this;
    var shareButton = $("#share-button");
    var shareWidget = $("#share-widget");
    var shareWidgetCloseButton = $("#share-widget-close");
    var shareOverlay = $("#share-overlay");
    var filterFields = {};
    var GET_SHARE_TOKEN_URL = '/entity/' + entityType + '/sharetoken';
    var GET_ENTITY_PREFERENCE_URL = '/entity/' + entityType + '/get_preference';
    var SAVE_ENTITY_PREFERENCE_URL = '/entity/' + entityType + '/save_preference';

    var displayShareLink = function (token) {
        shareWidget.find('input').val(window.location.origin + "/public/maps/" + token)
        shareWidget.show();
        shareWidgetCloseButton.show();
        shareWidget.find('input').select();
        shareOverlay.height(getOverlayHeight()).show();
    };

    var onShare = function() {
       $.getJSON(GET_SHARE_TOKEN_URL).done(function(result) {
            displayShareLink(result.token);
       });
    };

    var onShareWidgetClose = function() {
        shareWidget.hide();
        shareWidgetCloseButton.hide();
        shareOverlay.hide();
    };

    var saveEntityPreference = function(entityPreference) {
        $.post(SAVE_ENTITY_PREFERENCE_URL, { data: JSON.stringify(entityPreference) }).done(function(result) {
            $("#map-preview").attr('src', $("#map-preview").attr('src'));
        });
    };

    var sprintf = function(text) {
        var i=1, args=arguments;
        return text.replace(/%s/g, function(pattern){
            return (i < args.length) ? args[i++] : "";
        });
    };
    
    var onSpecialQuestionCheck = function(widget, questionCode, showChoices, choices) {
        var questionBox = $(widget).find('input[value=' + questionCode + ']');
        var choiceButtons = $("#special-idnrs>ul").clone();
        if(showChoices) {
            choices.forEach(function(item) {
                choiceButtons.append(sprintf(choiceButtons.contents()[1].nodeValue, item.val, item.text));
            });
            questionBox.next().after(choiceButtons);
            choiceButtons.show();
        } else {
            questionBox.next().nextAll().remove();
        }
    };

    var initWidget = function(widgetSelector, data, saveCallback) {
        var transformedData = data.map(function(item) {
            return { value: item.code, label: item.label, checked: item.visibility };
        });
        var widget = new DW.MultiSelectWidget(widgetSelector, transformedData);
        widget.on('close', function (event) {
            saveCallback(event.detail.selectedValues);
        });
        return widget;
    };

    self.init = function() {
        shareButton.click(onShare);
        shareWidgetCloseButton.click(onShareWidgetClose);

        initWidget('#filters-widget', filters, function(result) {
            saveEntityPreference({filters: result});
        });

        initWidget('#customize-widget', details, function(result) {
            saveEntityPreference({details: result});
        });

        var specialIdnrsWidget = initWidget('#special-idnrs-widget', filters, function(result) {
            saveEntityPreference({specials: result});
        });

        var specialsMap = specials.reduce(function(map, obj) {
            map[obj.code] = obj;
            return map;
        }, {});

        specialIdnrsWidget.on('render', function(event) {
            var widget = this;
            event.detail.items.forEach(function(item) {
                onSpecialQuestionCheck(widget, item.value, specialsMap[item.value].visibility, specialsMap[item.value].choices);
            })
        });

        specialIdnrsWidget.on('check', function(event) {
            onSpecialQuestionCheck(this, event.detail.value, event.detail.show, specialsMap[event.detail.value].choices);
        });
    }
}

