function ReminderSettingsModel(){
    var self = this;
    self.enable_reminder_before_deadline = ko.observable(false);
    self.enable_reminder_on_deadline = ko.observable(false);
    self.enable_reminder_after_deadline = ko.observable(false);

    self.enable_reminder_before_deadline.subscribe(function(){
       $("#id_should_send_reminders_before_deadline").attr('checked', self.enable_reminder_before_deadline());
    });

    self.enable_reminder_after_deadline.subscribe(function(){
       $("#id_should_send_reminders_after_deadline").attr('checked', self.enable_reminder_after_deadline());
    });

    self.enable_reminder_on_deadline.subscribe(function(){
       $("#id_should_send_reminders_on_deadline").attr('checked', self.enable_reminder_on_deadline());
    });
}
