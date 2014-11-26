$.valHooks.textarea = {
    get: function (elem) {
        return elem.value.replace(/\r?\n/g, "\r\n");
    }
};

var month_name_map = {0:'January' ,
                      1: 'February' ,
                      2: 'March' ,
                      3: 'April' ,
                      4: 'May' ,
                      5: 'June' ,
                      6: 'July' ,
                      7: 'August' ,
                      8: 'September' ,
                      9: 'October' ,
                      10:'November' ,
                      11:'December' };

var is_last_day_of_month = function(date){
    var last_day_of_current_month = new Date(date.getTime());
    last_day_of_current_month.setMonth(date.getMonth()+1);
    last_day_of_current_month.setDate(0);
    return date.getDate() == last_day_of_current_month.getDate();
};

var get_last_day_of_next_month = function(date) {
    var last_day_of_next_month = date;
    last_day_of_next_month.setMonth(date.getMonth()+2);
    last_day_of_next_month.setDate(0);
    return last_day_of_next_month;
};

Date.prototype.convert_to_month_name = function () {
    month_number = this.getMonth();
    this.month_name =  month_name_map[month_number];
};

var add_days = function (date, days) {
    return new Date(date.getTime() + days * 24 * 60 * 60 * 1000);
};

var range_of_numbers = function (lowEnd, highEnd) {
    var list = [];
    for (var i = lowEnd; i <= highEnd; i++) {
        list.push(i);
    }
    return list;
};

function ReminderInstance() {
    var self = this;
    self.text = ko.observable('');
    self.number_of_days = ko.observable(2);
    self.enable = ko.observable(false);
    self.multiplier = 0;
    self.next_reminder_date = ko.observable(new Date());
    self.count = ko.computed(function () {
        self.is_modified = true;
        return self.text().length;
    }, this);
    self.is_modified = false;
    self.number_of_days.subscribe(function(){
        self.next_reminder_date(add_days(self.next_reminder_date(), self.multiplier * -1 * self.number_of_days()))
    },self,'beforeChange');

    self.number_of_days.subscribe(function(){
        self.update_example(self.next_reminder_date);
    });

    self.next_date_as_string = ko.computed(function () {
        self.is_modified = true;
        if (self.enable()) {
            var deadline = self.next_reminder_date();
            deadline.convert_to_month_name();
            return gettext("Next scheduled Reminder: ") + deadline.getDate() + " " + deadline.month_name + " " + deadline.getFullYear();
        }
        else return gettext("Next scheduled Reminder: ") + gettext("will not be sent");
    });

    self.update_example = function (next_deadline) {
        self.next_reminder_date(add_days(next_deadline(), self.multiplier * self.number_of_days()));
    };
}

