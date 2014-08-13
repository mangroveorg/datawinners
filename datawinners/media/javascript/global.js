// DW is the global name space on which all the function/methods will be attached through out the site
// This is to avoid introducing global functions/methods/variables in each page
// which could pollute the global namespace and make path for conflicting between the variable/function/method names, which would make debugging tough.
var DW = {};

$.ajaxSetup ({
    // Disable caching of AJAX responses
    cache: false
});

//Google analytics event tracking
DW.trackEvent = function(category, action){
    if (typeof _gaq !== 'undefined') {
        _gaq.push(['_trackEvent', category, action]);
    }
};


$(document).ready(function() {

    DW.flash_message = function() {
        $('.success-message-box').delay(10000).fadeOut();
    };

    DW.set_focus_on_flash_message = function(){
        if ($(".errorlist:has(li)").length == 0){
            $("#flash-message").attr("tabindex", -1).focus();
        }
    }
    var shoudlShowAjaxError = ($('#debug').val()=="True");
    if(shoudlShowAjaxError){
        $("#global_error").ajaxError(function(event, request, settings) {
            $("#global_error").addClass("message-box");
            $("#global_error").html("<p>Error requesting page " + settings.url + "</p>");
        });
    }

    $("#global_error").ajaxSuccess(function() {
        DW.flash_message();
    });

    $.addwatermarks();
    DW.ToolTip();
    DW.flash_message();

    function move_focus_to_first_error_field(){
        var first_error_field = $(".errorlist:has(li)").eq(0).prev();
        if (first_error_field.is("ul, span")){
            first_error_field = $("input, select", first_error_field).eq(0);
        }
        first_error_field.focus();
    }

    $("body").ajaxComplete(move_focus_to_first_error_field);
    move_focus_to_first_error_field();
});


RegExp.escape= function(s) {
    return s.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')
};

if(typeof String.prototype.trim !== 'function') {
  String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g, '');
  }
}

// Add ECMA262-5 Array methods if not supported natively
//
if (!('indexOf' in Array.prototype)) {
    Array.prototype.indexOf= function(find, i /*opt*/) {
        if (i===undefined) i= 0;
        if (i<0) i+= this.length;
        if (i<0) i= 0;
        for (var n= this.length; i<n; i++)
            if (i in this && this[i]===find)
                return i;
        return -1;
    };
}

$.fn.addBack = function (selector) {
    return this.add(selector == null ? this.prevObject : this.prevObject.filter(selector));
};
