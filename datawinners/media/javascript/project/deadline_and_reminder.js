function track_selection(options) {
     if($(options.selector).attr("checked")){
        DW.trackEvent('reminders', options.checked_action);
     }
     else{
        DW.trackEvent('reminders', options.unchecked_action);
     }
}

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

var model;
$(document).ready(function() {

    var deadline_changed = false;
    var viewModel = new ReminderSettingsModel();

    ko.applyBindings(viewModel, $("#reminder_deadline_form")[0]);
    model = viewModel;
    $("#reminder_deadline_form").on('change', "#id_frequency_period, #id_deadline_month, #id_deadline_type_month", function(){
        if(!deadline_changed){
            deadline_changed = true;
        }
    });

    $("#submit-button").on('click', function(){

        track_selection({selector: "#id_whom_to_send_message", checked_action: 'remind-all-registered-datasenders', unchecked_action: 'remind-not-submitted-datasenders'});
        track_deadline_selection({ selector: "#id_should_send_reminders_before_deadline", checked_action: 'reminder-before-deadline-selected', unchecked_action: 'reminder-before-deadline-not-selected', days: "#id_number_of_days_before_deadline"});
        track_deadline_selection({ selector: "#id_should_send_reminders_on_deadline", checked_action: 'reminder-on-deadline-selected', unchecked_action: 'reminder-on-deadline-not-selected'});
        track_deadline_selection({ selector: "#id_should_send_reminders_after_deadline", checked_action: 'reminder-after-deadline-selected', unchecked_action: 'reminder-after-deadline-not-selected', days: "#number_of_days_after_deadline"});
        if(deadline_changed){
            DW.trackEvent('reminders', 'deadline-changed');
        }

        DW.trackEvent('reminders', 'saved-reminders');
        return true;
    });

});