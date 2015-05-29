var PollOptionsViewModel = function(){
    var self = this;
    self.selectedPollOption = ko.observableArray([1,3,4]);
    self.change_status = ko.observable();
    self.status = ko.observable();
    self.fromDate = ko.observable();
    self.toDate = ko.observable();
    self.isOpen = ko.observable(false);
    self.isDeactivated = ko.observable(false);
    self.deactivatePollDialog = ko.observable($('#deactivate_poll_dialog').html());
    self.activatePollDialog = ko.observable($('#activate_poll_dialog').html());

    if (is_active == 'True'){
        self.change_status('Deactivate');
        self.status('Active');
        self.fromDate("From "+from_date);
        self.toDate("To "+to_date);
    }
    else {
        self.change_status('Activate');
        self.status('Deactivated');
        self.fromDate("");
        self.toDate("");
    }
    self.deactivate_poll = function(){
        data = {};
        if (self.change_status() == 'Deactivate' ) {
            $.post(deactivate_poll_url, data).done(function (response) {
                var responseJson = $.parseJSON(response);
                if (responseJson['success']) {
                    self.status('Deactivated');
                    self.change_status('Activate');
                    self.fromDate("");
                    self.toDate("");
                    DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
                }
                else{
                    $('<div class="message-box">' + responseJson['message'] + '</div>').insertBefore($("#poll_success"))
                }
            });
        }
        else if(self.change_status() == 'Activate'){
            $.post(activate_poll_url, data).done(function (response) {
                var responseJson = $.parseJSON(response);
                if (responseJson['success']) {
                    self.status('Active');
                    self.change_status('Deactivate');
                    self.fromDate("From "+ from_date);
                    self.toDate("To "+ to_date);
                    DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
                }
                else{
                    $('<div class="warning-message-box">' + responseJson['message'] + '</div>').insertBefore($("#poll_success"))
                }
            });
        }
        self.close_popup();
    };

    self.open = function () {
        (self.change_status() == 'Deactivate') ? self.isOpen(true) : self.isDeactivated(true);
    };

    self.close_popup = function () {
        self.isOpen(false);
        self.isDeactivated(false);
    };
};

$(document).ready(function () {
//    window.pollViewModel = new PollViewModel();
    window.poll_options = new PollOptionsViewModel();
    ko.applyBindings(window.poll_options, $('#poll_options')[0]);
//    ko.applyBindings(window.pollViewModel, $('#poll_options')[0]);
});
