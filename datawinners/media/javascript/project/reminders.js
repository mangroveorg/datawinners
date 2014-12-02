$(document).ready(function() {
    var project_id = $('#project_id').html();

    function reminder(projectName, message, beforeDay, afterDay, reminderMode, ownerViewModel, targetDataSenders) {
        this.projectName = projectName;
        this.beforeDay = ko.observable(beforeDay);
        this.afterDay = ko.observable(afterDay);
        this.reminderMode = ko.observable(reminderMode);
        this.targetDataSenders = ko.observable(targetDataSenders);
        this.remove = function() {
            ownerViewModel.reminders.remove(this);
        };
        this.defaultMessage = function() {
            return gettext("Hello. We have not received your data for ") + this.projectName + gettext(".Please send it to us today. Thank you.");
        };

        if (message == null){
          message = this.defaultMessage();
        }
        this.message = ko.observable(message);
        var self = this;
        this.header = ko.dependentObservable(function() {
            if (self.reminderMode() === "before_deadline") {
                return self.beforeDay() + gettext(" day(s) before deadline");
            } else if (self.reminderMode() === "after_deadline") {
                return self.afterDay() + gettext(" day(s) after deadline");
            } else {
                return gettext("On the deadline");
            }
        }, this);
        this.selectBeforeDay = ko.dependentObservable(function() {
            if (self.reminderMode() === "before_deadline") {
                return true;
            }
            self.beforeDay("");
            return false;
        }, this);
        this.selectAfterDay = ko.dependentObservable(function() {
            if (self.reminderMode() === "after_deadline") {
                return true;
            }
            self.afterDay("");
            return false;
        }, this);
    }

    function viewModel() {
        this.reminders = ko.observableArray([]);
        this.remindersToSave = [];
        this.addReminder = function() {
            if($("#reminder_form").valid()){
                this.reminders.push(new reminder($("#project_name").text(), null, "", "", "on_deadline", this, 'all_datasenders'));
                $("#review_section").accordion("destroy").accordion({header:'.header',collapsible: true});
                if (this.reminders().length > 1) {
                    $("#review_section").accordion("activate", this.reminders().length - 1);
                }
            }
        };
        this.save = function() {
            this.remindersToSave = [];
            var i=0;
            for (i; i < this.reminders().length; i = i+1) {
                var newReminder = {};
                newReminder['targetDataSenders'] = this.reminders()[i].targetDataSenders();
                newReminder['message'] = this.reminders()[i].message();
                if (this.reminders()[i].reminderMode() == 'before_deadline') {
                    newReminder['reminderMode'] = 'before_deadline';
                    newReminder['day'] = this.reminders()[i].beforeDay();
                }
                if (this.reminders()[i].reminderMode() == 'after_deadline') {
                    newReminder['reminderMode'] = 'after_deadline';
                    newReminder['day'] = this.reminders()[i].afterDay();
                }
                if (this.reminders()[i].reminderMode() == "on_deadline") {
                    newReminder['reminderMode'] = 'on_deadline';
                    newReminder['day'] = 0;
                }
                this.remindersToSave.push(newReminder);
            }
            $.post('/project/reminders/' + project_id + "/", {'reminders':ko.toJSON(this.remindersToSave)}, function() {
                $('.success-message-box').show().html(gettext('The reminders has been saved')).fadeOut(10000);
            });
        };

        var self = this;
        $.getJSON("/project/reminders/" + project_id + "/", function(data) {
            var mappedReminders = $.map(data, function(item) {
                var beforeDay = "";
                var afterDay = "";
                if (item.reminder_mode === "before_deadline") {
                    beforeDay = item.day;
                } else {
                    afterDay = item.day;
                }
                return new reminder($("#project_name").text(), item.message, beforeDay, afterDay, item.reminder_mode, self, item.remind_to);
            });
            self.reminders(mappedReminders);
            $("#review_section").accordion({header:'.header',collapsible: true});
            $('#review_section').accordion("activate", -1);
        });
    }

    var viewmodel = new viewModel();
    ko.applyBindings(viewmodel);

    // calls viewmodel.save only on jquery validate success.
    $("#reminder_form").validate({
        submitHandler: function () {
            viewmodel.save();
        }
    });

});

