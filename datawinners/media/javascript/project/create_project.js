DW.init_delete_periodicity_question_warning = function(){
    var kwargs = {container: "#delete_periodicity_question_warning",
        title: gettext('Warning: Your Collected Data Will be Lost'),
        width: 700,
        continue_handler: function(){
            question = questionnaireViewModel.selectedQuestion();
            questionnaireViewModel.removeQuestion(question);
        }
    };
    DW.delete_periodicity_question_warning = new DW.warning_dialog(kwargs);
};

basic_project_info = function(){
        var name = questionnaireViewModel.projectName() || '';
        var language = questionnaireViewModel.language();
        return JSON.stringify({'name':name, 'language':language});
};

DW.post_project_data = function (callback) {
    var questionnaire_data = JSON.stringify(ko.toJS(questionnaireViewModel.questions()));
    var post_create_request = function(original_questionnaire){

    var post_data = {
                      'questionnaire-code':questionnaireViewModel.questionnaireCode(),
                      'question-set':questionnaire_data,
                      'profile_form':basic_project_info(),
                      'csrfmiddlewaretoken':$('#question_form input[name=csrfmiddlewaretoken]').val()
                    };
        if (typeof original_questionnaire != "undefined"){
            post_data["datasenders"] = JSON.stringify(original_questionnaire.datasenders);
            post_data["reminder_and_deadline"] = JSON.stringify(original_questionnaire.reminder_and_deadline);
        }

        $.post(post_url , post_data).done(function(response){
            var responseJson = $.parseJSON(response);
            if (responseJson.success) {
               return callback(responseJson);
            }
            else {
                $.unblockUI();
                if(!(responseJson.code_has_errors || responseJson.name_has_errors)) {
                    questionnaireViewModel.errorInResponse(true);
                }
                if(responseJson.code_has_errors) {
                    questionnaireViewModel.questionnaireCode.valid(false);
                    questionnaireViewModel.questionnaireCode.error(responseJson.error_message['code']);
                }
                if(responseJson.name_has_errors) {
                    questionnaireViewModel.projectName.valid(false);
                    questionnaireViewModel.projectName.error(responseJson.error_message['name']);
                }
//                questionnaireViewModel.responseErrorMsg(responseJson.error_message);
            }
        });
    };
    original_questionnaire_id = questionnaireCreationOptionsViewModel.selectedQuestionnaireId();
    if(original_questionnaire_id){
    questionnaireDataFetcher.getQuestionnaire(questionnaireCreationOptionsViewModel.selectedQuestionnaireId()).done(function(original_questionnaire){
        post_create_request(original_questionnaire);
    });
    } else {
        post_create_request();
    }
};


DW.controllers = {
    "templateQuestionnaire":function () {
            questionnaireViewModel.clearQuestionnaire();
            templateFetcher.getTemplateData(this.params.template_id).done(function(templateData){
                questionnaireViewModel.projectName(templateData.project_name);
                questionnaireViewModel.language(templateData.project_language);
                questionnaireViewModel.questionnaireCode(templateData.questionnaire_code);
                DW.existing_questions = templateData.existing_questions;
                $(templateData.existing_questions).each(function (index, question) {
                    questionnaireViewModel.loadQuestion(new DW.question(question));
                });
                questionnaireViewModel.showQuestionnaireForm(true);
                questionnaireCreationOptionsViewModel.showQuestionnaireCreationOptions(false);
            });

    },
    "copyQuestionnaire": function(){
        questionnaireViewModel.clearQuestionnaire();
        var questionnaireData = questionnaireDataFetcher.getQuestionnaireData(this.params.questionnaire_id);
        questionnaireViewModel.language(questionnaireData.language);
        var question_list = questionnaireData.questions;
        for (var index in question_list) {
            var questions = new DW.question(question_list[index]);
            questionnaireViewModel.loadQuestion(questions);
        };
        questionnaireCreationOptionsViewModel.showQuestionnaireCreationOptions(false);
        questionnaireViewModel.showQuestionnaireForm(true);
        questionnaireViewModel.enableQuestionnaireTitleFocus(true);
        questionnaireViewModel.questionnaireCode(questionnaire_code);
    },
    "blankQuestionnaire": function () {
            questionnaireViewModel.clearQuestionnaire();
            questionnaireViewModel.showQuestionnaireForm(true);
            questionnaireCreationOptionsViewModel.showQuestionnaireCreationOptions(false);
            questionnaireViewModel.questionnaireCode(questionnaire_code);
            questionnaireViewModel.enableQuestionnaireTitleFocus(true);
    },
    "questionnaireCreationOptions": function () {
            questionnaireCreationOptionsViewModel.resetCreationOption();
            questionnaireDataFetcher.clearCache();
            questionnaireViewModel.showQuestionnaireForm(false);
            questionnaireCreationOptionsViewModel.showQuestionnaireCreationOptions(true);
    }
};


DW.projectRouter = Sammy(function () {
        this.get('#questionnaire/new', DW.controllers.blankQuestionnaire);
        this.get('#questionnaire/load/:template_id', DW.controllers.templateQuestionnaire);
        this.get('#questionnaire/copy/:questionnaire_id', DW.controllers.copyQuestionnaire)
        this.get('project/wizard/create/$', DW.controllers.questionnaireCreationOptions);
});

function _initializeViewModel() {
    ko.setTemplateEngine(new ko.nativeTemplateEngine());
    window.questionnaireViewModel = new ProjectQuestionnaireViewModel();
    ko.applyBindings(questionnaireViewModel, $('#create_questionnaire')[0]);
    ko.applyBindings(questionnaireCreationOptionsViewModel, $('#project_profile')[0]);
}

function _save_questionnaire(callback) {
    if(!DW.check_empty_questionnaire() || !questionnaireViewModel.validateForSubmission())
        return false;

    $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
    DW.post_project_data(callback);
}
$(document).ready(function () {
    _initializeViewModel();
    DW.option_warning_dialog.init();
    DW.init_delete_periodicity_question_warning();
    DW.init_empty_questionnaire_warning();
    var options = {
                    successCallBack: _save_questionnaire,
                    isQuestionnaireModified: function(){
                                                return questionnaireViewModel.showQuestionnaireForm() &&
                                                    (DW.questionnaire_was_changed || questionnaireViewModel.questions().length > 0);
                                            }
                  };
    new DW.CancelQuestionnaireWarningDialog(options).init();

    $("#save_and_create").bind("click", function () {
            _save_questionnaire(function (response) {
                var redirect_url = '/project/overview/' + response.project_id;
                window.location.replace(redirect_url);
                return true;
            });
    });

    DW.projectRouter.run();

});


