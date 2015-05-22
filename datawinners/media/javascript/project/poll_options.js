var PollOptions = function(){
    var self = this;
    self.selectedPollOption = ko.observableArray([1,3,4]);

};

$(document).ready(function () {
    window.poll_options = new PollOptions();
    ko.applyBindings(window.poll_options, ('#poll_options')[0]);
});
