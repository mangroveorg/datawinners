var PollOptionsViewModel = function() {
    var self = this;

    var end_date;
    var current_date = new Date();

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

    self.change_status = ko.observable();
    self.status = ko.observable();

    self.fromDate = ko.observable();
    self.toDate = ko.observable();

    self.to_date_poll = ko.observable();
    self.from_date_poll = ko.observable(get_current_date());
    self.from_time_poll = ko.observable(get_current_time());

    self.isOpen = ko.observable(false);

    self.isDeactivated = ko.observable(false);
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
        return item_map_week[current_date.getDay()] + ", " +
            current_date.getDate() + " " +
            month_name_map[current_date.getMonth()] + " " +
            current_date.getFullYear();
    }


    function get_current_time() {
        return current_date.getHours() + ":" +
            current_date.getMinutes() + ":" +
            current_date.getSeconds();
    }

    if (is_active == 'True') {
        self.change_status('Deactivate');
        self.status('Active');
        self.fromDate("From " + from_date);
        self.toDate("To " + to_date);
    }
    else {
        self.change_status('Activate');
        self.status('Deactivated');
        self.fromDate("");
        self.toDate("");
    }

    self.open = function () {
        (self.change_status() == 'Deactivate') ? self.isOpen(true) : self.isDeactivated(true);
    };

    self.close_popup = function () {
        self.isOpen(false);
        self.isDeactivated(false);
    };

    self.deactivate_poll = function () {
        data = {};
        if (self.change_status() == 'Deactivate') {
            $.post(deactivate_poll_url, data).done(function (response) {
                var responseJson = $.parseJSON(response);
                if (responseJson['success']) {
                    self.status('Deactivated');
                    self.change_status('Activate');
                    self.fromDate("");
                    self.toDate("");
                    DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
                }
                else {
                    $('<div class="message-box">' + responseJson['message'] + '</div>').insertBefore($("#poll_success"))
                }
            });
        }
        else if (self.change_status() == 'Activate') {
            $.post(activate_poll_url, data).done(function (response) {
                var responseJson = $.parseJSON(response);
                if (responseJson['success']) {
                    self.status('Active');
                    self.change_status('Deactivate');
                    self.fromDate("From " + self.from_date_poll());
                    self.toDate("To " + self.to_date_poll());
                    DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
                }
                else {
                    $('<div class="message-box">' + responseJson['message'] + '<a href="/project/poll/' + responseJson['question_id_active'] + '">' + responseJson['question_name_active'] + '</a></div>').insertBefore($("#poll_success"))
                }
            });
        }
        self.close_popup();
    };
};

$(document).ready(function () {
    window.poll_options = new PollOptionsViewModel();
    ko.applyBindings(window.poll_options, $('#poll_options')[0]);
});