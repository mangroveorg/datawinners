DW.MappingEditor = function() {
    var shareButton = $("#share-button");
    var shareWidget = $("#share-widget");
    var shareWidgetCloseButton = $("#share-widget-close");
    var shareOverlay = $("#share-overlay");

    var onShare = function() {
        shareWidget.show();
        shareWidgetCloseButton.show();
        shareOverlay.height(getOverlayHeight()).show();
    }

    var onShareWidgetClose = function() {
        shareWidget.hide();
        shareWidgetCloseButton.hide();
        shareOverlay.hide();
    }

    this.init = function() {
        shareButton.click(onShare)
        shareWidgetCloseButton.click(onShareWidgetClose)
    }
}