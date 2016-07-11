DW.MappingEditor = function(entityType) {
    var self = this;
    var shareButton = $("#share-button");
    var shareWidget = $("#share-widget");
    var shareWidgetCloseButton = $("#share-widget-close");
    var shareOverlay = $("#share-overlay");
    var filterFields = {};
    var ENTITY_PREFERENCE_URL = '/entity/' + entityType + '/sharetoken';

    var getFieldsForFilter = function() {
        var result = {};
        var selectedFields = $('#filter-fields option:selected').map(function(index, field) { return { name: $(field).attr('name'), label : $(field).val() } });
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
       //     TODO: remove JSON parsing
       var selectedFields = getFieldsForFilter();
       $.post(ENTITY_PREFERENCE_URL, { data: JSON.stringify(selectedFields) }).done(function(result) {
            displayShareLink(JSON.parse(result).token);
       });
    };

    var onShareWidgetClose = function() {
        shareWidget.hide();
        shareWidgetCloseButton.hide();
        shareOverlay.hide();
    };

    var selectExistingFilterFields = function() {
        $.getJSON(ENTITY_PREFERENCE_URL).done(function(result) {
            var selectedFieldsNames =  result.filters.map(function(item) { return item['name']; });
            $('#filter-fields option').filter(function(index, field) {
                return selectedFieldsNames.indexOf($(field).attr('name')) !== -1;
            }).prop('selected', true);
        });
    };

    self.init = function() {
        shareButton.click(onShare);
        shareWidgetCloseButton.click(onShareWidgetClose);
        selectExistingFilterFields();
    }
}