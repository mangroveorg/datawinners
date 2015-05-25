var PollOptionsViewModel = function(){
    var self = this;
    self.selectedPollOption = ko.observableArray([1,3,4]);

    if (is_active == 'True'){
        self.disableDeactivate = ko.observable(false);
    }
    else {
        self.disableDeactivate = ko.observable(true);
    }
    self.deactivate_poll = function(){
         data = {};
        if (self.disableDeactivate() != true) {
            $.post(deactivate_poll_url, data).done(function (response) {

                var responseJson = $.parseJSON(response);
                if (responseJson['success']) {
                    self.disableDeactivate(true);
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
