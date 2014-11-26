
function track_deadline_selection(options) {
    var selector = $(options.selector);
    var number_of_days = options.days ? $(options.days).val() : "";
    var text_message = $(options.message).val();
    var label = options.days ? number_of_days + ":" + text_message : text_message;

    if(selector.attr("checked")){
        DW.trackEvent('reminders', options.checked_action, label);
    }
    else{
        DW.trackEvent('reminders', options.unchecked_action, label);
    }
    }
