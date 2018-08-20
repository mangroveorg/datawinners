function getOverlayHeight() {
    overlayHeight = $('#container_header_application').outerHeight() + $('#container_content').outerHeight() + 30;
    if(overlayHeight > 970) {
        overlayHeight = overlayHeight + 5;
    } else {
        overlayHeight = 970;
    }
    return overlayHeight;
}

function capitalize(text) {
    if (!text) return text;
    return text.charAt(0).toUpperCase() + text.slice(1);
};