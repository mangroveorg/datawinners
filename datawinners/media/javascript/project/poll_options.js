var PollOptionsViewModel = function(){
    var self = this;
    self.selectedPollOption = ko.observableArray([1,3,4]);
    self.change_status = ko.observable();
    self.status = ko.observable();
    if (is_active == 'True'){
        //self.disableDeactivate = ko.observable(false);
        self.change_status('Deactivate');
        self.status('Active')
    }
    else {
        //self.disableDeactivate = ko.observable(true);
         self.change_status('Activate');
        self.status('Deactivated')
    }
    self.deactivate_poll = function(){
        data = {};
        if (self.change_status() == 'Deactivate' ) {
            $.post(deactivate_poll_url, data).done(function (response) {

                var responseJson = $.parseJSON(response);
                if (responseJson['success']) {
                    //self.disableDeactivate(true);
                    self.status('Deactivated');
                    self.change_status('Activate');
                    DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
                }
            });
        }
        else if(self.change_status() == 'Activate'){
            $.post(activate_poll_url, data).done(function (response) {

                var responseJson = $.parseJSON(response);
                if (responseJson['success']) {
                    //self.disableDeactivate(true);
                    self.status('Active');
                    self.change_status('Deactivate');
                    DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
                }
            });
        }
    }

};


$(document).ready(function () {
    window.poll_options = new PollOptionsViewModel();
    ko.applyBindings(window.poll_options, $('#poll_options')[0]);
});
