var questionnnaire_code= new DW.questionnaire_code("#questionnaire-code","#questionnaire-code-error");
var questionnaire_form =new DW.questionnaire_form('#question_form');

DW.hide_message = function() {
    $('#message-label').delay(5000).fadeOut();
};

DW.post_subject_data = function(){
    var questionnaire_data = JSON.stringify(ko.toJS(questionnaireViewModel.questions()), null, 2);
    var post_data = {'questionnaire-code':$('#questionnaire-code').val(),'question-set':questionnaire_data, 'entity-type':$('#entity-type').val(),
                    'saved-questionnaire-code':$('#saved-questionnaire-code').val(), 'csrfmiddlewaretoken':$('#question_form input[name=csrfmiddlewaretoken]').val()};
    $.post($('#post_url').val(), post_data, function(response){
        var responseJson = $.parseJSON(response);
        if (responseJson.success) {
            $("#message-label").removeClass("none");
            $("#message-label").removeClass("message-box");
            $("#message-label").addClass("success-message-box");
            $("#message-label").show().html("<label class='success'>" + gettext("The question has been saved.") + "</label");
            $("#saved-questionnaire-code").val(responseJson.form_code);
            questionnaireViewModel.set_all_questions_as_old_questions();
            questionnaireViewModel.selectedQuestion.valueHasMutated();
            questionnaireViewModel.questions.valueHasMutated();
            DW.hide_message();
        } else {
            $("#message-label").removeClass('none');
            $("#message-label").removeClass("success-message-box");
            $("#message-label").addClass("message-box");
            $("#message-label").html("<label class='error_message'> " + gettext(responseJson.error_message) + ".</label>");
        }
    });
};

$(document).ready(function() {
    $("#delete_warning").dialog({
        autoOpen: false,
        modal: true,
        title: gettext('Your Collected Data Will be Lost'),
        zIndex:200,
        width: 600
    });

    $("#submit-button").click(function() {
        if(questionnnaire_code.processValidation() && questionnaire_form.processValidation()){
            $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>' ,css: { width:'275px'}});
            DW.post_subject_data();
            $.unblockUI();
        }
    });

    $("#edit_warning").dialog({
        title: gettext("Shared Registration Form"),
        modal: true,
        autoOpen: true,
        width: 600,
        height: 150,
        position: ['center', 120]
    });

    $("#edit_ok").click(function() {
        $("#edit_warning").dialog("close");
    });
});
