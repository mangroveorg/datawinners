DW.MappingEditor = function(entityType, filters, details, specials) {
    var self = this;
    var shareButton = $("#share-button");
    var shareWidget = $("#share-widget");
    var shareWidgetDoneButton = $("#share-widget-done");
    var shareOverlay = $("#share-overlay");
    var freezeButton = $('#freeze-map');
    var mapPreviewWindow = $('#map-preview');
    var successMessage = $('#success-message');
    var filterFields = {};
    var filterWidgetTitle = 'Choose how to filter ' + entityType;
    var customizeWidgetTitle = 'Choose which details to display for each ' + entityType;
    var specialIdnrsWidgetTitle = 'Choose how to color for each ' + entityType;
    var GET_SHARE_TOKEN_URL = '/entity/' + entityType + '/sharetoken';
    var SAVE_ENTITY_PREFERENCE_URL = '/entity/' + entityType + '/save_preference';

    var specialsMap = specials.reduce(function(map, obj) {
        map[obj.code] = obj;
        return map;
    }, {});

    var displayShareLink = function (token) {
        shareWidget.find('input').val(window.location.origin + "/public/maps/" + token +"/")
        shareWidget.show();
        shareWidget.find('input').select();
        shareOverlay.height(getOverlayHeight()).show();
        shareButton.addClass('highlight');
    };

    var onShare = function() {
       $.getJSON(GET_SHARE_TOKEN_URL).done(function(result) {
            displayShareLink(result.token);
       });
    };

    var onShareWidgetClose = function() {
        shareWidget.hide();
        shareOverlay.hide();
        shareButton.removeClass('highlight');
    };

    var saveEntityPreference = function(entityPreference, saveCallback) {
        $.post(SAVE_ENTITY_PREFERENCE_URL, { data: JSON.stringify(entityPreference) }).done(function(result) {
            saveCallback(result);
        });
    };

    var reloadMapPreview = function() {
        mapPreviewWindow.attr('src', mapPreviewWindow.attr('src'));
    };

    var showSuccessMessage = function(message) {
         successMessage.text(message)
         successMessage.show()
         setTimeout(function() { successMessage.hide(); }, 4000);
    };

    var saveEntityPreferenceAndReloadMapPreview = function(entityPreference, saveCallback) {
        saveEntityPreference(entityPreference, function(result) {
            saveCallback(result);
            showSuccessMessage("Your changes have been saved.");
            reloadMapPreview();
        })
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
                    item.choice.val, item.color, item.visible?'checked':'', item.choice.text
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
        questionLabel.find("p").attr("data-toggle", "tooltip");
        questionLabel.find("p").attr("title", questionLabel.find("p")[0].innerHTML);
        var choiceButtons = createChoiceButtons(questionCode);
        choiceButtons.find("p").attr("data-toggle", "tooltip");
        var choiceButtonArray = choiceButtons.find("p");
        for(i=0; i<choiceButtonArray.length; i++){
            choiceButtonArray[i].title = choiceButtonArray[i].innerHTML;
        }
        var colorpicker = createColorPicker();

        questionLabel.after(choiceButtons);
        choiceButtons.after(colorpicker);

        choiceButtons.find("input").click(function() {
            if($(this).is(':checked')) {
                $(this).attr('checked', false);
                $(this).attr('waiting', true);
                colorpicker.find('.track').show();
            }
        });

        colorpicker.click(function() {
            choiceButtons.find('input[waiting="true"]').attr("checked", true);
            choiceButtons.find('input[waiting="true"]').css('background-color', $(this).find('input').val());
            choiceButtons.find('input[waiting="true"]').attr("waiting", false);
        });
    };

    var onSpecialQuestionCheck = function(widget, questionCode, showChoices) {
        var input = $(widget).find('input[value=' + questionCode + ']')
        var choiceButtons = $(widget).find('input[value=' + questionCode + ']').parent().next();
        input.parents("li").siblings().find("p").removeClass("highlight")
        input.parents("li").find("p").addClass("highlight");
        if(showChoices) {
            input.attr("checked", true);
            input.parents("li").siblings().hide();
            input.parents("li").show();
            choiceButtons.show();
        } else {
            input.attr("checked", false);
            input.parents("li").siblings().show();
            choiceButtons.hide();
            choiceButtons.find('input').attr("checked", false);
            choiceButtons.find('input').css("background-color", "none");
            choiceButtons.next().find('.track').hide();
        }
    };

    var onFreeze = function() {
        var center = mapPreviewWindow.contents().find('#map-center').val().split(",");
        var resolution = mapPreviewWindow.contents().find('#map-zoom').val();
        mapPreviewWindow.addClass("do-freeze");
        setTimeout(function() { mapPreviewWindow.removeClass("do-freeze"); }, 500);
        if (!!resolution && !!center.toString()) {
            saveEntityPreference({ fallback_location: { center: center, resolution: resolution } }, function(){});
        }
    };

    var initWidget = function(widgetSelector, data, closeCallback, title) {
        var widget = new DW.MultiSelectWidget(widgetSelector, data, title || 'Choose which details to display for each <ID NR Type>');
        widget.on('select', function () {
            shareOverlay.height(getOverlayHeight()).show();
        });
        widget.on('close', function (event) {
            shareOverlay.hide();
        });
        widget.on('done', function (event) {
            shareOverlay.hide();
            closeCallback(event.detail.selectedValues, widget, this);
        });
        return widget;
    };

    var widgetDataTransformer = function(item) {
        return { value: item.code, label: item.label, checked: item.visible };
    };

    self.init = function() {
        shareButton.click(onShare);
        shareWidgetDoneButton.click(onShareWidgetClose);
        freezeButton.click(onFreeze);

        initWidget('#filters-widget', filters.map(widgetDataTransformer), function(selectedValues, widget) {
            saveEntityPreferenceAndReloadMapPreview({filters: selectedValues}, function(result){
                widget.setItems(JSON.parse(result).filters.map(widgetDataTransformer));
            });
        }, filterWidgetTitle);

        initWidget('#customize-widget', details.map(widgetDataTransformer), function(selectedValues, widget) {
            saveEntityPreferenceAndReloadMapPreview({details: selectedValues}, function(result) {
                widget.setItems(JSON.parse(result).details.map(widgetDataTransformer));
            });
        }, customizeWidgetTitle);

        var specialIdnrsWidget = initWidget('#special-idnrs-widget', specials.map(widgetDataTransformer),
            function(selectedValues, widget, widgetParentElement) {
                saveEntityPreferenceAndReloadMapPreview({
                    specials: selectedValues.reduce(function(map, code) {
                        var questionLabel = $(widgetParentElement).find('input[value=' + code + ']').parent();
                        var choiceButtons = questionLabel.next();
                        var colorpicker = choiceButtons.next();
                        map[code] = choiceButtons.find('input:checked').map(function(i, e){
                            return {value: $(e).val(), color: $(e).css('background-color')}
                        }).get()
                        return map;
                    }, {})
                },
                function(result) {
                    specialsMap = JSON.parse(result).specials.reduce(function(map, obj) {
                        map[obj.code] = obj;
                        return map;
                    }, {});
                    widget.setItems(JSON.parse(result).specials.map(widgetDataTransformer));
                });
            }
        , specialIdnrsWidgetTitle);

        specialIdnrsWidget.on('render', function(event) {
            var widget = this;
            var checkedItem = event.detail.items[0]
            event.detail.items.forEach(function(item) {
                if(item.checked) {
                    checkedItem = item
                }
                onSpecialQuestionRender(widget, item.value);
            })
            onSpecialQuestionCheck(widget, checkedItem.value, true);
        });

        specialIdnrsWidget.on('check', function(event) {
            if(event.detail.value in specialsMap) {
                onSpecialQuestionCheck(this, event.detail.value, event.detail.show);
            }
        });
    }
}

