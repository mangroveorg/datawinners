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
    questionnaireViewModel.language(project_language);
    questionnaireViewModel.hasExistingData = project_has_submissions === 'True';
    questionnaireViewModel.isEditMode = true;
    ko.setTemplateEngine(new ko.nativeTemplateEngine());
    ko.applyBindings(questionnaireViewModel);

    DW.charCount();
    DW.smsPreview();
    $('#question_form').live("keyup", DW.charCount);
    $('#question_form').live("click", DW.charCount);
    $('#question_form').live("click", DW.smsPreview);
    $('.delete').live("click", DW.charCount);
    $('.delete').live("click", DW.smsPreview);

//    $.validator.addMethod('spacerule', function (value, element, params) {
//        var list = $.trim($('#' + element.id).val()).split(" ");
//        if (list.length > 1) {
//            return false;
//        }
//        return true;
//    }, gettext("Space is not allowed in question code"));
//
//    $.validator.addMethod('regexrule', function (value, element, params) {
//        var text = $('#' + element.id).val();
//        var re = new RegExp('^[A-Za-z0-9 ]+$');
//        return re.test(text);
//    }, gettext("Only letters and digits are valid"));
//
//    $.validator.addMethod('naturalnumberrule', function (value, element, params) {
//        var num = $('#' + element.id).val();
//        return num != 0;
//    }, gettext("Answer cannot be of length less than 1"));

//    $("#question_form").validate({
//        messages: {
//            max_length: {
//                digits: gettext("Please enter positive numbers only")
//            }
//
//        },
//        rules: {
//            question_title: {
//                required: true
//            },
//            code: {
//                required: true,
//                spacerule: true,
//                regexrule: true
//            },
//            type: {
//                required: true
//            },
//            max_length: {
//                digits: true
//            },
//            range_min: {
//                number: true
//            },
//            range_max: {
//                number: true
//            },
//            choice_text: {
//                required: "#choice_text:visible"
//            }
//        },
//        wrapper: "div",
//        errorPlacement: function (error, element) {
//            var offset = element.offset();
//            error.insertAfter(element);
//            error.addClass('error_arrow'); // add a class to the wrapper
//
//        }
//
//    });

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

//        if (!$('#question_form').valid()) {
//            $("#message-label").show().html("<label class='error_message'> " + gettext("This questionnaire has an error") + ".</label> ");
//            hide_message();
//            return;
//        }
        DW.loading();
        var post_data = {
                            'questionnaire-code': questionnaireViewModel.questionnaireCode(),
                            'question-set': data,
                            'profile_form':basic_project_info()
                        };
        $.post(post_url, post_data,
            function (response) {
                $("#message-label").removeClass("none");
                $("#message-label").removeClass("message-box");
                $("#message-label").addClass("success-message-box");
                $("#message-label").show().html("<label class='success'>" + gettext("Your changes have been saved.") + "</label");

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
                $("#message-label").removeClass("none");
                $("#message-label").removeClass("success-message-box");
                $("#message-label").addClass("message-box");
                $("#message-label").show().html("<label class='error_message'>" + e.responseText + "</label>");
            });
        return false;
    }

    $("#submit-button").click(function() {
        if(!DW.check_empty_questionnaire()) return false;
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