DW.MappingEditor = function(entityType, filters, details, specials) {
    var self = this;
    var shareButton = $("#share-button");
    var shareWidget = $("#share-widget");
    var shareWidgetCloseButton = $("#share-widget-close");
    var shareOverlay = $("#share-overlay");
    var filterFields = {};
    var GET_SHARE_TOKEN_URL = '/entity/' + entityType + '/sharetoken';
    var SAVE_ENTITY_PREFERENCE_URL = '/entity/' + entityType + '/save_preference';

    var specialsMap = specials.reduce(function(map, obj) {
        map[obj.code] = obj;
        return map;
    }, {});

    var displayShareLink = function (token) {
        shareWidget.find('input').val(window.location.origin + "/public/maps/" + token +"/")
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

    var saveEntityPreference = function(entityPreference, widget, saveCallback) {
        $.post(SAVE_ENTITY_PREFERENCE_URL, { data: JSON.stringify(entityPreference) }).done(function(result) {
            $("#map-preview").attr('src', $("#map-preview").attr('src'));
            widget.setItems(JSON.parse(result).specials.map(widgetDataTransformer));
            saveCallback && saveCallback(result);
        });
    };

    var sprintf = function(text) {
        var i=1, args=arguments;
        return text.replace(/%s/g, function(pattern){
            return (i < args.length) ? args[i++] : "";
        });
    };

    var createChoiceButtons = function(questionCode) {
        var choiceButtons = $("#special-idnrs>.choices").clone();

        specialsMap[questionCode].choices.forEach(function(item) {
            choiceButtons.append(
                sprintf(
                    choiceButtons.contents()[1].nodeValue,
                    questionCode, item.choice.val, specialsMap[questionCode].color,
                    item.visible?'checked':'', item.choice.text
                )
            );
        });

        return choiceButtons;
    };

    var createColorPicker = function() {
        var colorpicker = $("#special-idnrs>.colorpicker").clone();
        colorpicker.tinycolorpicker({backgroundUrl: '/media/images/text-color.png'});
        return colorpicker;
    };

    var onSpecialQuestionRender = function(widget, questionCode) {
        var questionLabel = $(widget).find('input[value=' + questionCode + ']').parent();
        var choiceButtons = createChoiceButtons(questionCode);
        var colorpicker = createColorPicker();

        questionLabel.after(choiceButtons);
        choiceButtons.after(colorpicker);

        choiceButtons.find("input").click(function() {
            colorpicker.find('.track').show();
        });

        colorpicker.click(function() {
            choiceButtons.find('input').css('background-color', $(this).find('input').val());
        });
    };

    var onSpecialQuestionCheck = function(widget, questionCode, showChoices) {
        var choiceButtons = $(widget).find('input[value=' + questionCode + ']').parent().next();
        if(showChoices) {
            choiceButtons.show();
        } else {
            choiceButtons.hide();
        }
    };

    var initWidget = function(widgetSelector, data, closeCallback) {
        var widget = new DW.MultiSelectWidget(widgetSelector, data);
        widget.on('close', function (event) {
            closeCallback(event.detail.selectedValues, widget, this);
        });
        return widget;
    };

    var widgetDataTransformer = function(item) {
        return { value: item.code, label: item.label, checked: item.visible };
    };

    self.init = function() {
        shareButton.click(onShare);
        shareWidgetCloseButton.click(onShareWidgetClose);

        initWidget('#filters-widget', filters.map(widgetDataTransformer), function(result, widget) {
            saveEntityPreference({filters: result}, widget);
        });

        initWidget('#customize-widget', details.map(widgetDataTransformer), function(result, widget) {
            saveEntityPreference({details: result}, widget);
        });

        var specialIdnrsWidget = initWidget('#special-idnrs-widget', specials.map(widgetDataTransformer),
            function(selectedValues, widget, widgetParentElement) {
                saveEntityPreference({
                    specials: selectedValues.reduce(function(map, code) {
                        var questionLabel = $(widgetParentElement).find('input[value=' + code + ']').parent();
                        var choiceButtons = questionLabel.next();
                        var colorpicker = choiceButtons.next();
                        map[code] = {choice: choiceButtons.find('input:checked').val(), color: choiceButtons.find('input:checked').css('background-color')}
                        return map;
                    }, {})
                },
                widget,
                function(result) {
                    specialsMap = JSON.parse(result).specials.reduce(function(map, obj) {
                        map[obj.code] = obj;
                        return map;
                    }, {});
                });
            }
        );

        specialIdnrsWidget.on('render', function(event) {
            var widget = this;
            event.detail.items.forEach(function(item) {
                onSpecialQuestionRender(widget, item.value);
                onSpecialQuestionCheck(widget, item.value, item.checked);
            })
        });

        specialIdnrsWidget.on('check', function(event) {
            if(event.detail.value in specialsMap) {
                onSpecialQuestionCheck(this, event.detail.value, event.detail.show);
            }
        });
    }
}

