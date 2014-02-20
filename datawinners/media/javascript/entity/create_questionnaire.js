function populate_project_details() {
    if (is_edit) {
        $.getJSON("/project/details/" + questionnaire_code, function (project_details) {
            questionnaireViewModel.setQuestionnaireCreationType();
            questionnaireViewModel.projectName(project_details.project_name);
            questionnaireViewModel.language(project_details.project_language);
            questionnaireViewModel.questionnaireCode(project_details.questionnaire_code);
            DW.existing_questions = $.parseJSON(project_details.existing_questions);
            $($.parseJSON(project_details.existing_questions)).each(function(index, question){
                questionnaireViewModel.loadQuestion(new DW.question(question));
            });
            questionnaireViewModel.questions.valueHasMutated();

        });
    }
    else {
        questionnaireViewModel.questionnaireCode(questionnaire_code);
        questionnaireViewModel.questions([]);
        questionnaireViewModel.questions.valueHasMutated();
    }

}
function populate_subject_details() {
    $.getJSON("/entity/subject/details/" + subject_type, function (questionnaire_details) {
        questionnaireViewModel.questionnaireCode(questionnaire_details.questionnaire_code);
        DW.existing_questions = $.parseJSON(questionnaire_details.existing_questions);
        $($.parseJSON(questionnaire_details.existing_questions)).each(function(index, question){
            questionnaireViewModel.loadQuestion(new DW.question(question));
        });
        questionnaireViewModel.questions.valueHasMutated();
    });

}
DW.init_view_model = function (is_project_questionnaire) {
    if (is_project_questionnaire) {
        populate_project_details()
    }
    else{
//        Populating questions for subject questionnaire
        populate_subject_details()
    }
    questionnaireViewModel.selectedQuestion(new DW.question({is_null_question: true}));
    questionnaireViewModel.selectedQuestion.valueHasMutated();
    questionnaireViewModel.hasAddedNewQuestions = false;
    DW.smsPreview();
};

DW.error_appender = function (element) {
    this.element = element;
};

DW.error_appender.prototype = {
    appendError: function (errorText) {
        $(this.element).html("<label class='error_message'> " + gettext(errorText) + ".</label>");
    },
    hide_message: function () {
        $(this.element).delay(5000).fadeOut();
    }
};

DW.questionnaire_form = function (formElement) {
    this.formElement = formElement;
    this.errorAppender = new DW.error_appender("#message-label");
};

DW.questionnaire_form.prototype = {
    isValid: function () {
        return $(this.formElement).valid();
    },
    processValidation: function () {
        if (!this.isValid()) {
            this.errorAppender.appendError("This questionnaire has an error");
            this.errorAppender.hide_message();
            return false;
        }
        return true;
    }
};


$(document).ready(function () {
    DW.init_view_model(is_project_questionnaire);

    ko.validation.init({insertMessages: false});

    ko.validation.group(questionnaireViewModel);
    ko.applyBindings(questionnaireViewModel);

    questionnaireViewModel.routing.run();

    DW.charCount();
    $('#continue_project').live("click", DW.charCount);
    $('#question_form').live("keyup", DW.charCount);
    $('#question_form').live("click", DW.charCount);
    $('#question_form').live("click", DW.smsPreview);
    $('.delete').live("click", DW.charCount);

    $.validator.addMethod('spacerule', function (value, element, params) {
        var list = $.trim($('#' + element.id).val()).split(" ");
        if (list.length > 1) {
            return false;
        }
        return true;
    }, gettext("Space is not allowed in question code"));

    $.validator.addMethod('regexrule', function (value, element, params) {
        var text = $('#' + element.id).val();
        var re = new RegExp('^[A-Za-z0-9 ]+$');
        return re.test(text);
    }, gettext("Only letters and digits are valid"));

    $.validator.addMethod('naturalnumberrule', function (value, element, params) {
        var num = $('#' + element.id).val();
        return num != 0;
    }, gettext("Answer cannot be of length less than 1"));

    $.validator.addMethod('duplicate', function (value, element, params) {
        var val = $('#' + element.id).val();
        var valid = true;
        if (!questionnaireViewModel.hasAddedNewQuestions)
            return true;
        for (index in questionnaireViewModel.questions()) {
            var question = questionnaireViewModel.questions()[index];
            if (question != questionnaireViewModel.selectedQuestion() && question.display().toLowerCase() == val.toLowerCase()) {
                valid = false;
                break;
            }
        }
        return valid;
    }, gettext("This question is a duplicate"));

    $("#question_form").validate({
        messages: {
            max_length: {
                digits: gettext("Please enter positive numbers only")
            }
        },
        rules: {
            code: {
                required: true,
                spacerule: true,
                regexrule: true
            },
            'type[]': {
                required: true
            },
            max_length: {
                digits: true
            },
            range_min: {
                number: true
            },
            range_max: {
                number: true
            },
            choice_text: {
                required: "#choice_text:visible"
            }
        },
        wrapper: "div",
        errorPlacement: function (error, element) {
            var offset = element.offset();
            error.insertAfter(element);
            error.addClass('error_arrow');  // add a class to the wrapper
        }
    });

    $("#question_title").rules("add", {duplicate: true});

    $('input[name=text_length]:radio').change(
        function () {
            questionnaireViewModel.selectedQuestion().max_length("");
        }
    );
});
