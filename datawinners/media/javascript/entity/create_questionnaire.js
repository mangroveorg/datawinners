DW.init_view_model = function (question_list) {
    if(is_edit){
        questionnaireViewModel.setQuestionnaireCreationType();
    }
    questionnaireViewModel.questions([]);
    questionnaireViewModel.questions.valueHasMutated();
    $(question_list).each(function(index, question){
        questionnaireViewModel.loadQuestion(new DW.question(question));
    });

    questionnaireViewModel.selectedQuestion(new DW.question({is_null_question: true}));
    questionnaireViewModel.selectedQuestion.valueHasMutated();
    DW.current_code = questionnaireViewModel.questions().length + 1; //This variable holds the next question code to be generated.
    questionnaireViewModel.hasAddedNewQuestions = false;
    DW.smsPreview();
};

DW.error_appender=function(element){
    this.element=element;
};

DW.error_appender.prototype={
   appendError:function(errorText){
       $(this.element).html("<label class='error_message'> " + gettext(errorText) + ".</label>");
   },
   hide_message:function () {
       $(this.element).delay(5000).fadeOut();
   }
};

DW.questionnaire_code=function(questionnaireCode,questionnaireErrorCode){
    this.questionnaireCode=questionnaireCode;
    this.questionnaireErrorCode=questionnaireErrorCode;
};


DW.questionnaire_code.prototype={
    processMandatory:function(){
        if (!this.isPresent()){
            this.appendError("The Questionnaire code is required");
            return false;
        }
        return true;
    },
    processSpaces:function(){
        var trimmed_value = $.trim($(this.questionnaireCode).val());
        var list = trimmed_value.split(" ");
        if(list.length>1){
            this.appendError("Space is not allowed in questionnaire code");
            return false;
        }

        $(this.questionnaireCode).val(trimmed_value);
        return true;
    },

    processLetterAndDigitValidation:function(){
        var code = $(this.questionnaireCode).val();
        var re = new RegExp('^[A-Za-z0-9 ]+$');
        if (!re.test(code)) {
            this.appendError("Only letters and digits are valid");
            return false;
        }
        return true;
    },

    isPresent:function(){
        return !($.trim($(this.questionnaireCode).val())=="");
    },

    appendError:function(errorText){
        $(this.questionnaireErrorCode).html("<label class='error'> " + gettext(errorText) + ".</label>");
    },

    processValidation:function(){
        if(!this.processMandatory()){
            return false;
        }

        if(!this.processSpaces()){
            return false;
        }

        //TODO The below expression needs to be simplified, I am not touching it because I am not sure if there is a Gotcha here!
        if(!this.processLetterAndDigitValidation()){
            return false;
        }
        return true;
    }
};

DW.questionnaire_form=function(formElement){
    this.formElement=formElement;
    this.errorAppender=new DW.error_appender("#message-label");
};

DW.questionnaire_form.prototype={
    isValid:function(){
        return $(this.formElement).valid();
    },
    processValidation:function(){
        if (!this.isValid()){
            this.errorAppender.appendError("This questionnaire has an error");
            this.errorAppender.hide_message();
            return false;
        }
        return true;
    }
};


$(document).ready(function() {
    DW.init_view_model(existing_questions);
    ko.applyBindings(questionnaireViewModel);
    questionnaireViewModel.routing.run();
    DW.charCount();
    $('#continue_project').live("click", DW.charCount);
    $('#question_form').live("keyup", DW.charCount);
    $('#question_form').live("click", DW.charCount);
    $('#question_form').live("click", DW.smsPreview);
    $('.delete').live("click", DW.charCount);

    $.validator.addMethod('spacerule', function(value, element, params) {
        var list = $.trim($('#' + element.id).val()).split(" ");
        if (list.length > 1) {
            return false;
        }
        return true;
    }, gettext("Space is not allowed in question code"));

    $.validator.addMethod('regexrule', function(value, element, params) {
        var text = $('#' + element.id).val();
        var re = new RegExp('^[A-Za-z0-9 ]+$');
        return re.test(text);
    }, gettext("Only letters and digits are valid"));

    $.validator.addMethod('naturalnumberrule', function(value, element, params) {
        var num = $('#' + element.id).val();
        return num != 0;
    }, gettext("Answer cannot be of length less than 1"));

    $.validator.addMethod('duplicate', function(value, element, params) {
        var val = $('#' + element.id).val();
        var valid = true;
        if (!questionnaireViewModel.hasAddedNewQuestions)
            return true;
        for(index in questionnaireViewModel.questions()){
            var question = questionnaireViewModel.questions()[index];
            if (question != questionnaireViewModel.selectedQuestion() && question.display().toLowerCase() == val.toLowerCase()){
                valid = false;
                break;
            }
        }
        return valid;
    }, gettext("This question is a duplicate"));

    $("#question_form").validate({
        messages: {
            max_length:{
                digits: gettext("Please enter positive numbers only")
            }
        },
        rules: {
            code:{
                required: true,
                spacerule: true,
                regexrule: true
            },
            'type[]':{
                required: true
            },
            max_length:{
                digits:true
            },
            range_min:{
                number: true
            },
            range_max:{
                number: true
            },
            choice_text:{
                required: "#choice_text:visible"
            }
        },
        wrapper: "div",
        errorPlacement: function(error, element) {
            var offset = element.offset();
            error.insertAfter(element);
            error.addClass('error_arrow');  // add a class to the wrapper
        }
    });

    $("#question_title").rules("add", {duplicate: true})

    $('input[name=text_length]:radio').change(
        function() {
            questionnaireViewModel.selectedQuestion().max_length("");
        }
    );
});
