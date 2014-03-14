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
        var activity_report = 'yes';
        return JSON.stringify({'name':name, 'language':language, 'activity_report':activity_report});
};

DW.post_project_data = function (callback) {
    var questionnaire_data = JSON.stringify(ko.toJS(questionnaireViewModel.questions()));

    var post_data = {
                      'questionnaire-code':questionnaireViewModel.questionnaireCode(),
                      'question-set':questionnaire_data,
                      'profile_form':basic_project_info(),
                      'csrfmiddlewaretoken':$('#question_form input[name=csrfmiddlewaretoken]').val()
                    };

    $.post(post_url , post_data).done(function(response){
        var responseJson = $.parseJSON(response);
        if (responseJson.success) {
           return callback(responseJson);
        }
        else {
            $.unblockUI();
            questionnaireViewModel.errorInResponse(true);
            questionnaireViewModel.responseErrorMsg(responseJson.error_message);
        }
    });
};


DW.controllers = {
    "templateQuestionnaire":function () {
            questionnaireViewModel.questions([]);
            questionnaireViewModel.errorInResponse(false);
            questionnaireViewModel.selectedQuestion(null);
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
        var question_list = questionnaireDataFetcher.getQuestionnaireData(this.params.questionnaire_id).questions;
        for (var index in question_list) {
            var questions = new DW.question(question_list[index]);
            questionnaireViewModel.loadQuestion(questions);
        };
        questionnaireCreationOptionsViewModel.showQuestionnaireCreationOptions(false);
        questionnaireViewModel.showQuestionnaireForm(true); //TODO:keep only one flag
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
            questionnaireViewModel.showQuestionnaireForm(false);
            questionnaireCreationOptionsViewModel.showQuestionnaireCreationOptions(true);
    }
};


DW.projectRouter = Sammy(function () {
        this.get('#:questionnaire/new', DW.controllers.blankQuestionnaire);
        this.get('#:questionnaire/load/:template_id', DW.controllers.templateQuestionnaire);
        this.get('#:questionnaire/copy/:questionnaire_id', DW.controllers.copyQuestionnaire)
        this.get('#:create', DW.controllers.questionnaireCreationOptions);
});

function _initializeViewModel() {
    ko.setTemplateEngine(new ko.nativeTemplateEngine());
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
                                                return DW.questionnaire_was_changed || questionnaireViewModel.questions().length > 0;
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


