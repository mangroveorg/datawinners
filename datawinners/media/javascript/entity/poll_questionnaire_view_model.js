function PollViewModel() {
    var self = this;

    self.show_sms = ko.observable();
    self.projectNameAlreadyExists = ko.observable();
    self.number_of_days = ko.observable();
    self.show_error = ko.observable(false);
    var active_poll_days = [1,2,3,4,5] ;
    var current_date = new Date();
    var month_name_map = {0:gettext('January') ,
                      1: gettext('February') ,
                      2: gettext('March') ,
                      3: gettext('April') ,
                      4: gettext('May') ,
                      5: gettext('June') ,
                      6: gettext('July') ,
                      7: gettext('August') ,
                      8: gettext('September'),
                      9: gettext('October') ,
                      10:gettext('November') ,
                      11:gettext('December') };

    var item_map_week = {
            1: gettext('Monday'),
            2: gettext('Tuesday'),
            3: gettext('Wednesday'),
            4: gettext('Thursday'),
            5: gettext('Friday'),
            6: gettext('Saturday'),
            0: gettext('Sunday')
    };
    self.to_date_poll = ko.observable();

    var end_date;
    self.days_active = ko.computed(function(){
        var dat = new Date();
        dat.setDate(dat.getDate() + self.number_of_days());
        end_date = dat;
        self.to_date_poll(item_map_week[dat.getDay()]+", "+ dat.getDate()+ " "+ month_name_map[dat.getMonth()] +" "+ dat.getFullYear());
        return active_poll_days
    });

    self.from_date_poll = ko.observable(item_map_week[current_date.getDay()]+", "+ current_date.getDate()+ " "+ month_name_map[current_date.getMonth()] +" "+ current_date.getFullYear());

    self.disableSendPoll = ko.computed(function(){
        if(window.smsViewModel.disableSendSms() ){
            if(!(DW.ko.mandatoryValidator(window.questionnaireViewModel.projectName)) && (self.show_sms() != 'poll_broadcast')) {

                return true;
            }
            else{
                return false;
            }
        }
        return false;
    });

    self.validateCreatePoll = function(){
        return ( (DW.ko.mandatoryValidator(window.questionnaireViewModel.projectName) && ((window.smsViewModel.validate() == 1) || self.show_sms() == 'poll_broadcast') ));
    };

    function get_questionnaire_or_group_names() {
        if (window.smsViewModel.selectedSmsOption() == 'linked') {

            return {
                'option': 'questionnaire_linked',
                'questionnaire_names': window.smsViewModel.selectedQuestionnaireNames()
            };

        }
        else if (window.smsViewModel.selectedSmsOption() == 'group') {

            return {
                'option': 'group',
                'group_names': window.smsViewModel.selectedGroupNames()
            };

        }

    }

    function _send_sms_() {
        if (self.show_sms() == 'poll_via_sms') {
            window.smsViewModel.sendSms()
        }
    }

    self.create_poll = function(){
        if(self.validateCreatePoll()) {
            var selected_option = {};
            var question = $("#sms-text").val();
            if (self.show_sms() == 'poll_broadcast'){
                selected_option = {
                    'option' : 'broadcast'
            };
                question = "BroadCast"
            }
            else{
                selected_option = get_questionnaire_or_group_names(selected_option);
            }

            var data = {
                'poll_name': window.questionnaireViewModel.projectName().trim(),
                'active_days': self.days_active,
                'question': question,
                'selected_option' : JSON.stringify(selected_option),
                'csrfmiddlewaretoken': $("#poll_form input[name=csrfmiddlewaretoken]").val(),
                'end_date' : end_date.getFullYear() +"-"+ end_date.getMonth()+"-" + end_date.getDate()+"T" + end_date.getHours() +":"+ end_date.getMinutes() +":"+ end_date.getSeconds()
            };

            $.post(create_poll_url, data).done(function (response) {

                var responseJson = $.parseJSON(response);
                if(responseJson['success']) {
                    var redirect_url = '/project/'+ responseJson.project_id + '/results/' + responseJson.project_code ;
                    DW.trackEvent('poll-creation-method', 'poll-qns-success');
                    window.location.replace(redirect_url);
                    _send_sms_();
                }
                else{
                    self.show_error(true);
                    self.projectNameAlreadyExists(responseJson['error_message']['name'])
                }

                $('#sms-success').hide();
                window.smsViewModel.clearSelection();
            });
        }
        else {if(window.questionnaireViewModel.projectName().trim() == ""){
            self.show_error(true);
            self.projectNameAlreadyExists('This field is required');

        }}
    };
}
