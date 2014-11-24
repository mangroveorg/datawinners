$.valHooks.textarea = {
    get: function (elem) {
        return elem.value.replace(/\r?\n/g, "\r\n");
    }
};

Date.prototype.convert_to_month_name = function () {
    switch (this.getMonth()) {
        case 0:
            this.month_name = "January";
            break;
        case 1:
            this.month_name = "February";
            break;
        case 2:
            this.month_name = "March";
            break;
        case 3:
            this.month_name = "April";
            break;
        case 4:
            this.month_name = "May";
            break;
        case 5:
            this.month_name = "June";
            break;
        case 6:
            this.month_name = "July";
            break;
        case 7:
            this.month_name = "August";
            break;
        case 8:
            this.month_name = "September";
            break;
        case 9:
            this.month_name = "October";
            break;
        case 10:
            this.month_name = "November";
            break;
        case 11:
            this.month_name = "December";
            break;
    }
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
        var next_deadline = new Date();
        if (self.selected_frequency() == 'month') {
            if (self.select_day() < current_date.getDate()) {
                next_deadline.setMonth(next_deadline.getMonth() + 1);
            }
            next_deadline.setDate(self.select_day());
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

    self.save_reminders = function () {
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

        $.post(post_url, post_data).done(function (response) {
            var responseJson = $.parseJSON(response);
            if (responseJson.success) {
                $('.success-message-box').removeClass('none');
                $('.success-message-box').html(responseJson.success_message);
                $(document).scrollTop(0);
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
        return self.selected_frequency() == 'month' ? range_of_numbers(1, 30) : range_of_numbers(1, 7);
    }, this);

    self.display_text = function (item) {
        if (self.selected_frequency() == 'month') {
            switch (item) {
                case 1:
                    return "1st";
                    break;
                case 2:
                    return "2nd";
                    break;
                case 3:
                    return "3rd";
                    break;
                default:
                    return item.toString() + 'th';
                    break;
            }
        }
        else {
            switch (item) {
                case 1:
                    return "Monday";
                    break;
                case 2:
                    return "Tuesday";
                    break;
                case 3:
                    return "Wednesday";
                    break;
                case 4:
                    return "Thursday";
                    break;
                case 5:
                    return "Friday";
                    break;
                case 6:
                    return "Saturday";
                    break;
                case 7:
                    return "Sunday";
                    break;
            }
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
});