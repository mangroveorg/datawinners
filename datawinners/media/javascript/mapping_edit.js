DW.MappingEditor = function(entityType) {
    var self = this;
    var shareButton = $("#share-button");
    var shareWidget = $("#share-widget");
    var shareWidgetCloseButton = $("#share-widget-close");
    var shareOverlay = $("#share-overlay");

    var onShare = function() {
        $.getJSON('/entity/' + entityType + '/sharetoken', function (result) {
            shareWidget.find('input').val(window.location.origin + "/public/maps/" + result.token)
            shareWidget.show();
            shareWidgetCloseButton.show();
            shareWidget.find('input').select();
            shareOverlay.height(getOverlayHeight()).show();
        });
    }

    var onShareWidgetClose = function() {
        shareWidget.hide();
        shareWidgetCloseButton.hide();
        shareOverlay.hide();
    }

    self.init = function() {
        shareButton.click(onShare);
        shareWidgetCloseButton.click(onShareWidgetClose);
    }
}