DW.init_view_model = function (question_list) {
    questionnaireViewModel.questions([]);
    questionnaireViewModel.questions.valueHasMutated();
    var index = 0;
    for (index in question_list) {
        var questions = new DW.question(question_list[index]);
        questionnaireViewModel.loadQuestion(questions);
    }

    questionnaireViewModel.selectedQuestion(questionnaireViewModel.questions()[0]);
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
        $(this.questionnaireErrorCode).html("<label class='error_message'> " + gettext(errorText) + ".</label>");
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

    DW.charCount();
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

    $("#question_form").validate({
        messages: {
            max_length:{
                digits: gettext("Please enter positive numbers only")
            }
        },
        rules: {
            question_title:{
                required: true
            },
            code:{
                required: true,
                spacerule: true,
                regexrule: true
            },
            type:{
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

    $('input[name=type]:radio').change(
        function() {
            questionnaireViewModel.selectedQuestion().range_min("");
            questionnaireViewModel.selectedQuestion().range_max("");
            questionnaireViewModel.selectedQuestion().min_length(1);
            questionnaireViewModel.selectedQuestion().max_length("");
            questionnaireViewModel.selectedQuestion().length_limiter("length_unlimited");
            questionnaireViewModel.selectedQuestion().choices([
                {text:gettext("default"), val:'a'}
            ]);
            $('.error_arrow').remove();
            $('input[type=text]').removeClass('error');
        }
    );

    $('input[name=text_length]:radio').change(
        function() {
            questionnaireViewModel.selectedQuestion().max_length("");
        }
    );
});
