// function populate_subject_details() {
//    $.getJSON("/entity/subject/details/" + subject_type, function (questionnaire_details) {
//        questionnaireViewModel.questionnaireCode(questionnaire_details.questionnaire_code);
//        DW.existing_questions = $.parseJSON(questionnaire_details.existing_questions);
//        $($.parseJSON(questionnaire_details.existing_questions)).each(function(index, question){
//            questionnaireViewModel.loadQuestion(new DW.question(question));
//        });
//        questionnaireViewModel.questions.valueHasMutated();
//    });
//
//}

//var init_view_model = function () {
//    if (!is_project_questionnaire){
////        Populating questions for subject questionnaire
//        populate_subject_details();
//    }
////    questionnaireViewModel.selectedQuestion(new DW.question({is_null_question: true}));
//    questionnaireViewModel.selectedQuestion.valueHasMutated();
//    questionnaireViewModel.hasAddedNewQuestions = false;
//    DW.smsPreview();
//};

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

//DW.questionnaire_form = function (formElement) {
//    this.formElement = formElement;
//    this.errorAppender = new DW.error_appender("#message-label");
//};

//DW.questionnaire_form.prototype = {
//    isValid: function () {
////        return $(this.formElement).valid();
//        return true;
//    },
//    processValidation: function () {
//        if (!this.isValid()) {
//            this.errorAppender.appendError("This questionnaire has an error");
//            this.errorAppender.hide_message();
//            return false;
//        }
//        return true;
//    }
//};


$(document).ready(function () {
//    init_view_model();
//
//    ko.setTemplateEngine(new ko.nativeTemplateEngine());
//    ko.applyBindings(questionnaireViewModel);

    DW.charCount();
    $('#continue_project').live("click", DW.charCount);
    $('#question_form').live("keyup", DW.charCount);
    $('#question_form').live("click", DW.charCount);
//    $('#question_form').live("click", DW.smsPreview);
    $('.delete').live("click", DW.charCount);

//    $('input[name=text_length]:radio').change(
//        function () {
//            questionnaireViewModel.selectedQuestion().max_length("");
//        }
//    );
});
