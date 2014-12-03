$.valHooks.textarea = {
    get: function (elem) {
        return elem.value.replace(/\r?\n/g, "\r\n");
    }
};

var month_name_map = {0:gettext('January') ,
                      1: gettext('February') ,
                      2: gettext('March') ,
                      3: gettext('April') ,
                      4: gettext('May') ,
                      5: gettext('June') ,
                      6: gettext('July') ,
                      7: gettext('August') ,
                      8: gettext('September'),
                      9: gettext('October') ,
                      10:gettext('November') ,
                      11:gettext('December') };

var item_map_week = {
        1: gettext('Monday'),
        2: gettext('Tuesday'),
        3: gettext('Wednesday'),
        4: gettext('Thursday'),
        5: gettext('Friday'),
        6: gettext('Saturday'),
        0: gettext('Sunday')
};

var is_last_day_of_month = function(date){
    var last_day_of_current_month = new Date(date.getTime());
    last_day_of_current_month.setMonth(date.getMonth()+1);
    last_day_of_current_month.setDate(0);
    return date.getDate() == last_day_of_current_month.getDate();
};

var get_last_day_of_next_month = function(date) {
    var last_day_of_next_month = new Date(date.getTime());
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
    self.next_reminder_date = new MonthlyReminder();
    self.is_modified = ko.observable(false);
    self.next_deadline_date = new Date();
    self.is_valid = ko.computed(function(){
        return !(self.enable() && self.text().length <= 0)
    });
    self.count = ko.computed(function () {
        self.is_modified(true);
        return self.text().length;
    }, this);

    self.number_of_days.subscribe(function(){
        self.next_reminder_date.reminder_date = self.next_deadline_date;
        self.update_example(self.next_reminder_date);
    });

    self.next_date_as_string = ko.computed(function () {
        self.is_modified(true);
        if (self.enable()) {
            return gettext("Next scheduled Reminder: ") + self.next_reminder_date.get_display_string();
        }
        else return gettext("Next scheduled Reminder: ") + gettext("will not be sent");
    });

    self.update_example = function (next_deadline) {
        self.next_deadline_date = next_deadline.reminder_date;
        var next_reminder_date = next_deadline.get_new_instance();
        next_reminder_date.update_date(next_deadline.reminder_date, self.multiplier,self.number_of_days());
        self.next_reminder_date = next_reminder_date;
        self.enable.valueHasMutated();
    };
}

function MonthlyReminder(){
    var self = this;
    self.reminder_date = new Date();
    self.calculate_deadline = function(selected_day){
        var current_date = new Date();
        var next_deadline = new Date();
        var lastdays_of_feb = [29, 30];
        if (selected_day <= current_date.getDate()) {
            next_deadline.setMonth(next_deadline.getMonth() + 1);
        }
        if(next_deadline.getMonth() == 1 && lastdays_of_feb.indexOf(selected_day)!=-1){
            next_deadline.setMonth(2);
            next_deadline.setDate(0);
            self.reminder_date = next_deadline;
            return;
        }
        next_deadline.setDate(selected_day);
        if(is_last_day_of_month(current_date) && selected_day==0){
            next_deadline = get_last_day_of_next_month(current_date);
        }
        self.reminder_date = next_deadline;
    };
    self.get_display_string = function(){
        var next_deadline = new Date (self.reminder_date.getTime());
//        var current_date = new Date();
//        if (next_deadline.getDate() <= current_date.getDate()) {
//            next_deadline.setMonth(next_deadline.getMonth() + 1);
//        }
        next_deadline.convert_to_month_name();
        return next_deadline.getDate() + " " + next_deadline.month_name + " " + next_deadline.getFullYear();
    };
    self.get_new_instance = function(){
        return new MonthlyReminder();
    };
    self.update_date = function (next_deadline_date, multiplier, number_of_days) {
        var next_date = add_days(next_deadline_date, multiplier * number_of_days);
        var current_date = new Date();
        if (next_date <= current_date) {
            var next_month_date = new Date(next_deadline_date.getTime());
            next_month_date.setMonth(self.reminder_date.getMonth() + 1);
            self.update_date(next_month_date, multiplier, number_of_days)
        }
        else {
            self.reminder_date = next_date;
        }
    };
}

