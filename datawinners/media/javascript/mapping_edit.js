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
        $.post(SAVE_ENTITY_PREFERENCE_URL, { data: JSON.stringify({ filters: entityPreference.filters }) }).done(function(result) {
            console.log(result);
       });
    };

    var getEntityPreference = function() {
        $.getJSON(GET_ENTITY_PREFERENCE_URL).done(function(result) {
            var multiSelectWidgetAdapter = new DW.MultiSelectWidgetAdapter(result);
            var multiSelectWidget = new DW.MultiSelectWidget('#filters-widget', multiSelectWidgetAdapter.getFilters());
            multiSelectWidget.on('close', function (event) {
                console.log('closed');
                saveEntityPreference({ filters: event.detail.selectedValues });
            });
        });
    };

    self.init = function() {
        shareButton.click(onShare);
        shareWidgetCloseButton.click(onShareWidgetClose);
        getEntityPreference();
    }
}


DW.MultiSelectWidgetAdapter = function (entityPreference) {
    var _this = this;

    this.transformedEntityPreference = {};

    function transformFiltersForMultiSelectWidget(filters) {
        var transformedFilters = [];
        for(i in filters) {
            var transformedFilter = { value: filters[i].code, label: filters[i].label, checked: filters[i].visibility };
            transformedFilters.push(transformedFilter);
        }
        _this.transformedEntityPreference.filters = transformedFilters;
    }

    _this.getFilters = function () { return _this.transformedEntityPreference.filters; };

    transformFiltersForMultiSelectWidget(entityPreference.filters);
};