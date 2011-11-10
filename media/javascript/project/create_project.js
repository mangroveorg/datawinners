DW.init_view_model = function (question_list) {

    viewModel.questions([]);
    viewModel.questions.valueHasMutated();
    DW.current_code = 2;

    for (index in question_list) {
        var questions = new DW.question(question_list[index]);
        viewModel.loadQuestion(questions);
    }

    viewModel.selectedQuestion(viewModel.questions()[0]);
    viewModel.selectedQuestion.valueHasMutated();
};

DW.devices=function(smsElement){
  this.smsElement=smsElement;
}

DW.error_appender=function(element){
    this.element=element;

}

DW.error_appender.prototype={
   appendError:function(errorText){
       $(this.element).html("<label class='error_message'> " + gettext(errorText) + ".</label>");

   },
   hide_message:function () {
    $(this.element).delay(5000).fadeOut();
}


}

DW.devices.prototype={
    disableSMSElement:function(){
        $(this.smsElement).attr("disabled",true);
    },
    enableSMSElement:function(){
        $(this.smsElement).attr("disabled",false);
    }
}

DW.questionnaire_code=function(questionnaireCode,questionnaireErrorCode){
    this.questionnaireCode=questionnaireCode;
    this.questionnaireErrorCode=questionnaireErrorCode;

}


DW.questionnaire_code.prototype={
    processMandatory:function(){
        if (!this.isPresent()){
            this.appendError("The Questionnaire code is required")
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

        if(!this.processLetterAndDigitValidation()){
            return false;
        }
        return true;

    }

}

DW.basic_project_info=function(project_info_form_element){
    this.project_info_form_element=project_info_form_element;
}

DW.basic_project_info.prototype={

    createValidationRules:function(){
        $(this.project_info_form_element).validate({
            rules: {
                name:{
                    required: true
                },
                entity_type:{
                    required:true
                }
            },
            wrapper: "div",
            errorPlacement: function(error, element) {
                offset = element.offset();
                error.insertAfter(element);
                error.addClass('error_arrow');  // add a class to the wrapper
            }
        });

    },
    isValid:function(){
        return $(this.project_info_form_element).valid();
    }

}

DW.questionnaire_form=function(formElement){
    this.formElement=formElement;
    this.errorAppender=new DW.error_appender("#message-label");

}

DW.questionnaire_form.prototype={
    isValid:function(){
        return $(this.formElement).valid();
    },
    processValidation:function(){
        if (!this.isValid()){
            this.error_appender.appendError("This questionnaire has an error");
            this.error_appender.hide_message();
        }

    }

}

$(document).ready(function() {
    DW.init_view_model(existing_questions);
    ko.applyBindings(viewModel);
    DW.subject_warning_dialog_module.init();
    var devices=new DW.devices("#id_devices_0");
    devices.disableSMSElement();
    $($('input[name="frequency_enabled"]')).change(function() {
        if (this.value == "True") {
            $('#id_frequency_period').attr('disabled', false);
        }
        else {
            $('#id_frequency_period').attr('disabled', true);
        }
    });

    $('#id_entity_type').change(function() {
        $("#subject_warning_message").dialog("open");
    });

    $('input[name="activity_report"]').change(function() {
        if(DW.current_code > 2){
            $("#subject_warning_message").dialog("open");
        }
        else{
            DW.continue_flip();
        }
    });

    var basic_project_info=new DW.basic_project_info('#create_project_form');
    basic_project_info.createValidationRules();

    $('.create_project input:button').click(function() {
        var data = JSON.stringify(ko.toJS(viewModel.questions()), null, 2);

        var questionnnaire_code= new DW.questionnaire_code("#questionnaire-code","#questionnaire-code-error");
        if(!questionnnaire_code.processValidation()){
            return;
        }
        var questionnaire_form =new DW.questionnaire_form('#question_form');

        questionnaire_form.processValidation();

        if (!basic_project_info.isValid()){
            var location = "/project/wizard/create";
            window.location.href = location + "#create_project_form";
            return;
        }
       if (!questionnaire_form.isValid()){
            var location = "/project/wizard/create";
            window.location.href = location + "#questionnaire";
            return;
        }
        devices.enableSMSElement();
        var post_data = {'questionnaire-code':$('#questionnaire-code').val(),'question-set':data,'pid':$('#project-id').val(),
                        'profile_form': $('#create_project_form').serialize(), 'state':this.id};

        var clickItemId = jQuery(this).attr("id");

        $.post('/project/save/', post_data,
                function(response) {
                    devices.disableSMSElement();
                    var responseJson = $.parseJSON(response);
                    if (responseJson.success) {
                        var location = "/project/wizard/create"
                        if (clickItemId == 'continue_project') {
                            $("#project-message-label").addClass('none');
                            $("#message-label").addClass('none');
                            $("#project_profile").addClass('none');
                            $("#questionnaire").removeClass('none');
                            window.location.href = location + "#header"
                        }
                        else if (clickItemId == 'back_to_project') {
                            $("#project-message-label").addClass('none');
                            $("#message-label").addClass('none');
                            $("#project_profile").removeClass('none');
                            $("#questionnaire").addClass('none');
                            window.location.href = location + "#header"
                        }
                        else {
                            window.location.href = responseJson.redirect_url;
                        }
                    }
                    else {
                        if (responseJson.error == 'project') {
                            $("#message-label").addClass('none');
                            $("#project-message-label").removeClass('none');
                            $("#project-message-label").html("<label class='error_message'>" + responseJson.error_message + "</label>");
                            var location = "/project/wizard/create";
                            window.location.href = location + "#project-message-label";
                        }
                        else {
                            $("#project-message-label").addClass('none');
                            $("#message-label").removeClass('none');
                            $("#message-label").html("<label class='error_message'>" + responseJson.error_message + "</label>");
                        }
                    }
                });
        return false;
    });
    

});