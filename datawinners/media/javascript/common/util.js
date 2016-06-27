function getOverlayHeight() {
    overlayHeight = $('#container_header_application').outerHeight() + $('#container_content').outerHeight() + 30;
    if(overlayHeight > 970) {
        overlayHeight = overlayHeight + 5;
    } else {
        overlayHeight = 970;
    }
    return overlayHeight;
}