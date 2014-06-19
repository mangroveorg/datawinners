var IEDetector = {
    getInternetExplorerVersion: function() {
        var rv = -1; // Return value assumes failure.
        if (navigator.appName == 'Microsoft Internet Explorer') {
            var ua = navigator.userAgent;
            var re = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");
            if (re.exec(ua) != null)
                rv = parseFloat(RegExp.$1);
        }
        return rv;
    }
};

$(function(){
    var ver = IEDetector.getInternetExplorerVersion();
    if (ver == 8){
        var messageBox = $("#ie8-warning");
        messageBox.removeClass("none");
        $("#close-ie-msg").on('click', function(){
            messageBox.remove();
        });
    }
});