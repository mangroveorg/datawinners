    function PollViewModel() {
    var self = this;
    self.show_sms = ko.observable();
    self.number_of_days = ko.observable();
    var active_poll_days = [1,2,3,4,5];
    var current_date = new Date();
    window.smsViewModel.smsOptionList = ko.observableArray([ {"label":gettext('Select Recipients'), disable: ko.observable(true)},
                                            {"label":gettext('Group'), "code": "group"},
                                            {"label":gettext('Contacts linked to a Questionnaire'), "code": "linked"}
                                            ]);
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
        self.to_date_poll(dat.getDate()+ " "+ month_name_map[dat.getMonth()] +" "+ dat.getFullYear());
        return active_poll_days
    });

    function get_current_date() {
        return current_date.getDate() + " " +
                            month_name_map[current_date.getMonth()] + " " +
                            current_date.getFullYear();
    }

    self.from_date_poll = ko.observable(get_current_date());

    self.disableSendPoll = ko.computed(function(){
        if(window.smsViewModel.disableSendSms() ){
            return (self.show_sms() != 'poll_broadcast' || window.smsViewModel.validate() == 1)
        }
        return false;
    });

    self.validateCreatePoll = function(){
        window.smsViewModel.clearSelection();
        return (DW.ko.mandatoryValidator(window.questionnaireViewModel.projectName) && ((window.smsViewModel.validate() == 1) || self.show_sms() == 'poll_broadcast'));
    };

    function get_questionnaire_or_group_names() {
        if (window.smsViewModel.selectedSmsOption() == 'linked')
            return {
                'option': 'questionnaire_linked',
                'questionnaire_names': window.smsViewModel.selectedQuestionnaireNames()
            };

        else if (window.smsViewModel.selectedSmsOption() == 'group')
            return {
                'option': 'group',
                'group_names': window.smsViewModel.selectedGroupNames()
            };
    }

    function _send_sms_(project_id) {
        if (self.show_sms() == 'poll_via_sms') {
            window.smsViewModel.sendSms(project_id)
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
                'active_days': self.to_date_poll,
                'question': question,
                'selected_option' : JSON.stringify(selected_option),
                'csrfmiddlewaretoken': $("#poll_form input[name=csrfmiddlewaretoken]").val(),
                'end_date' : end_date.getFullYear() +"-"+ (end_date.getMonth()+1)+"-" + end_date.getDate()+"T" + end_date.getHours() +":"+ end_date.getMinutes() +":"+ end_date.getSeconds()
            };
            $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
            $.post(create_poll_url, data).done(function (response) {

                var responseJson = $.parseJSON(response);
                if(responseJson['success']) {
                    var redirect_url = '/project/'+ responseJson.project_id + '/results/' + responseJson.project_code ;
                    DW.trackEvent('poll-creation-method', 'poll-qns-success');
                    window.location.replace(redirect_url);
                    _send_sms_(responseJson.project_id);
                }
                else{
                    if(responseJson['error_message']['name']){
                        window.questionnaireViewModel.projectName.setError(responseJson['error_message']['name']);}
                    else{
                        $('<div class="message-error  margin-left-right-null">' + responseJson['error_message'] + '</a></span></div>').insertBefore($("#poll_title"));
                    }

                }

                $('#sms-success').hide();
                window.smsViewModel.clearSelection();
            });
        }
        else {if(window.questionnaireViewModel.projectName().trim() == ""){

            window.questionnaireViewModel.projectName.setError('This field is required');

        }}
    };
}
