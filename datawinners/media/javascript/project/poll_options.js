var PollOptionsViewModel = function() {
    var self = this;

    var start_date = new Date();
    var end_date;
    var END_TIME = "T23:59:00";
    var data = {};

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
    self.send_poll_text = ko.observable("Send Sms to More People");
    self.status = ko.observable();
    self.change_days = ko.observable();
    self.number_of_people = ko.observable();
    self.show_poll_table = ko.observable(false);
    self.poll_messages = ko.observableArray();
    self.from_date_poll = ko.observable(get_current_date());
    self.show_sms_option = ko.observable(false);

    self.duration = ko.observable();
    self.active_dates_poll = ko.observable();
    self.activationDialogVisible = ko.observable(false);
    self.deactivationDialogVisible = ko.observable(false);
    self.deactivatePollDialog = ko.observable($('#deactivate_poll_dialog').html());
    self.activatePollDialog = ko.observable($('#activate_poll_dialog').html());

    $('#sms-text').val(message_text);
    window.smsViewModel.smsOptionList = ko.observableArray([ {"label":gettext('Select Recipients'), disable: ko.observable(true)},
                                            {"label":gettext('My Poll Recipients'), "code": "poll_recipients"},
                                            {"label":gettext('Group'), "code": "group"},
                                            {"label":gettext('Contacts linked to a Questionnaire'), "code": "linked"}
                                            ]);


    self.to_date_poll = ko.computed(function () {
        end_date = new Date();
        end_date.setDate(end_date.getDate() + self.number_of_days());
        return end_date.getDate() + " " + month_name_map[end_date.getMonth()] + " " + end_date.getFullYear();
    });

    function get_current_date() {
        return start_date.getDate() + " " +
            month_name_map[start_date.getMonth()] + " " +
            start_date.getFullYear();
    }

    if (is_active == 'True') {
        self.status('Active');
        self.activation('');
        self.deactivation('Deactivate');
        self.duration('is active From ' + from_date + ' To ' + to_date);
        self.change_days('Change');
        self.active_dates_poll('<b>From</b> '+ from_date + ' <b>To</b> ' + to_date);
    }
    else {
        $('#send_sms').addClass('link_color disable_link');
        self.status('Deactivated');
        self.deactivation('');
        self.activation('Activate');
        self.duration('is inactive');
        self.change_days('');
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
        $.post(deactivate_poll_url, data).done(function (response) {
            var responseJson = $.parseJSON(response);
            if (responseJson['success']) {
                self.status('Deactivated');
                self.activation('Activate');
                self.deactivation('');
                self.duration('is inactive');
                self.active_dates_poll('');
                self.change_days('');
                DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
                $('<div class="success-message-box"> Your changes have been saved.</div>').insertBefore($("#poll_options"))
                $('#send_sms').addClass('link_color disable_link');
            }
            else {
                $('<div class="message-box">' + responseJson['message'] + '</div>').insertBefore($("#poll_success"))
            }
        });
        self.close_deactivation_popup();
    };

    self.show_poll_info = function(){
       $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
       $.get(get_poll_info_url, data).done(function (response) {
           var responseJson = $.parseJSON(response);
           if (responseJson['success']) {
               var poll_me = responseJson['poll_messages'];

                self.poll_messages(poll_me);
                self.show_poll_table(true);
           }
       });
    };

    self.activate_poll = function() {

        data = {
            'end_date': end_date.getFullYear() + "-" + (end_date.getMonth()+1) + "-" + end_date.getDate() + END_TIME
        };

        $.post(activate_poll_url, data).done(function (response) {
            var responseJson = $.parseJSON(response);
            if (responseJson['success']) {
                self.status('Active');
                self.deactivation('Deactivate');
                self.activation('');
                self.duration('is active From ' + self.from_date_poll() + ' To ' + self.to_date_poll());
                self.active_dates_poll('<b>From</b> '  + self.from_date_poll() + ' <b>To</b> ' + self.to_date_poll());
                self.change_days('Change');
                DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
                $('<div class="success-message-box"> Your changes have been saved.</div>').insertBefore($("#poll_options"));
                $('#send_sms').removeClass('link_color disable_link');
            }
            else {
                $('<div class="message-box">' + responseJson['message'] + '<a href="/project/poll/' + responseJson['question_id_active'] + '">' + responseJson['question_name_active'] + '</a></div>').insertBefore($("#poll_success"))
            }
        });
        data = {};
        self.close_activation_popup();
    };
};

$(document).ready(function () {
    window.smsViewModel = new SmsViewModel();
    window.poll_options = new PollOptionsViewModel();

    ko.applyBindings(poll_options, $('#poll_options')[0]);
});