function WeeklyReminder(){
    var self = this;
    self.reminder_date = new Date();
    self.calculate_deadline = function(selected_day){
        var current_date = new Date();
        var next_deadline = new Date();
        if (selected_day % 7 <= current_date.getDay()) {
            next_deadline = add_days(current_date, 7 - (current_date.getDay() - (selected_day % 7)));
        }
        else {
            next_deadline = add_days(current_date, ((selected_day % 7) - current_date.getDay()));
        }
        self.reminder_date = next_deadline;
    };
    self.get_display_string = function(){
        var next_deadline = self.reminder_date;
        next_deadline.convert_to_month_name();
        return item_map_week[next_deadline.getDay()]+", "+ next_deadline.getDate() + " " + next_deadline.month_name + " " + next_deadline.getFullYear();
    };
    self.get_new_instance = function(){
        return new WeeklyReminder();
    };
    self.update_date = function (next_deadline_date, multiplier, number_of_days) {
        var next_date = add_days(next_deadline_date, multiplier * number_of_days);
        var current_date = new Date();
        if (next_date <= current_date) {
            var next_week_date = add_days(next_deadline_date, 7);
            self.update_date(next_week_date, multiplier, number_of_days)
        }
        else self.reminder_date = next_date;
    };

    self.shift_to_next_deadline = function(){
        var current_date = new Date();
        if(self.reminder_date <= current_date) self.reminder_date = add_days(self.reminder_date, 7);
    }
}

