// vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
$(document).ready(function () {
    DW.questionnaire_was_changed = false;
    DW.init_inform_datasender_about_changes();
    DW.init_empty_questionnaire_warning();
    var index;
    for (index in question_list) {
        var questions = new DW.question(question_list[index]);
        questionnaireViewModel.loadQuestion(questions);
    }
    questionnaireViewModel.questionnaireCode(questionnaire_code);
    questionnaireViewModel.projectName(project_name);
    questionnaireViewModel.language(project_language);
    questionnaireViewModel.hasExistingData = project_has_submissions === 'True';
    questionnaireViewModel.isEditMode = true;
    ko.setTemplateEngine(new ko.nativeTemplateEngine());
    ko.applyBindings(questionnaireViewModel);

    DW.charCount();
    $('#question_form').live("keyup", DW.charCount);
    $('#question_form').live("click", DW.charCount);
    $('.delete').live("click", DW.charCount);

    function hide_message() {
        $('#message-label').delay(5000).fadeOut();
    }

    function basic_project_info() {
        var name = questionnaireViewModel.projectName();
        var language = questionnaireViewModel.language();
        var activity_report = 'yes';
        return JSON.stringify({'name':name, 'language':language, 'activity_report':activity_report});
    };

    function submit_questionnaire() {

        var data = JSON.stringify(ko.toJS(questionnaireViewModel.questions()), null, 2);
        DW.loading();
        var post_data = {
                            'questionnaire-code': questionnaireViewModel.questionnaireCode(),
                            'question-set': data,
                            'profile_form':basic_project_info()
                        };
        $.post(post_url, post_data,
            function (response) {
                var flash_message = $("#message-label");
                flash_message.removeClass("none").removeClass("message-box").addClass("success-message-box").
                html("<label class='success'>" + gettext("Your changes have been saved.") + "</label").show();
                flash_message[0].scrollIntoView();

                if (DW.questionnaire_was_changed || questionnaireViewModel.has_newly_added_question() || DW.has_questions_changed(question_list) || questionnaire_code != questionnaireViewModel.questionnaireCode()) {
                    questionnaireViewModel.set_all_questions_as_old_questions();
                    questionnaire_code = questionnaireViewModel.questionnaireCode();
                    DW.inform_datasender_about_changes.show_warning();
                    DW.questionnaire_was_changed = false;
                }
                hide_message();
                redirect();
            }).error(function (e) {
                $("#global_error").addClass("none");
                var flash_message = $("#message-label");
                flash_message.removeClass("none").removeClass("success-message-box").addClass("message-box").
                html("<label class='error_message'>" + e.responseText + "</label>").show();
                flash_message[0].scrollIntoView();
            });
        return false;
    }

    $("#submit-button").click(function() {
        if(!DW.check_empty_questionnaire())
            return false;
        if(!questionnaireViewModel.validateForSubmission())
            return false;
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