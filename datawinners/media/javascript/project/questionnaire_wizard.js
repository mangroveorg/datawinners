// vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
function _isQuestionnaireChanged() {
    return DW.questionnaire_was_changed || questionnaireViewModel.has_newly_added_question() ||
           DW.isQuestionsReOrdered(question_list) || existing_questionnaire_code != questionnaireViewModel.questionnaireCode();
}

function basic_project_info() {
    var name = questionnaireViewModel.projectName();
    var language = questionnaireViewModel.language();
    return JSON.stringify({'name':name, 'language':language});
}

$(document).ready(function () {
    window.questionnaireViewModel = new ProjectQuestionnaireViewModel();
    DW.init_inform_datasender_about_changes();
    DW.init_empty_questionnaire_warning();
    var options = {
                    successCallBack: submit_questionnaire,
                    isQuestionnaireModified: _isQuestionnaireChanged,
                    validate:function(){
                       return questionnaireViewModel.validateSelectedQuestion() && questionnaireViewModel.validateQuestionnaireDetails()
                    }

                  };
    new DW.CancelWarningDialog(options).init().initializeLinkBindings();
    new DW.UniqueIdHelpSection().init();

    var index;
    DW.existing_question_codes = [];
    for (index=0; index < question_list.length; index++) {
        DW.existing_question_codes.push(question_list[index].code);
        var questions = new DW.question(question_list[index]);
        questionnaireViewModel.loadQuestion(questions);
    }
    questionnaireViewModel.questionnaireCode(existing_questionnaire_code);
    questionnaireViewModel.projectName(project_name);
    questionnaireViewModel.language(project_language);
    questionnaireViewModel.hasExistingData = project_has_submissions === 'True';
    questionnaireViewModel.isEditMode = true;
    ko.setTemplateEngine(new ko.nativeTemplateEngine());

    ko.applyBindings(questionnaireViewModel);
    DW.charCount();
    DW.questionnaire_was_changed = false;
    $('#question_form').live("keyup", DW.charCount);
    $('#question_form').live("click", DW.charCount);
    $('.delete').live("click", DW.charCount);

    if(is_success == "True"){
        var flash_message = $("#message-label");
        flash_message.removeClass("none").removeClass("message-box").addClass("success-message-box").
        html("<label class='success'>" + gettext("Your changes have been saved.") + "</label").show();
        flash_message[0].scrollIntoView();
        window.scrollTo(0, 0);
        hide_message();
    }
    function hide_message() {
        $('#message-label').delay(5000).fadeOut();
    }

    function submit_questionnaire(callBack) {
        if(!DW.check_empty_questionnaire() || !questionnaireViewModel.validateForSubmission())
            return false;

        var data = JSON.stringify(ko.toJS(questionnaireViewModel.questions()));
        var has_callback = false;
        if(callBack)
            has_callback = true;
        DW.loading();
        var post_data = {
                            'questionnaire-code': questionnaireViewModel.questionnaireCode(),
                            'question-set': data,
                            'has_callback': has_callback,
                            'profile_form':basic_project_info()
                        };

        function show_error(responseText) {
            $("#global_error").addClass("none");
            var flash_message = $("#message-label");
            flash_message.removeClass("none").removeClass("success-message-box").addClass("message-box").
                html("<label class='error_message'>" + responseText + "</label>").show();
            flash_message[0].scrollIntoView();
        }
        function show_code_error(responseText) {
            questionnaireViewModel.questionnaireCode.valid(false);
            questionnaireViewModel.questionnaireCode.error(responseText);
            var flash_message = $("#questionnaire_code_validation_message");
            flash_message[0].scrollIntoView();
        }

        $.post(post_url, post_data,
            function (response) {
                var responseJson = $.parseJSON(response);
                if (!responseJson.success) {
                    if(!responseJson.code_has_error)
                        show_error(responseJson.error_message);
                    else
                        show_code_error(responseJson.error_message);
                }
                else {
                    if(_isQuestionnaireChanged()) {
                        DW.inform_datasender_about_changes.continue_handler = function(){
                            window.location.reload();
                            if (callBack)
                                callBack();
                        };
                        DW.inform_datasender_about_changes.show_warning();
                    }
                    else
                        window.location.reload();
                }
            }).error(function (e) {
                show_error(e.responseText);
            });
        return false;
    }

    $("#submit-button").click(function() {
        submit_questionnaire();
        return false;
    });

    $('input[name=text_length]:radio').change(
        function () {
            questionnaireViewModel.selectedQuestion().max_length("");
        }
    );

    //Currently unused - but may be used in future
    $("#edit_cancel").click(function () {
        history.go(-1);
    });

});