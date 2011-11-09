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

    $($('input[name="activity_report"]')).change(function() {
        $("#subject_warning_message").dialog("open");
    });

    var basic_project_info=new DW.basic_project_info('#create_project_form');
    basic_project_info.createValidationRules();

    $('.create_project input:button').click(function() {
        var data = JSON.stringify(ko.toJS(viewModel.questions()), null, 2);

        var questionnnaire_code= new DW.questionnaire_code("#questionnaire-code","#questionnaire-code-error");
        if(!questionnnaire_code.processValidation()){
            return;
        }


        var is_project_form_valid = $('#create_project_form').valid();
        var is_questionnaire_form_valid = $('#question_form').valid();
        if (!is_questionnaire_form_valid){
            $("#message-label").show().html("<label class='error_message'> " + gettext("This questionnaire has an error") + ".</label> ");
            hide_message();
        }
        if (!is_questionnaire_form_valid || !is_project_form_valid){
            var location = "/project/wizard/create";
            $('.error_arrow:visible').closest('div.clear_both').attr('id','error');
            window.location.href = location + "#error";
            $('div.clear_both').removeAttr('id','error');
            return;
        }
        devices.enableSMSElement();
        var post_data = {'questionnaire-code':$('#questionnaire-code').val(),'question-set':data,'pid':$('#project-id').val(),
                        'profile_form': $('#create_project_form').serialize(), 'state':this.id};

        $.post('/project/save/', post_data,
                function(response) {
                    var responseJson = $.parseJSON(response);
                    if (responseJson.success) {
                        window.location.href = responseJson.redirect_url;
                    }
                    else {
                        if (responseJson.error == 'project') {
                            $("#message-label").addClass('none');
                            $("#project-message-label").removeClass('none');
                            $("#project-message-label").html("<label class='error_message'>" + responseJson.error_message + "</label>");
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

    function hide_message() {
        $('#message-label').delay(5000).fadeOut();
    }
});