function ReminderSettingsModel() {
    var self = this;
    self.selected_frequency = ko.observable();
    self.select_day = ko.observable();
    self.whom_to_send_message = ko.observable();
    self.select_datasender = ko.observable();
    self.is_reminder_enabled = ko.observable();
    self.isOpen= ko.observable(false);
    self.label = ko.observable();
    self.is_modified = false;
    self.open = function() {
        this.isOpen(true);
    };

    self.is_deadline_date_changed = false;
    self.initialize = function() {
        self.init_reminders();
        self.init_variables();
    };

    self.cancel_changes = function(){
        self.init_variables(self);
        self.reset_reminders(self);
    };

    self.is_reminders_modified = function(){
        return self.reminder_before_deadline.is_modified || self.reminder_after_deadline.is_modified || self.reminder_on_deadline.is_modified;
    };

    self.reset_modified_flag = function(){
        self.reminder_before_deadline.is_modified = false;
        self.reminder_after_deadline.is_modified = false;
        self.reminder_on_deadline.is_modified = false;
        self.is_modified = false;
    };

    self.next_deadline = ko.computed(function () {
        var current_date = new Date();
        var next_deadline = new Date(current_date.getTime());
        if (self.selected_frequency() == 'month') {
            var lastdays_of_feb = [29, 30, 0];
            if (self.select_day() <= current_date.getDate()) {
                if(next_deadline.getMonth() == 0 && lastdays_of_feb.indexOf(self.select_day())!=-1){
                    next_deadline.setMonth(2);
                    next_deadline.setDate(0);
                    return next_deadline;
                }
                next_deadline.setMonth(next_deadline.getMonth() + 1);
            }
            if(next_deadline.getMonth() == 1 && lastdays_of_feb.indexOf(self.select_day())!=-1){
                next_deadline.setMonth(2);
            }
            next_deadline.setDate(self.select_day());
            if(is_last_day_of_month(current_date) && self.select_day()==0){
                next_deadline = get_last_day_of_next_month(current_date);
            }
        }
        else {
            if (self.select_day() % 7 < current_date.getDay()) {
                next_deadline = add_days(current_date, 7 - (current_date.getDay() - (self.select_day() % 7)));
            }
            else {
                next_deadline = add_days(current_date, ((self.select_day() % 7) - current_date.getDay()));
            }
        }
        self.is_modified = true;
        return next_deadline;
    }, this);

    self.next_deadline.subscribe(function () {
        self.reminder_before_deadline.update_example(self.next_deadline);
        self.reminder_on_deadline.update_example(self.next_deadline);
        self.reminder_after_deadline.update_example(self.next_deadline);
        self.is_deadline_date_changed = true;

    });

    self.next_deadline_string = ko.computed(function () {
        self.next_deadline().convert_to_month_name();
        return gettext("Next deadline: ") + self.next_deadline().getDate() + " " + self.next_deadline().month_name + " " + self.next_deadline().getFullYear();
    });

    self.save_reminders = function (callback) {
        var post_data = {
            'should_send_reminders_before_deadline': self.reminder_before_deadline.enable(),
            'should_send_reminders_on_deadline': self.reminder_on_deadline.enable(),
            'should_send_reminders_after_deadline': self.reminder_after_deadline.enable(),
            'selected_frequency': self.selected_frequency(),
            'select_day': self.select_day(),
            'reminder_text_on_deadline': self.reminder_on_deadline.text(),
            'reminder_text_after_deadline': self.reminder_after_deadline.text(),
            'reminder_text_before_deadline': self.reminder_before_deadline.text(),
            'number_of_days_after_deadline': self.reminder_after_deadline.number_of_days(),
            'number_of_days_before_deadline': self.reminder_before_deadline.number_of_days(),
            'has_deadline': reminder_data['has_deadline'],
            'whom_to_send_message': self.whom_to_send_message(),
            'csrfmiddlewaretoken': $('#reminder_deadline_form input[name=csrfmiddlewaretoken]').val()
        };
        self.track_selection({valueAccessor: self.whom_to_send_message, checked_action: 'remind-all-registered-datasenders', unchecked_action: 'remind-not-submitted-datasenders'});
        self.track_deadline_selection({ valueAccessor: self.reminder_before_deadline, checked_action: 'reminder-before-deadline-selected', unchecked_action: 'reminder-before-deadline-not-selected', days: "#id_number_of_days_before_deadline"});
        self.track_deadline_selection({ valueAccessor: self.reminder_on_deadline, checked_action: 'reminder-on-deadline-selected', unchecked_action: 'reminder-on-deadline-not-selected'});
        self.track_deadline_selection({ valueAccessor: self.reminder_after_deadline, checked_action: 'reminder-after-deadline-selected', unchecked_action: 'reminder-after-deadline-not-selected', days: "#number_of_days_after_deadline"});

        if(self.is_deadline_date_changed){
            DW.trackEvent('reminders', 'deadline-changed');
        }
        DW.trackEvent('reminders', 'saved-reminders');
        DW.loading();
        $.post(post_url, post_data).done(function (response) {
            var responseJson = $.parseJSON(response);
            if (responseJson.success) {
                $('.success-message-box').html(responseJson.success_message);
                $('.success-message-box').show();
                $(document).scrollTop(0);
                if (typeof callback == "function") callback();
                        }
        });
    };

    self.init_variables = function () {
        self.selected_frequency(reminder_data['frequency_period']);
        self.select_day(reminder_data['select_day']);
        self.select_datasender(reminder_data['whom_to_send_message'] ? 'my_datasender' : 'all_my_datasender');
        self.is_reminder_enabled(is_reminder_enabled);
    };

    self.init_reminders = function(){
        self.reminder_before_deadline = new ReminderInstance();
        self.reminder_after_deadline = new ReminderInstance();
        self.reminder_on_deadline = new ReminderInstance();
        self.reset_reminders();
        self.reset_modified_flag();
    };

    self.reset_reminders = function(){
        self.reminder_before_deadline.text(reminder_data['reminder_text_before_deadline']);
        self.reminder_after_deadline.text(reminder_data['reminder_text_after_deadline']);
        self.reminder_on_deadline.text(reminder_data['reminder_text_on_deadline']);
        self.reminder_before_deadline.number_of_days(reminder_data['number_of_days_before_deadline']);
        self.reminder_after_deadline.number_of_days(reminder_data['number_of_days_after_deadline']);
        self.reminder_before_deadline.enable(reminder_information['should_send_reminders_before_deadline']);
        self.reminder_after_deadline.enable(reminder_information['should_send_reminders_after_deadline']);
        self.reminder_on_deadline.enable(reminder_information['should_send_reminders_on_deadline']);
        self.reminder_before_deadline.multiplier = -1;
        self.reminder_after_deadline.multiplier = 1;
    };

    self.track_selection = function (options) {
        if ($(options.valueAccessor())) {
            DW.trackEvent('reminders', options.checked_action);
        }
        else {
            DW.trackEvent('reminders', options.unchecked_action);
        }
    };

    self.track_deadline_selection = function(options) {
        var selector = options.valueAccessor;
        var number_of_days = selector.number_of_days();
        var text_message = selector.text();
        var label = number_of_days + ":" + text_message;

        if(selector.enable()){
            DW.trackEvent('reminders', options.checked_action, label);
        }
        else{
            DW.trackEvent('reminders', options.unchecked_action, label);
        }
    };

    self.option_list = ko.computed(function () {
        return self.selected_frequency() == 'month' ? range_of_numbers(1, 7) : range_of_numbers(1, 3);
    }, this);

    self.dialogContentHtml = ko.computed(function(){
        return self.selected_frequency() == 'month'?$('#learn_more_for_month').html():$('#learn_more_for_week').html();
    },this);


    self.whom_to_send_message = ko.computed(function () {
        self.is_modified = true;
        return self.select_datasender() == 'my_datasender';
    });

    self.select_option = ko.computed(function () {
        return self.selected_frequency() == 'month' ? range_of_numbers(1, 30).concat([0]) : range_of_numbers(1, 7);
    }, this);

    self.display_text = function (item) {
        var item_map_week = {};
        item_map_week[1] = 'Monday';
        item_map_week[2] = 'Tuesday';
        item_map_week[3] = 'Wednesday';
        item_map_week[4] = 'Thursday';
        item_map_week[5] = 'Friday';
        item_map_week[6] = 'Saturday';
        item_map_week[7] = 'Sunday';
        var item_map_month = {};
        item_map_month[1] = "1st";
        item_map_month[2] = "2nd";
        item_map_month[3] = "3rd";
        item_map_month[0] = "Last Day";
        if (self.selected_frequency() == 'month') {
            if(item<=3 || item == 31){
                return item_map_month[item];
            }
            else{
                return item.toString() + 'th';
            }

        }
        else {
               return item_map_week[item];
        }
    };
}

ko.bindingHandlers.disableChildren = {
    update: function (element, valueAccessor) {
        var isDisabled = ko.unwrap(valueAccessor());
        var ele = $(element);
        if (isDisabled) {
            ele.find('*').attr('disabled', 'disabled');
        }
        else {
            ele.find('*').removeAttr('disabled');
        }
    }

};

$(document).ready(function() {
    var deadline_changed = false;
    var viewModel = new ReminderSettingsModel();
    viewModel.initialize();
    var options = {
        successCallBack:function(callback){
            viewModel.save_reminders(callback);
        },
        isQuestionnaireModified : function(){
            return viewModel.is_modified || viewModel.is_reminders_modified();
        },
        cancelDialogDiv : "#cancel_reminder_changes",
        validate: function(){
            return true;
        }
    };
    new DW.CancelWarningDialog(options).init().initializeLinkBindings();
    ko.applyBindings(viewModel, $("#reminder_deadline_form")[0]);
    $('.success-message-box').hide();
});