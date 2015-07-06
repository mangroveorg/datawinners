function PollViewModel() {
    var self = this;
    self.show_sms = ko.observable(gettext('Save/Create Poll'));
    self.number_of_days = ko.observable();
    self.to_date_poll = ko.observable();

    self.show_sms.subscribe(function(){
       window.smsViewModel.clearSelection();
    });
    var active_poll_days = [1,2,3,4,5];
    var start_date = new Date();
    var calculateDays = new CalculateDays(start_date.getDate() + self.number_of_days() + start_date);
    var maxAllowedSMSCharacters = 160;

    var smsTextElement = $("#sms-text");
    var smsTextLengthCheck = function (e) {
        if (e.target.value.length > maxAllowedSMSCharacters) {
            $(this).val(e.target.value.substring(0, maxAllowedSMSCharacters));
        }
        window.smsViewModel.smsCharacterCount($(this).val().length +
            gettext(" of " + maxAllowedSMSCharacters + " characters used"));
    };

    smsTextElement.keyup(smsTextLengthCheck);
    smsTextElement.keydown(smsTextLengthCheck)

    window.smsViewModel.smsOptionList = ko.observableArray([ {"label":gettext('Select Recipients'), disable: ko.observable(true)},
                                            {"label":gettext('Group'), "code": "group"},
                                            {"label":gettext('Contacts linked to a Questionnaire'), "code": "linked"}
                                            ]);

    var end_date;
    self.days_active = ko.computed(function(){
        var current_date = new Date();
        current_date.setDate(current_date.getDate() + self.number_of_days());
        end_date = current_date;
        self.to_date_poll(calculateDays.get_formatted_date_for_poll(current_date));
        return active_poll_days
    });

    self.from_date_poll = ko.observable(calculateDays.get_formatted_date_for_poll(start_date));

    self.disableSendPoll = ko.computed(function(){
        if(window.smsViewModel.disableSendSms() ){
            if(DW.ko.mandatoryValidator(window.questionnaireViewModel.projectName) && self.show_sms() == 'Save Poll')
                return false;
            return (self.show_sms() != 'Save Poll' || window.smsViewModel.validate() == 1)
        }
        return false;
    });

    self.validateCreatePoll = function(){
        return (DW.ko.mandatoryValidator(window.questionnaireViewModel.projectName) && ((window.smsViewModel.validate() == 1) || self.show_sms() == 'Save Poll'));
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
        if (self.show_sms() == 'Send Poll') {
            window.smsViewModel.sendSms(project_id)
        }
    }

    self.create_poll = function(){
        if(self.validateCreatePoll()) {
            var selected_option = {};
            var question = $("#sms-text").val();
            if (self.show_sms() == 'Save Poll'){
                selected_option = {
                    'option' : 'broadcast'
            };
                question = gettext("Response")
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
                     DW.trackEvent('Create Questionnaire', 'Poll');
                }
                else{
                    if(responseJson['error_message']['name']){
                        window.questionnaireViewModel.projectName.setError(responseJson['error_message']['name']);}
                    else{

                        var responseMessage =responseJson['error_message'].replace(responseJson['question_name_active'], '<a class="link_color" href="/project/poll/' + responseJson['question_id_active'] + '">' + '</a>');
                        $('<div class="information_box">' + responseMessage + '</div>').insertBefore($("#poll_title"));
                    }

                }
            });
        }
        else {if(window.questionnaireViewModel.projectName().trim() == ""){

            window.questionnaireViewModel.projectName.setError('This field is required');

        }}
    };
}
