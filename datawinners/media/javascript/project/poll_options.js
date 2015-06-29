var PollOptionsViewModel = function() {
    var self = this;
    var start_date = new Date();
    var end_date;
    var END_TIME = "T23:59:00";
    var data = {};

    var get_current_number_of_days = function(){
        return (to_date.getDate() - from_date.getDate());
    };

    self.get_formatted_date = function(date){
        return  date.getDate() +" " +month_name_map[date.getMonth()] +" "+ date.getFullYear();
    };

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

    self.selectedPollOption = ko.observableArray([1, 3, 4]);
    self.active_poll_days = ko.observable([1, 2, 3, 4, 5]);
    self.number_of_days = ko.observable();
    self.activation = ko.observable();
    self.deactivation = ko.observable();
    self.send_poll_text = ko.observable("Send SMS to More People");
    self.status = ko.observable();
    self.change_days = ko.observable();
    self.number_of_people = ko.observable();
    self.show_poll_table = ko.observable(false);
    self.poll_messages = ko.observableArray();
    self.from_date_poll = ko.observable(self.get_formatted_date(start_date));
    self.show_sms_option = ko.observable(false);

    self.duration = ko.observable();
    self.active_dates_poll = ko.observable();
    self.activationDialogVisible = ko.observable(false);
    self.deactivationDialogVisible = ko.observable(false);
    self.deactivatePollDialog = ko.observable($('#deactivate_poll_dialog').html());
    self.activatePollDialog = ko.observable($('#activate_poll_dialog').html());


    window.smsViewModel.smsOptionList = ko.observableArray([
                                {"label":gettext('Select Recipients'), disable: ko.observable(true)},
                                {"label":gettext('My Poll Recipients'), "code": "poll_recipients"},
                                {"label":gettext('Group'), "code": "group"},
                                {"label":gettext('Contacts linked to a Questionnaire'), "code": "linked"}
    ]);


    self.to_date_poll = ko.computed(function () {
        end_date = new Date();
        end_date.setDate(end_date.getDate() + self.number_of_days());
        return self.get_formatted_date(end_date);
    });

    if (is_active == 'True') {
        self.status(gettext('Active'));
        self.activation('');
        self.deactivation(gettext('Deactivate'));
        self.duration(gettext(' active From : ') + self.get_formatted_date(from_date) + gettext('To : ') + self.get_formatted_date(to_date));
        self.change_days(gettext('Change'));
        self.number_of_days(get_current_number_of_days());
        self.active_dates_poll('<i class="italic_grey"><b> '+gettext('From : ')+'</b> '+ self.get_formatted_date(from_date) + ' <b>&nbsp'+gettext(' To : ')+'</b>' + self.get_formatted_date(to_date) +'</i>');
    }
    else {
        $('#send_sms').addClass('link_color disable_link');
        self.status(gettext('Deactivated'));
        self.deactivation('');
        self.activation(gettext('Activate'));
        self.duration(gettext(' inactive'));
        self.number_of_days(1);
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
        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
        $.post(deactivate_poll_url, data).done(function (response) {
            var responseJson = $.parseJSON(response);
            if (responseJson['success']) {
                self.status(gettext('Deactivated'));
                self.activation(gettext('Activate'));
                self.deactivation('');
                self.duration(gettext(' inactive'));
                self.active_dates_poll('');
                self.change_days('');
                self.number_of_days(1);
                DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
                $('<div class="success-message-box">'+ gettext('Your changes have been saved.')+'</div>').insertBefore($("#poll_options"))
                $('#send_sms').addClass('link_color disable_link');
                 DW.trackEvent('Poll', 'deactivation');
            }
            else {
                $('<div class="message-box">' + responseJson['message'] + '</div>').insertBefore($("#poll_options"))
                $('.message-box').delay(2000).fadeOut();
            }
        });

        self.close_deactivation_popup();
    };

    self.show_poll_info = function(){
       $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
       $.get(get_poll_info_url, data).done(function (response) {
           var responseJson = $.parseJSON(response);
           if (responseJson['success']) {
               var poll_msg = responseJson['poll_messages'];
                self.poll_messages(poll_msg);
                self.show_poll_table(true);
                DW.trackEvent('Poll', 'Poll Table Info');
           }
       });
    };

    self.activate_poll = function() {
        data = {
            'end_date': end_date.getFullYear() + "-" + (end_date.getMonth()+1) + "-" + end_date.getDate() + END_TIME
        };
        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
        $.post(activate_poll_url, data).done(function (response) {
            var responseJson = $.parseJSON(response);
            if (responseJson['success']) {
                self.status(gettext('Active'));
                self.deactivation(gettext('Deactivate'));
                self.activation('');
                self.duration(gettext(' active From : ') + self.from_date_poll() + gettext('To : ') + self.to_date_poll());
                self.active_dates_poll('<i class="italic_grey"><b> '+gettext('From : ')+'</b> '+ self.from_date_poll() + ' <b>&nbsp'+gettext(' To : ')+'</b>' + self.to_date_poll() +'</i>');
                self.change_days(gettext('Change'));
                DW.trackEvent('poll-deactivation-method', 'poll-deactivate-success');
                $('<div class="success-message-box">' + gettext('Your changes have been saved.') +'</div>').insertBefore($("#poll_options"));

                $('#send_sms').removeClass('link_color disable_link');
                 DW.trackEvent('Poll', 'Activation');

            }
            else {
                var responseMessage =responseJson['message'].replace(responseJson['question_name_active'], '<a class="link_color" href="/project/poll/' + responseJson['question_id_active'] + '">' + responseJson['question_name_active'] + '</a>');
                $('<div class="information_box">' + responseMessage + '</div>').insertBefore($("#poll_options"));
                $('.message-box').delay(2000).fadeOut();
                $('.information_box').delay(30000).fadeOut();
            }
        });
        self.close_activation_popup();
    };
};

$(document).ready(function () {
    window.smsViewModel = new SmsViewModel();
    window.poll_options = new PollOptionsViewModel();
    ko.applyBindings(poll_options, $('#poll_options')[0]);
    ko.applyBindings(smsViewModel, $('#send-sms-section')[0]);
});
