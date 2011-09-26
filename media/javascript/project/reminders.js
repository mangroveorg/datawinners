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


function reminder(message, beforeDay, afterDay, reminderMode, ownerViewModel,targetDataSenders) {
    this.message = ko.observable(message);
    this.beforeDay = ko.observable(beforeDay);
    this.afterDay = ko.observable(afterDay);
    this.reminderMode = ko.observable(reminderMode);
    this.targetDataSenders = ko.observable(targetDataSenders);
    this.remove = function() {
        ownerViewModel.reminders.remove(this);
    }
    var self = this;
    this.header = ko.dependentObservable(function(){
        if(self.reminderMode() === "before_deadline"){
            return self.beforeDay() + " days before deadline";
        }else if(self.reminderMode() === "after_deadline"){
            return self.afterDay() + " days after deadline";
        }else{
            return "On the deadline";
        }
    }, this);
    this.selectBeforeDay = ko.dependentObservable(function(){
        if(self.reminderMode() === "before_deadline"){
            return true;
        }
        self.beforeDay("");
        return false;
    },this);
    this.selectAfterDay = ko.dependentObservable(function(){
        if (self.reminderMode() === "after_deadline"){
            return true;
        }
        self.afterDay("");
        return false;
    },this);
}

function viewModel() {
    this.reminders = ko.observableArray([]);
    this.remindersToSave = [];
    this.addReminder = function() {
        this.reminders.push(new reminder("", "", "", "on_deadline", this,'all_datasenders'));
        $("#review_section").accordion("destroy").accordion({header:'.header',collapsible: true} );
        if(this.reminders().length > 1)
            $("#review_section").accordion("activate",this.reminders().length -1);
    }
    this.save = function() {
        var shouldSave = true;
        for(var i = 0; i < this.reminders().length; i++){
            var newReminder = {};
            newReminder['targetDataSenders'] = this.reminders()[i].targetDataSenders()
            if (this.reminders()[i].message() === "") {
                $('#newMessage_err').show().html(gettext("Can't be blank."));
                shouldSave = false
            } else {
                newReminder['message'] = this.reminders()[i].message();
            }
            if (this.reminders()[i].reminderMode() == 'before_deadline') {
                if (this.reminders()[i].beforeDay() === "") {
                    $('#newDay_err').show().html(gettext("Day Can't be blank."))
                    shouldSave = false;
                } else {
                    newReminder['reminderMode'] = 'before_deadline';
                    newReminder['day'] = this.reminders()[i].beforeDay();
                }
            }
            if (this.reminders()[i].reminderMode() == 'after_deadline') {
                if (this.reminders()[i].afterDay() === "") {
                    $('#newDay_err').show().html(gettext("Day Can't be blank."))
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
        $.post('/project/reminders/' + project_id + "/", {'reminders':ko.toJSON(this.remindersToSave)}, function() {
            $('.success_message').show().html("The reminders has been saved").fadeOut(10000);
        })
    }

    var self = this;
    $.getJSON("/project/reminders/" + project_id + "/", function(data) {
        var mappedReminders = $.map(data, function(item) {
            var beforeDay = "";
            var afterDay = "";
            if(item.reminder_mode === "before_deadline"){
                beforeDay = item.day;
            }else{
                afterDay = item.day;
            }
            return new reminder(item.message, beforeDay, afterDay, item.reminder_mode, self, item.remind_to)
        });
        self.reminders(mappedReminders);
        $("#review_section").accordion({header:'.header',collapsible: true});
    });
}

ko.applyBindings(new viewModel());
});

