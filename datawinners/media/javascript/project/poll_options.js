var PollOptionsViewModel = function() {
    var self = this;

    var start_date = new Date();
    var end_date;
    var END_TIME = "T23:59:00";

    var month_name_map = {
        0: gettext('January'),
        1: gettext('February'),
        2: gettext('March'),
        3: gettext('April'),
        4: gettext('May'),
        5: gettext('June'),
        6: gettext('July'),
        7: gettext('August'),
        8: gettext('September'),
        9: gettext('October'),
        10: gettext('November'),
        11: gettext('December')
    };

    var item_map_week = {
        1: gettext('Monday'),
        2: gettext('Tuesday'),
        3: gettext('Wednesday'),
        4: gettext('Thursday'),
        5: gettext('Friday'),
        6: gettext('Saturday'),
        0: gettext('Sunday')
    };

    self.selectedPollOption = ko.observableArray([1, 3, 4]);
    self.active_poll_days = ko.observable([1, 2, 3, 4, 5]);
    self.number_of_days = ko.observable();

    self.activation = ko.observable();
    self.deactivation = ko.observable();
    self.status = ko.observable();
    self.change_days = ko.observable();

    self.fromDate = ko.observable();
    self.toDate = ko.observable();

    self.to_date_poll = ko.observable();
    self.from_date_poll = ko.observable(get_current_date());

    self.duration = ko.observable();

    self.activationDialogVisible = ko.observable(false);
    self.deactivationDialogVisible = ko.observable(false);
    self.deactivatePollDialog = ko.observable($('#deactivate_poll_dialog').html());
    self.activatePollDialog = ko.observable($('#activate_poll_dialog').html());

    self.days_active = ko.computed(function () {
        var dat = new Date();
        dat.setDate(dat.getDate() + self.number_of_days());
        end_date = dat;
        self.to_date_poll(item_map_week[dat.getDay()] + ", " + dat.getDate() + " " + month_name_map[dat.getMonth()] + " " + dat.getFullYear());
        return self.active_poll_days
    });

    function get_current_date() {
        return item_map_week[start_date.getDay()] + ", " +
            start_date.getDate() + " " +
            month_name_map[start_date.getMonth()] + " " +
            start_date.getFullYear();
    }

    if (is_active == 'True') {
        self.status('Active');
        self.activation('');
        self.deactivation('Deactivate');
        self.duration('From ' + from_date + ' To ' + to_date +': ');
        self.change_days('Change');
        self.fromDate('From ' + from_date);
        self.toDate('To ' + to_date);
    }
    else {
        self.status('Deactivated');
        self.deactivation('');
        self.activation('Activate');
        self.duration('');
        self.change_days('');
        self.fromDate('');
        self.toDate('');
    }

    self.deactivate = function(){
        self.deactivationDialogVisible(true);
        self.activationDialogVisible(false);
    };

    self.activate = function () {
        self.activationDialogVisible(true);
        self.deactivationDialogVisible(false);
    };

    self.close_activation_popup = function () {
        self.activationDialogVisible(false);
    };

    self.close_deactivation_popup = function () {
        self.deactivationDialogVisible(false);
    };

    self.deactivate_poll = function () {
        data = {};
        $.post(deactivate_poll_url, data).done(function (response) {
            var responseJson = $.parseJSON(response);
            if (responseJson['success']) {
                self.status('Deactivated');
                self.activation('Activate');
                self.deactivation('');
                self.duration('');
                self.change_days('');
                self.fromDate('');
                self.toDate('');
                DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
            }
            else {
                $('<div class="message-box">' + responseJson['message'] + '</div>').insertBefore($("#poll_success"))
            }
        });
        self.close_deactivation_popup();
    };

    self.activate_poll = function() {
        data = {
            'end_date': end_date.getYear() + "-" + end_date.getMonth() + "-" + end_date.getDate() + END_TIME
        };
        $.post(activate_poll_url, data).done(function (response) {
            var responseJson = $.parseJSON(response);
            if (responseJson['success']) {
                self.status('Active');
                self.deactivation('Deactivate');
                self.activation('');
                self.duration('From ' + self.from_date_poll() + ' To ' + self.to_date_poll() +': ');
                self.change_days('Change');
                self.fromDate('From ' + self.from_date_poll());
                self.toDate('To ' + self.to_date_poll());
                DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
            }
            else {
                $('<div class="message-box">' + responseJson['message'] + '<a href="/project/poll/' + responseJson['question_id_active'] + '">' + responseJson['question_name_active'] + '</a></div>').insertBefore($("#poll_success"))
            }
        });
        self.close_activation_popup();
    };
};

$(document).ready(function () {
    window.poll_options = new PollOptionsViewModel();
    ko.applyBindings(window.poll_options, $('#poll_options')[0]);
});