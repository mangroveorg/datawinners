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
}

basic_project_info = function(){
        var name = questionnaireViewModel.projectName() || '';
        var language = questionnaireViewModel.language();
        var activity_report = 'yes';
        return JSON.stringify({'name':name, 'language':language, 'activity_report':activity_report});
};

DW.post_project_data = function (state, function_to_construct_redirect_url_on_success) {
    var questionnaire_data = JSON.stringify(ko.toJS(questionnaireViewModel.questions()));

    var post_data = {
                      'questionnaire-code':questionnaireViewModel.questionnaireCode(),
                      'question-set':questionnaire_data,
                      'profile_form':basic_project_info(),
                      'project_state':state,
                      'csrfmiddlewaretoken':$('#question_form input[name=csrfmiddlewaretoken]').val()
                    };

    $.post(post_url , post_data, function (response) {
        var responseJson = $.parseJSON(response);
        if (responseJson.success) {
            var redirect_url = function_to_construct_redirect_url_on_success(responseJson);
            var has_newly_added_question = questionnaireViewModel.has_newly_added_question();
            window.location.replace(redirect_url);
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
            var project_details = DW.getTemplateDataFromCache(this.params.template_id);

            questionnaireViewModel.projectName(project_details.project_name);
            questionnaireViewModel.language(project_details.project_language);
            questionnaireViewModel.questionnaireCode(project_details.questionnaire_code);
            DW.existing_questions = $.parseJSON(project_details.existing_questions);
            $($.parseJSON(project_details.existing_questions)).each(function (index, question) {
                questionnaireViewModel.loadQuestion(new DW.question(question));
            });
            questionnaireViewModel.showQuestionnaireForm(true);
            questionnaireHelperModel.showQuestionnaireCreationOptions(false);
    },
    "blank_questionnaire": function () {
            questionnaireViewModel.projectName('');
            questionnaireViewModel.questions([]);
            questionnaireViewModel.showQuestionnaireForm(true);
            questionnaireHelperModel.showQuestionnaireCreationOptions(false);
            questionnaireViewModel.questionnaireCode(questionnaire_code);
    }
};


DW.projectRouter = Sammy(function () {
        this.get('#:questionnaire/new', DW.controllers.blank_questionnaire);

        this.get('#:questionnaire/load/:template_id', DW.controllers.questionnaire_load_controller);

        this.get('project/wizard/create/$', function () {
            questionnaireViewModel.showQuestionnaireForm(false);
            questionnaireHelperModel.showQuestionnaireCreationOptions(true);
        });
});

function _initializeViewModel() {
    ko.setTemplateEngine(new ko.nativeTemplateEngine());
    ko.applyBindings(questionnaireViewModel, $('#create_questionnaire')[0]);
    ko.applyBindings(questionnaireHelperModel, $('#project_profile')[0]);
}

$(document).ready(function () {
    _initializeViewModel();
    DW.option_warning_dialog.init();
    DW.init_delete_periodicity_question_warning();
    DW.init_empty_questionnaire_warning();

    $("#save_and_create").bind("click", function () {
        if(!DW.check_empty_questionnaire())
            return false;

        if (questionnaireViewModel.validateForSubmission()) {
            $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
            DW.post_project_data('Test', function (response) {
                return '/project/overview/' + response.project_id;
            });
        }
    });

    DW.projectRouter.run();

});


