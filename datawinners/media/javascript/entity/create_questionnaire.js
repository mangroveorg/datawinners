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
var init_view_model = function () {
    if (is_project_questionnaire && is_edit) {
        questionnaireViewModel.setQuestionnaireCreationTypeToEdit();
    }
    else if (!is_project_questionnaire){
//        Populating questions for subject questionnaire
        populate_subject_details();
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
    init_view_model();

    ko.setTemplateEngine(new ko.nativeTemplateEngine());
    ko.validation.group(questionnaireViewModel);
    ko.applyBindings(questionnaireViewModel);

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
            },
            answer_type: {
               required: true            }
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
