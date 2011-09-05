$(document).ready(function(){
    var project_id = $('#project_id').html();
    $('.choice').change(function(){
        var is_reminder = $("input[@name='rdio']:checked").val();
        var url = '/project/reminderstatus/' + project_id+"/";
        $.post(url, {'is_reminder': is_reminder}, function(data){
            var message = "Reminders has been activated for the project"
            if(is_reminder === "False"){
                message = "Reminders has been de-activated for the project"
                $('.add_reminder').addClass('none');
            }else{
                $('.add_reminder').removeClass('none');
            }
            $('.success_message').show().html(message).fadeOut(10000);
        });
    });

function reminder(message, beforeDay, afterDay, reminderMode, ownerViewModel) {
    this.message = ko.observable(message);
    this.beforeDay = ko.observable(beforeDay);
    this.afterDay = ko.observable(afterDay);
    this.reminderMode = ko.observable(reminderMode);
    this.remove = function() {
        ownerViewModel.reminders.remove(this);
    }
    var self = this;
    this.header = ko.dependentObservable(function(){
        if(self.reminderMode === "before_deadline"){
            return self.beforeDay + " days before deadline";
        }else if(self.reminderMode === "after_deadline"){
            return self.afterDay + " days after deadline";
        }else{
            return "";
        }
    }, this);
}

function viewModel() {
    this.reminders = ko.observableArray([]);
    this.remindersToSave = [];
    this.addReminder = function() {
        this.reminders.push(new reminder("", "", "", "before_deadline", this));
    }
    this.save = function() {
        var shouldSave = true;
        for(var i = 0; i < this.reminders().length; i++){
            var newReminder = {};
            if (this.reminders()[i].message() === "") {
                $('#newMessage_err').show().html("Can't be blank.");
                shouldSave = false
            } else {
                newReminder['message'] = this.reminders()[i].message();
            }
            if (this.reminders()[i].reminderMode() == 'before_deadline') {
                if (this.reminders()[i].beforeDay() === "") {
                    $('#newDay_err').show().html("Day Can't be blank.")
                    shouldSave = false;
                } else {
                    newReminder['reminderMode'] = 'before_deadline';
                    newReminder['day'] = this.reminders()[i].beforeDay();
                }
            }
            if (this.reminders()[i].reminderMode() == 'after_deadline') {
                if (this.reminders()[i].afterDay() === "") {
                    $('#newDay_err').show().html("Day Can't be blank.")
                    shouldSave = false;
                } else {
                    newReminder['reminderMode'] = 'after_deadline';
                    newReminder['day'] = this.reminders()[i].afterDay();
                }
            }
            if(this.reminders()[i].reminderMode() == "on_deadline"){
                newReminder['reminderMode'] = 'on_deadline'
                newReminder['day'] = 0
            }
            this.remindersToSave.push(newReminder);
        };
        if (!shouldSave) {
            this.remindersToSave = [];
            return;
        }
        console.log(ko.toJSON(this.remindersToSave));
        $.post('/project/reminders/' + project_id + "/", {'reminders':ko.toJSON(this.remindersToSave)}, function() {
            $('.success_message').show().html("The reminders has been saved").fadeOut(10000);
        })
    }

    var self = this;
    $.getJSON("/project/reminders/" + project_id + "/", function(data) {
        var mappedReminders = $.map(data, function(item) {
            var beforeDay = "";
            var afterDay = "";
            if(item.reminderMode === "after_deadline"){
                beforeDay = item.day;
            }else{
                afterDay = item.day;
            }
            return new reminder(item.message, beforeDay, afterDay, item.reminderMode, self)
        });
        self.reminders(mappedReminders);
    });
}

ko.applyBindings(new viewModel());
});

