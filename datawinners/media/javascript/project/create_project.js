DW.init_view_model = function (question_list) {

    viewModel.questions([]);
    viewModel.questions.valueHasMutated();
    var index = 0;
    for (index in question_list) {
        var questions = new DW.question(question_list[index]);
        viewModel.loadQuestion(questions);
    }

    viewModel.selectedQuestion(viewModel.questions()[0]);
    viewModel.selectedQuestion.valueHasMutated();
    DW.current_code = viewModel.questions().length + 1; //This variable holds the next question code to be generated.
    viewModel.hasAddedNewQuestions = false;
    DW.smsPreview();
};

DW.devices=function(smsElement){
  this.smsElement=smsElement;
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

DW.devices.prototype={
    disableSMSElement:function(){
        $(this.smsElement).attr("disabled",true);
    },
    enableSMSElement:function(){
        $(this.smsElement).attr("disabled",false);
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

DW.questionnaire_section = function(questionnaire_form_element){
    this.questionnaire_form_element = questionnaire_form_element;
};
DW.questionnaire_section.prototype = {
    show:function(){
        $(this.questionnaire_form_element).removeClass('none');
    },
    hide:function(){
        $(this.questionnaire_form_element).addClass('none');
    }

};
DW.basic_project_info=function(project_info_form_element){
    this.project_info_form_element=project_info_form_element;
};

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
                var offset = element.offset();
                error.insertAfter(element);
                error.addClass('error_arrow');  // add a class to the wrapper
            }
        });

    },
    isValid:function(){
        return $(this.project_info_form_element).valid();
    },
    values:function(){
        var name = $('#id_name').val();
        var goals = $('#id_goals').val();
        var language = $('input[name=language]:checked').val();
        var activity_report = $('input[name=activity_report]:checked').val();
        var entity_type = $('#id_entity_type').val();
        var devices = [];
        $('input[name=devices]:checked').each(function(){
            devices.push($(this).val());
        });
        return JSON.stringify({'name':name, 'goals':goals, 'language':language, 'activity_report': activity_report,
        'entity_type': entity_type, 'devices': devices});
    },
    show: function(){
        $(this.project_info_form_element).show();
    },
    hide: function(){
        $(this.project_info_form_element).hide();
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


var basic_project_info=new DW.basic_project_info('#create_project_form');
var questionnnaire_code= new DW.questionnaire_code("#questionnaire-code","#questionnaire-code-error");
var questionnaire_form =new DW.questionnaire_form('#question_form');
var questionnaire_section = new DW.questionnaire_section("#questionnaire");
var devices=new DW.devices("#id_devices_0");

DW.post_project_data = function(state, function_to_construct_redirect_url_on_success){
    var questionnaire_data = JSON.stringify(ko.toJS(viewModel.questions()), null, 2);
    var post_data = {'questionnaire-code':$('#questionnaire-code').val(),'question-set':questionnaire_data, 'profile_form': basic_project_info.values(),
        'project_state': state, 'csrfmiddlewaretoken':$('#create_project_form input[name=csrfmiddlewaretoken]').val()};
    $.post($('#post_url').val(), post_data, function(response){
        var responseJson = $.parseJSON(response);
        if (responseJson.success) {
            window.location.replace(function_to_construct_redirect_url_on_success(responseJson));
        } else {
            if (responseJson.error_in_project_section) {
                basic_project_info.show();
                questionnaire_section.hide();
            } else {
                basic_project_info.hide();
                questionnaire_section.show();
            }
            $('#project-message-label').removeClass('none');
            $('#project-message-label').html("<label class='error_message'> " + gettext(responseJson.error_message) + ".</label>");
        }
    });
};
$(document).ready(function() {
    DW.init_view_model(existing_questions);
    ko.applyBindings(viewModel);
    DW.subject_warning_dialog_module.init();

    devices.disableSMSElement();
    $('#id_entity_type').change(function() {
        if(is_edit || viewModel.hasAddedNewQuestions){
            $("#subject_warning_message").dialog("open");
        }else{
            DW.continue_flip();
        }
    });

    $('input[name="activity_report"]').change(function() {
        if(is_edit || viewModel.hasAddedNewQuestions){
            $("#subject_warning_message").dialog("open");
        }else{
            DW.continue_flip();
        }
    });

    basic_project_info.createValidationRules();

    $('#continue_project').click(function(){
        if (!basic_project_info.isValid()){
            $('html,body').animate({scrollTop:0}, 'slow');
            return false;
        }
        basic_project_info.hide();
        questionnaire_section.show();
    });

    $('#back_to_project').click(function(){
        basic_project_info.show();
        questionnaire_section.hide();
    });

    $('#save_and_create').click(function(){
        if(questionnnaire_code.processValidation() && questionnaire_form.processValidation()){
            $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>' ,css: { width:'275px'}});
            DW.post_project_data('Test', function(response){
                return '/project/overview/' + response.project_id;
            });
        }
        return false;
    });

    $('#save_as_draft').click(function(){
        if(questionnnaire_code.processValidation() && questionnaire_form.processValidation()){
            DW.post_project_data('Inactive', function(response){
                return '/project/';
            });
        }
        return false;

    });
});