function ReminderSettingsModel() {
    var self = this;
    self.selected_frequency = ko.observable();
    self.select_day = ko.observable();
    self.whom_to_send_message = ko.observable();
    self.select_datasender = ko.observable();
    self.is_reminder_disabled = ko.observable();
    self.isOpen= ko.observable(false);
    self.label = ko.observable();
    self.next_deadline_string = ko.observable();
    self.is_modified = ko.observable(false);
    self.reminder_before_deadline = new ReminderInstance();
    self.reminder_after_deadline = new ReminderInstance();
    self.reminder_on_deadline = new ReminderInstance();
    self.open = function() {
        self.isOpen(true);
    };

    self.is_deadline_date_changed = false;
    self.initialize = function() {
        self.init_reminders();
        self.init_variables();
    };

    self.cancel_changes = function(){
        self.init_variables();
        self.reset_reminders();
        self.reset_modified_flags();
    };

    self.reset_modified_flags = function(){
        self.reminder_before_deadline.is_modified(false);
        self.reminder_after_deadline.is_modified(false);
        self.reminder_on_deadline.is_modified(false);
        self.is_modified(false);
    };

    self.is_reminders_modified = ko.computed(function(){
        return self.reminder_before_deadline.is_modified() || self.reminder_after_deadline.is_modified() || self.reminder_on_deadline.is_modified();
    });

    self.next_deadline_date = ko.computed(function(){
        return self.selected_frequency() == 'month'? new MonthlyReminder():new WeeklyReminder();
    }).extend({ throttle: 20 });

    self.update_example = function(){
        self.next_deadline_date().calculate_deadline(self.select_day());
        self.next_deadline_string(gettext("Next deadline: ") + self.next_deadline_date().get_display_string());
        self.reminder_before_deadline.update_example(self.next_deadline_date());
        self.reminder_on_deadline.update_example(self.next_deadline_date());
        self.reminder_after_deadline.update_example(self.next_deadline_date());
        self.is_modified(true);
        self.is_deadline_date_changed = true;
    };
    self.select_day.subscribe(function () {
        self.update_example();
    }, this);

    self.next_deadline_date.subscribe(function () {
        self.update_example();
    }, this);

    self.save_reminders = function (callback) {
        if (!(self.reminder_before_deadline.is_valid() && self.reminder_on_deadline.is_valid() && self.reminder_after_deadline.is_valid())) return;
        var post_data = {
            'should_send_reminders_before_deadline': self.reminder_before_deadline.enable(),
            'should_send_reminders_on_deadline': self.reminder_on_deadline.enable(),
            'should_send_reminders_after_deadline': self.reminder_after_deadline.enable(),
            'frequency_period': self.selected_frequency(),
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
                self.reset_initial_data();
                self.reset_modified_flags();
                if (typeof callback == "function") callback();
                }
        });
    };

    self.init_variables = function () {
        self.selected_frequency(reminder_data['frequency_period']);
        self.select_day(reminder_data['select_day']);
        self.select_datasender(reminder_data['whom_to_send_message'] ? 'my_datasender' : 'all_my_datasender');
        self.is_reminder_disabled(is_reminder_disabled);
    };

    self.init_reminders = function(){
        self.reset_reminders();
        self.reset_modified_flags();
    };

    self.reset_initial_data = function(){
        reminder_data['reminder_text_before_deadline'] = self.reminder_before_deadline.text();
        reminder_data['reminder_text_after_deadline'] = self.reminder_after_deadline.text();
        reminder_data['reminder_text_on_deadline'] = self.reminder_on_deadline.text();
        reminder_data['number_of_days_before_deadline'] = self.reminder_before_deadline.number_of_days();
        reminder_data['number_of_days_after_deadline'] = self.reminder_after_deadline.number_of_days();
        reminder_data['should_send_reminders_before_deadline'] = self.reminder_before_deadline.enable();
        reminder_data['should_send_reminders_after_deadline'] = self.reminder_after_deadline.enable();
        reminder_data['should_send_reminders_on_deadline'] = self.reminder_on_deadline.enable();
        reminder_data['frequency_period'] = self.selected_frequency();
        reminder_data['select_day'] = self.select_day();
        reminder_data['whom_to_send_message'] = self.whom_to_send_message();
    };

    self.reset_reminders = function(){
        self.reminder_before_deadline.text(reminder_data['reminder_text_before_deadline']);
        self.reminder_after_deadline.text(reminder_data['reminder_text_after_deadline']);
        self.reminder_on_deadline.text(reminder_data['reminder_text_on_deadline']);
        self.reminder_before_deadline.number_of_days(reminder_data['number_of_days_before_deadline']);
        self.reminder_after_deadline.number_of_days(reminder_data['number_of_days_after_deadline']);
        self.reminder_before_deadline.enable(reminder_data['should_send_reminders_before_deadline']);
        self.reminder_after_deadline.enable(reminder_data['should_send_reminders_after_deadline']);
        self.reminder_on_deadline.enable(reminder_data['should_send_reminders_on_deadline']);
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
        self.is_modified(true);
        return self.select_datasender() == 'my_datasender';
    });

    self.select_option = ko.computed(function () {
        return self.selected_frequency() == 'month' ? range_of_numbers(1, 30).concat([0]) : range_of_numbers(1, 7);
    }, this);

    self.should_not_save = ko.computed(function(){
        return self.is_reminder_disabled() || !(self.is_modified() || self.is_reminders_modified());
    });

    self.display_text = function (item) {
        var item_map_month = {};
        item_map_month[1] = "1" + gettext('st');
        item_map_month[2] = "2" + gettext('nd');
        item_map_month[3] = "3" + gettext('rd');
        item_map_month[0] = gettext("Last Day");
        if (self.selected_frequency() == 'month') {
            if(item<=3 || item == 31){
                return item_map_month[item];
            }
            else{
                return item.toString() + gettext('th');
            }

        }
        else {
               return item_map_week[item%7];
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
    vm = viewModel
    var options = {
        successCallBack:function(callback){
            viewModel.save_reminders(callback);
        },
        isQuestionnaireModified : function(){
            return viewModel.is_modified() || viewModel.is_reminders_modified();
        },
        cancelDialogDiv : "#cancel_reminder_changes",
        validate: function(){
            return true;
        }
    };
    new DW.CancelWarningDialog(options).init().initializeLinkBindings();
    ko.applyBindings(viewModel, $("#reminder_deadline_form")[0]);
    $('.success-message-box').hide();
    viewModel.reset_modified_flags();
});