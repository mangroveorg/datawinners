DW.hide_message = function() {
    $('#message-label').delay(5000).fadeOut();
};

DW.post_subject_data = function(){
    var questionnaire_data = JSON.stringify(ko.toJS(questionnaireViewModel.questions()));
    var post_data = {
                        'questionnaire-code':questionnaireViewModel.questionnaireCode(),
                        'question-set':questionnaire_data,
                        'entity-type':$('#entity-type').val(),
                        'saved-questionnaire-code':$('#saved-questionnaire-code').val(),
                        'csrfmiddlewaretoken':$('#question_form input[name=csrfmiddlewaretoken]').val(),
                        'project-name': $('#project-name').val()
                    };
    $.post($('#post_url').val(), post_data, function(response){
        var responseJson = $.parseJSON(response);
        var flash_message = $("#message-label");
        if (responseJson.success) {
            flash_message.removeClass("none").removeClass("message-box").addClass("success-message-box")
            .html("<label class='success'>" + gettext("Your changes have been saved.") + "</label").show();
            $("#saved-questionnaire-code").val(responseJson.form_code);

            questionnaireViewModel.set_all_questions_as_old_questions();
            questionnaireViewModel.selectedQuestion.valueHasMutated();
            questionnaireViewModel.questions.valueHasMutated();
            flash_message[0].focus();
            flash_message[0].scrollIntoView();
            DW.hide_message();
        } else {
            flash_message.removeClass('none').removeClass("success-message-box").addClass("message-box")
                .html("<label class='error_message'> " + gettext(responseJson.error_message) + ".</label>").show();
            flash_message[0].scrollIntoView();
        }

        $("#submit-button").removeAttr('disabled');
    });
};


DW.init_has_submission_delete_warning_for_entity = function(){
    var kwargs = {container: "#submission_exists",
        continue_handler: function(){
            questionnaireViewModel.removeMarkedQuestion();
        },
        title: gettext('Warning: Your Collected Data Will be Lost')
    };
    DW.has_submission_delete_warning_for_entity = new DW.warning_dialog(kwargs);
}


function _initializeViewModel() {
    window.questionnaireViewModel = new SubjectQuestionnaireViewModel();
    $(existing_questions).each(function(index, question){
            questionnaireViewModel.loadQuestion(new DW.question(question));
    });
    questionnaireViewModel.questionnaireCode(questionnaire_code);
    questionnaireViewModel.projectName("subject questionnaire");
    questionnaireViewModel.hasExistingData = false;
    questionnaireViewModel.isEditMode = false;
    ko.setTemplateEngine(new ko.nativeTemplateEngine());
    ko.applyBindings(questionnaireViewModel);
}

$(document).ready(function() {
    _initializeViewModel();
    DW.questionnaire_was_changed = false;
    DW.init_inform_datasender_about_changes();
    $("#submit-button").click(function() {
        if(questionnaireViewModel.validateForSubmission()){
            $("#submit-button").attr('disabled','disabled');
            $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>' ,css: { width:'275px'}});
            DW.post_subject_data();
            $("#submit-button").removeAttr("disabled");
            $.unblockUI();
        }
    });

    $("#edit_warning").dialog({
        title: gettext("Shared Registration Form"),
        modal: true,
        autoOpen: true,
        width: 600,
        height: 170,
        position: ['center', 120]
    });

    $("#edit_ok").click(function() {
        $("#edit_warning").dialog("close");
    });
    
    DW.init_has_submission_delete_warning_for_entity();
});
