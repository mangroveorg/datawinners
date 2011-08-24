$(document).ready(function(){
    var project_id = $('#project_id').html();
    $('.choice').change(function(){
        var is_reminder = $("input[@name='rdio']:checked").val();
        var url = '/project/reminderstatus/' + project_id+"/";
        $.post(url, {'is_reminder': is_reminder}, function(data){
            var message = "Reminders has been activated for the project"
            if(is_reminder === "False"){
                message = "Reminders has been de-activated for the project"
                $('.add_reminder').hide();
            }else{
                $('.add_reminder').show();
            }
            $('.success_message').show().html(message).fadeOut(10000);
        });
    });

function reminder(message, day, ownerViewModel) {
    this.message = ko.observable(message);
    this.day = ko.observable(day);
    this.remove = function() { ownerViewModel.reminders.remove(this) }
}

function viewModel() {
    this.reminders = ko.observableArray([]);
    this.newMessage = ko.observable("");
    this.newDay = ko.observable();
    this.addReminder = function() {
        console.log(this.newMessage());
        console.log(this.newDay());
        this.reminders.push(new reminder(this.newMessage(), this.newDay(), this));
        this.newMessage("");
        this.newDay("");
    }
    this.save = function(){
        $.post('/project/reminders/' + project_id + "/", {'reminders':ko.toJSON(this.reminders())}, function(){
            $('.success_message').show().html("The reminders has been saved").fadeOut(10000);
        })
    }

    var self = this;
    $.getJSON("/project/reminders/" + project_id + "/", function(data) {
        var mappedReminders = $.map(data, function(item) {
            return new reminder(item.message, item.day, self)
        });
        self.reminders(mappedReminders);
    });
}

ko.applyBindings(new viewModel());
});

