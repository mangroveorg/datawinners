DW.init_has_submission_delete_warning = function(){
    kwargs = {container: "#submission_exists",
        is_continue: !is_edit,
        title: gettext('Warning: Your Collected Data Will be Lost'),
        continue_handler: function(){
            question = questionnaireViewModel.selectedQuestion();
            questionnaireViewModel.removeQuestion(question);
        }
    }
    DW.has_submission_delete_warning = new DW.warning_dialog(kwargs);
}

DW.init_has_new_submission_delete_warning = function(){
    kwargs = {container: "#new_submission_exists",
        is_continue: !is_edit,
        title: gettext('Warning: Your Collected Data Will be Lost'),
        continue_handler: function(){
            $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
            DW.post_project_data('Test', function (response) {
                return '/project/overview/' + response.project_id;
            });
        }
    }
    DW.has_new_submission_delete_warning = new DW.warning_dialog(kwargs);
}


DW.init_delete_periodicity_question_warning = function(){
    kwargs = {container: "#delete_periodicity_question_warning",
        title: gettext('Warning: Your Collected Data Will be Lost'),
        width: 700,
        continue_handler: function(){
            question = questionnaireViewModel.selectedQuestion();
            questionnaireViewModel.removeQuestion(question);
        }
    }
    DW.delete_periodicity_question_warning = new DW.warning_dialog(kwargs);
}

var questionnaire_form = new DW.questionnaire_form('#question_form');

DW.post_project_data = function (state, function_to_construct_redirect_url_on_success) {
    var questionnaire_data = JSON.stringify(ko.toJS(questionnaireViewModel.questions()), null, 2);

    var basic_project_info = function () {
        var name = questionnaireViewModel.projectName();
        var language = questionnaireViewModel.language();
        var activity_report = 'yes';
        return JSON.stringify({'name':name, 'language':language, 'activity_report':activity_report});
    };

    var post_data = {'questionnaire-code':questionnaireViewModel.questionnaireCode(), 'question-set':questionnaire_data, 'profile_form':basic_project_info(),
        'project_state':state, 'csrfmiddlewaretoken':$('#question_form input[name=csrfmiddlewaretoken]').val()};

    $.post(post_url , post_data, function (response) {
        var responseJson = $.parseJSON(response);
        if (responseJson.success) {
            var redirect_url = function_to_construct_redirect_url_on_success(responseJson);
            var has_newly_added_question = questionnaireViewModel.has_newly_added_question();

            if (is_edit && (DW.questionnaire_was_changed || has_newly_added_question)){
                $.unblockUI();
                DW.inform_datasender_about_changes.redirect_url = redirect_url;
                DW.inform_datasender_about_changes.show_warning();
            } else {
                window.location.replace(redirect_url);
            }

        } else {
            $.unblockUI();
            $('#project-message-label').removeClass('none');
            $('#project-message-label').html("<label class='error_message'> " + gettext(responseJson.error_message) + "</label>");
        }
    });
};

DW.questionnaire_form_validate = function(){
    if(!DW.check_empty_questionnaire()) return false;

    return questionnaire_form.processValidation();
};

$(document).ready(function () {
    DW.option_warning_dialog.init();
    DW.init_delete_periodicity_question_warning();
    DW.init_empty_questionnaire_warning();
    if (is_edit){
        $('.report_type').find('input,select').prop('disabled',true);
        $("#add_subject_type").empty();
        DW.init_has_submission_delete_warning();
        DW.init_has_new_submission_delete_warning();
        DW.init_inform_datasender_about_changes();
    }
    var activity_report_question = $('#question_title').val();

    $('input[name="date_format"]').change(function () {
        if ($('input[name="date_format"]:checked').val() == 'mm.yyyy')
            DW.change_question_title_for_reporting_period('period', 'month');
        else
            DW.change_question_title_for_reporting_period('month', 'period');
    });


    $("#delete_question").dialog({
            title:gettext("Warning !!"),
            modal:true,
            autoOpen:false,
            height:275,
            width:300,
            closeText:'hide'
        }
    );

    $("#edit_question").dialog({
            title:gettext("Warning !!"),
            modal:true,
            autoOpen:false,
            height:275,
            width:300,
            closeText:'hide'
        }
    );

    $('#questionnaire-code').blur(function () {
        if ($('#project-state').val() == "Test" && $('#saved-questionnaire-code').val() != $('#questionnaire-code').val()) {
            DW.questionnaire_was_changed = true;
        }
    });

    $("#question_title").focus(function () {
        if (questionnaireViewModel.selectedQuestion().event_time_field_flag()) {
            $(this).addClass("blue_frame");
            $("#periode_green_message").show();
        }
    });

    $("#yes_button").bind("click", function () {
        activity_report_question = $('#question_title').val();
        questionnaireViewModel.selectedQuestion().title($('#question_title').val());
        $("#edit_question").dialog("close");
        return true;
    });

    $("#no_link").bind("click", function () {
        questionnaireViewModel.selectedQuestion().title(activity_report_question);
        $("#question_title").val(activity_report_question);
        $("#edit_question").dialog("close");
        return false;
    });

    $("#delete_periodicity_question_warning .show_link").bind("click", function () {
        var help_container = $("#delete_periodicity_question_warning > p.warning_message > span");
        help_container.fadeIn();
        $(this).hide();
    })

    $("#delete_periodicity_question_warning .hide_link").bind("click", function () {
        var help_container = $("#delete_periodicity_question_warning > p.warning_message > span");
        help_container.fadeOut();
        $("#delete_periodicity_question_warning .show_link").show();
    })

    $("#delete_periodicity_question_warning > p.warning_message > span").hide();
});
