DW.MappingEditor = function(entityType) {
    var self = this;
    var shareButton = $("#share-button");
    var shareWidget = $("#share-widget");
    var shareWidgetCloseButton = $("#share-widget-close");
    var shareOverlay = $("#share-overlay");
    var filterFields = {};
    var GET_SHARE_TOKEN_URL = '/entity/' + entityType + '/sharetoken';
    var GET_ENTITY_PREFERENCE_URL = '/entity/' + entityType + '/get_preference';
    var SAVE_ENTITY_PREFERENCE_URL = '/entity/' + entityType + '/save_preference';

    var getFieldsForFilter = function() {
        var result = {};
        var selectedFields = $('#filter-fields option:selected').map(function(index, field) { return $(field).attr('name'); });
        return selectedFields.toArray();
    };

    var displayShareLink = function (token) {
        shareWidget.find('input').val(window.location.origin + "/public/maps/" + token)
        shareWidget.show();
        shareWidgetCloseButton.show();
        shareWidget.find('input').select();
        shareOverlay.height(getOverlayHeight()).show();
    }

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

    var transformer = function(item) {
        return { value: item.code, label: item.label, checked: item.visibility };
    }
    var getEntityPreference = function() {
        $.getJSON(GET_ENTITY_PREFERENCE_URL).done(function(result) {

            var transformedFilters = result.filters.map(transformer);
            var filtersWidget = new DW.MultiSelectWidget('#filters-widget', transformedFilters);
            filtersWidget.on('close', function (event) {
                saveEntityPreference({filters: event.detail.selectedValues});
            });

            var transformedDetails = result.details.map(transformer);
            var customizeWidget = new DW.MultiSelectWidget('#customize-widget', transformedDetails);
            customizeWidget.on('close', function (event) {
                saveEntityPreference({details: event.detail.selectedValues});
            });

        });
    };

    self.init = function() {
        shareButton.click(onShare);
        shareWidgetCloseButton.click(onShareWidgetClose);
        getEntityPreference();
    }
}

