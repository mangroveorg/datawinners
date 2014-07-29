//All the deadline related drop-downs. They are very very very annoying.
DW.DeadlineDetails = function(){
    this.deadlineSectionSelectControls = '#frequency_values select';
    this.deadlineEnabledControl = 'input[name=has_deadline]';
    this.deadlineEnabledCheckedControl = 'input[name=has_deadline]:checked';
    this.frequencyPeriodControl = 'select[name=frequency_period]';
    this.deadlineTypeControl = 'select[name=deadline_type]'; //For the control which lets user select Same and Following. I wish i had a better name for this one.
    this.deadlineMonthControl = 'select[name=deadline_month]';
    this.deadlineWeekControl = 'select[name=deadline_week]';
    this.month_block_class = '.month_block';
    this.week_block_class = '.week_block';
    this.reminders_block_id = '#reminders_section';
    this.deadline_example = '#deadline_example';
    this.deadline_types = 'select.deadline_type';
    this.deadline_type_month = '#id_deadline_type_month';
    this.deadline_type_week = '#id_deadline_type_week';
};

DW.DeadlineDetails.prototype = {
    init: function() {
        $(this.deadline_types).attr('name', 'deadline_type');
        $(this.deadline_types).attr('disabled', 'disabled');
        this.is_reminder_enabled = DW.is_reminder_enabled;
        if (this.is_reminder_enabled)
            this.hide();
        this.show();
        this.update_example();
        return true; //It's a Best Practice to return either true or false when there are only side effects happening inside a method.
    },
    hide: function(){
        this.toggle_week_and_month_controls();
        $(this.deadlineSectionSelectControls).each(function(){
            $(this).attr('disabled', 'disabled');
        });
        $(this.reminders_block_id).hide();
    },
    show: function(){
        $(this.deadlineSectionSelectControls).each(function(){
            if (this.is_reminder_enabled)
                $(this).removeAttr('disabled');
        });
        this.toggle_week_and_month_controls();
        $(this.reminders_block_id).show();
    },
    toggle_week_and_month_controls: function(){
        var is_week = ($(this.frequencyPeriodControl).val() === "week");
        if(is_week){
            this.toggle_when_week_is_selected();
        }else{
            this.toggle_when_month_is_selected();
        }
    },
    toggle_when_month_is_selected: function(){
        $(this.month_block_class).show();
        $(this.week_block_class).hide();
        if (!this.is_reminder_enabled)
            $(this.deadline_type_month).removeAttr('disabled');
        $(this.deadline_type_week).attr('disabled', 'disabled');
    },
    toggle_when_week_is_selected: function(){
        $(this.week_block_class).show();
        $(this.month_block_class).hide();
        if (!this.is_reminder_enabled)
            $(this.deadline_type_week).removeAttr('disabled');
        $(this.deadline_type_month).attr('disabled', 'disabled');
    },
    update_example: function(){
        var deadline_example = "";
        var frequency = $(this.frequencyPeriodControl).val();

        if (frequency == 'week') {
            var deadline_type_value = $(this.deadline_type_week).val();
            var selected_weekday_text = $(this.deadlineWeekControl+" :selected").text();
            if (deadline_type_value == 'Following') {
                deadline_example = interpolate(gettext("Example: %(day)s of the week following the reporting week"), { day : selected_weekday_text}, true);
            } else {
                deadline_example = interpolate(gettext("Example: %(day)s of the reporting week"), { day : selected_weekday_text }, true);
            }
        } else if (frequency == 'month') {
            var deadline_type_value = $(this.deadline_type_month).val();
            var selected_month_day_text = $(this.deadlineMonthControl+" :selected").text();
            if (deadline_type_value == 'Following') {
                deadline_example = interpolate(gettext("Example: %(day)s of October for September report"), { day : selected_month_day_text }, true);
            } else {
                deadline_example = interpolate(gettext("Example: %(day)s of October for October report"), { day : selected_month_day_text }, true);
            }
        }
        $(this.deadline_example).html(deadline_example);

    }
};

DW.ReminderDetails = function(){
    this.number_of_days_before_deadline = 'input[name=number_of_days_before_deadline]';
    this.number_of_days_after_deadline = 'input[name=number_of_days_after_deadline]';
};

DW.ReminderDetails.prototype = {
    init: function(){
        $(this.number_of_days_before_deadline).attr('maxlength', '3');
        $(this.number_of_days_after_deadline).attr('maxlength', '3');
        return true;
    }
};

var deadlineDetails = new DW.DeadlineDetails;
var reminderDetails = new DW.ReminderDetails;
$(document).ready(function() {
    deadlineDetails.init();
    reminderDetails.init();
    $(deadlineDetails.frequencyPeriodControl).change(function(){
        deadlineDetails.show();
        deadlineDetails.update_example();
    });
    $(deadlineDetails.deadlineWeekControl).change(function(){
        deadlineDetails.update_example();
    });
    $(deadlineDetails.deadlineMonthControl).change(function(){
        deadlineDetails.update_example();
    });
    $(deadlineDetails.deadline_types).change(function(){
        deadlineDetails.update_example();
    });
});

sms_text_counter = function(kwargs) {
    var defaults = {
        reminder_type: "on"
    }
    this.options = $.extend(true, defaults, kwargs);
    this.sms_max_length = 160;
    this._init();
}

sms_text_counter.prototype = {
    _init: function() {
        var opts = this.options;
        this.reminder_type = opts.reminder_type;
        this.sms_counter_container_id = "#counter_for_reminder_" + this.reminder_type + "_deadline";
        this.sms_textarea_id = "#id_reminder_text_" + this.reminder_type + "_deadline";
        this.bind_keyup_event = function(){
            var cls = this;
            $(this.sms_textarea_id).keyup(function(){
                cls.update_counter_value();
            })
        };
        this.update_counter_value = function() {
            if (this.sms_max_length < this.get_sms_length()) {
                $(this.sms_textarea_id).val(this.get_sms_text().substring(0, this.sms_max_length));
            }

            $(this.sms_counter_container_id).html($(this.sms_textarea_id).val().length);
        };
        this.get_sms_text = function () {
            return $(this.sms_textarea_id).val();
        }
        this.get_sms_length = function () {
            return this.get_sms_text().length;
        }
        this.init = function () {
            this.bind_keyup_event();
            this.update_counter_value();
        }
        this.init();
    }
}

$(document).ready(function() {
    new sms_text_counter({'reminder_type': 'before'});
    new sms_text_counter({'reminder_type': 'on'});
    new sms_text_counter({'reminder_type': 'after'});
})