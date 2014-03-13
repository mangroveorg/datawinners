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
    "questionnaire_load_controller":function () {
            questionnaireViewModel.questions([]);
            questionnaireViewModel.errorInResponse(false);
            questionnaireViewModel.selectedQuestion(null);
            var project_details = DW.getTemplateData(this.params.template_id);

            questionnaireViewModel.projectName(project_details.project_name);
            questionnaireViewModel.language(project_details.project_language);
            questionnaireViewModel.questionnaireCode(project_details.questionnaire_code);
            DW.existing_questions = $.parseJSON(project_details.existing_questions);
            $($.parseJSON(project_details.existing_questions)).each(function (index, question) {
                questionnaireViewModel.loadQuestion(new DW.question(question));
            });
            questionnaireViewModel.showQuestionnaireForm(true);
            questionnaireCreationOptionsViewModel.showQuestionnaireCreationOptions(false);
    },
    "blank_questionnaire": function () {
            questionnaireViewModel.clearQuestionnaire();
            questionnaireViewModel.showQuestionnaireForm(true);
            questionnaireCreationOptionsViewModel.showQuestionnaireCreationOptions(false);
            questionnaireViewModel.questionnaireCode(questionnaire_code);
            questionnaireViewModel.enableQuestionnaireTitleFocus(true);
    }
};


DW.projectRouter = Sammy(function () {
        this.get('#:questionnaire/new', DW.controllers.blank_questionnaire);

        this.get('#:questionnaire/load/:template_id', DW.controllers.questionnaire_load_controller);

        this.get('#:create', function () {
            questionnaireViewModel.showQuestionnaireForm(false);
            questionnaireCreationOptionsViewModel.showQuestionnaireCreationOptions(true);
        });
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


