function ProjectQuestionnaireViewModel() {
    var self = this;

    self.uniqueIdTypes = ko.observableArray(uniqueIdTypes);
    self.isXLSUploadQuestionnaire = ko.observable(false);
    self.showPollQuestionnaireForm = ko.observable(false);
    self.show_sms = ko.observable();
    self.days_active = ko.observableArray(_.range(1,6));
    self.above = ko.observable('above');
    self.below = ko.observable('below');
    //self.send_poll_sms = ko.observable(false);
    //self.send_broadcast = ko.observable(false);
    self.show_error = ko.observable(false);
    self.projectNameAlreadyExists = ko.observable();
    self.show_send_sms_block_ex = ko.observable();

    self.disableSendPoll = ko.computed(function(){
        if(window.smsViewModel.disableSendSms() ){
            if(!(DW.ko.mandatoryValidator(self.projectName)) && (!self.show_sms())) {

                return true;
            }
            else{
                return false;
            }
        }
        return false;
    });

    self.validateCreatePoll = function(){
        return ((window.smsViewModel.validate() == 1) || self.show_sms() == 'poll_broadcast') && (DW.ko.mandatoryValidator(self.projectName));
    };

    function get_questionnaire_or_group_names(selected_option) {
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
                'poll_name': self.projectName().trim(),
                'active_days': self.days_active,
                'question': question,
                'selected_option' : JSON.stringify(selected_option),
                'csrfmiddlewaretoken': $("#poll_form input[name=csrfmiddlewaretoken]").val()



            };

            $.post(create_poll_url, data).done(function (response) {

                var responseJson = $.parseJSON(response);
                if(responseJson['success']) {
                    var redirect_url = '/project/'+ responseJson.project_id + '/results/' + responseJson.project_code ;
                    DW.trackEvent('poll-creation-method', 'poll-qns-success');
                    window.location.replace(redirect_url);
                    window.smsViewModel.sendSms()
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



    self.showUniqueIdTypeList = ko.computed(function(){
        return self.uniqueIdTypes().length == 0;
    }, self);
    self.isUniqueIdTypeVisible = ko.observable(false);

    self.toggleUniqueIdTypesVisibility = function () {
        var isVisible = self.isUniqueIdTypeVisible();
        _clearNewUniqueIdError();
        self.isUniqueIdTypeVisible(!isVisible);
    };

    ko.postbox.subscribe("uniqueIdTypeSelected", _resetUniqueIdTypeContentState, self);

    self.selectUniqueIdType = function (uniqueIdType) {
        ProjectQuestionnaireViewModel.prototype.selectedQuestion().uniqueIdType(uniqueIdType);
        self.isUniqueIdTypeVisible(false);
        _clearNewUniqueIdError();
    };

    self.newUniqueIdType = DW.ko.createValidatableObservable();
    self.newUniqueIdType.subscribe(DW.set_questionnaire_was_change);
    self.uniqueIdButtonText = ko.observable(gettext("Add"));

    self.addNewUniqueIdType = function () {
        var newUniqueIdType = self.newUniqueIdType();
        self.uniqueIdButtonText(gettext("Adding..."));
        $.post('/entity/type/create', {entity_type_regex: newUniqueIdType})
            .done(function (responseString) {
                self.uniqueIdButtonText(gettext('Add'));
                var response = $.parseJSON(responseString);
                if (response.success) {
                    var array = self.uniqueIdTypes();
                    array.push(newUniqueIdType);
                    array.sort();
                    self.newUniqueIdType.clearError();
                    self.uniqueIdTypes.valueHasMutated();
                    self.selectUniqueIdType(newUniqueIdType);
                }
                else {
                    self.newUniqueIdType.setError(response.message);
                }
            });
    };

    function _clearNewUniqueIdError() {
        self.newUniqueIdType("");
        self.newUniqueIdType.clearError();
    }

    function _resetUniqueIdTypeContentState() {
        _clearNewUniqueIdError();
        self.isUniqueIdTypeVisible(false);
    }

    self.validateAndRemoveQuestion = self.validateAndRemoveQuestion.bind(self);

    self.learnMoreBlockVisible = ko.observable(false);

    self.toggleLearnMoreBlockVisibility = function(){
    }
}

ProjectQuestionnaireViewModel.prototype = new QuestionnaireViewModel();
ProjectQuestionnaireViewModel.prototype.constructor = ProjectQuestionnaireViewModel;
