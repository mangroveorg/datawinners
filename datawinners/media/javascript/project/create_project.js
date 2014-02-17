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

DW.devices = function (smsElement) {
    this.smsElement = smsElement;
};

DW.devices.prototype = {
    disableSMSElement:function () {
        $(this.smsElement).attr("disabled", true);
    },
    enableSMSElement:function () {
        $(this.smsElement).attr("disabled", false);
    }
};

DW.questionnaire_section = function (questionnaire_form_element) {
    this.questionnaire_form_element = questionnaire_form_element;
};

DW.questionnaire_section.prototype = {
    show:function () {
        $(this.questionnaire_form_element).removeClass('none');
    },
    hide:function () {
        $(this.questionnaire_form_element).addClass('none');
    }

};

DW.basic_project_info = function (project_info_form_element) {
    this.project_info_form_element = project_info_form_element;
};

DW.basic_project_info.prototype = {
    createValidationRules:function () {
        $(this.project_info_form_element).validate({
            rules:{
                name:{
                    required:true
                },
                entity_type:{
                    required:true
                },
                goals:{
                    maxlength: 300
                }
            },
            wrapper:"div",
            errorPlacement:function (error, element) {
                var offset = element.offset();
                error.insertAfter(element);
                error.addClass('error_arrow');  // add a class to the wrapper
            },
            invalidHandler: function(form, validator) {
                var errors = validator.numberOfInvalids();
                if (errors) {
                    validator.errorList[0].element.focus();
                }
            }
        });
    },
    isValid:function () {
        return $(this.project_info_form_element).valid();
    },
    values:function () {
        var name = $('#id_name').val();
        var goals = $('#id_goals').val();
        var language = $('input[name=language]:checked').val();
        var activity_report = $('input[name=activity_report]:checked').val();
        var entity_type = $('#id_entity_type').val();
        var devices = [];
        $('input[name=devices]:checked').each(function () {
            devices.push($(this).val());
        });
        return JSON.stringify({'name':name, 'goals':goals, 'language':language, 'activity_report':activity_report,
            'entity_type':entity_type, 'devices':devices});
    },
    show:function () {
        $(this.project_info_form_element).show();
    },
    hide:function () {
        $(this.project_info_form_element).hide();
    },
    show_subject_link:function () {
        $('#add_subject_type').show()
    },
    hide_subject_link:function () {
        $("#add_subject_type").accordion("activate", -1)
        $('#add_subject_type').hide()
    }
};

var basic_project_info = new DW.basic_project_info('#create_project_form');
var questionnnaire_code = new DW.questionnaire_code("#questionnaire-code", "#questionnaire-code-error");
var questionnaire_form = new DW.questionnaire_form('#question_form');
var questionnaire_section = new DW.questionnaire_section("#questionnaire");
var devices = new DW.devices("#id_devices_0");

DW.post_project_data = function (state, function_to_construct_redirect_url_on_success) {
    var questionnaire_data = JSON.stringify(ko.toJS(questionnaireViewModel.questions()), null, 2);
    var post_data = {'questionnaire-code':$('#questionnaire-code').val(), 'question-set':questionnaire_data, 'profile_form':basic_project_info.values(),
        'project_state':state, 'csrfmiddlewaretoken':$('#create_project_form input[name=csrfmiddlewaretoken]').val()};
    $.post($('#post_url').val(), post_data, function (response) {
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
            if (responseJson.error_in_project_section) {
                basic_project_info.show();
                questionnaire_section.hide();
            } else {
                basic_project_info.hide();
                questionnaire_section.show();
            }
            $('#project-message-label').removeClass('none');
            $('#project-message-label').html("<label class='error_message'> " + gettext(responseJson.error_message) + "</label>");
        }
    });
};

DW.questionnaire_form_validate = function(){
    if(!DW.check_empty_questionnaire()) return false;

    return questionnnaire_code.processValidation() && questionnaire_form.processValidation();
};

$(document).ready(function () {
    DW.subject_warning_dialog_module.init();
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

    basic_project_info.hide_subject_link();
    devices.disableSMSElement();

    $('#id_entity_type').change(function () {
        if (is_edit || questionnaireViewModel.hasAddedNewQuestions) {
            $("#changed").html(gettext("subject type"));
            $("#subject_warning_message").dialog("open");
        } else {
            DW.continue_flip();
        }
    });

    $('input[name="activity_report"]').change(function () {
        if (is_edit || questionnaireViewModel.hasAddedNewQuestions) {
            $("#changed").html(gettext("project type"));
            $("#subject_warning_message").dialog("open");
        } else {
            DW.continue_flip();
        }
    });

    $('input[name="date_format"]').change(function () {
        if ($('input[name="date_format"]:checked').val() == 'mm.yyyy')
            DW.change_question_title_for_reporting_period('period', 'month');
        else
            DW.change_question_title_for_reporting_period('month', 'period');
    });

    basic_project_info.createValidationRules();

    if ($("#id_activity_report_1").attr("checked")) {
        $('#add_subject_type').show();
    }

    $('#continue_project').click(function () {
        if (!basic_project_info.isValid()) {
            $('html,body').animate({scrollTop:480}, 'slow');
            return false;
        }
        $("#project-message-label").addClass('none');
        basic_project_info.hide();
        questionnaire_section.show();
    });

    $('#back_to_project').click(function () {
        basic_project_info.show();
        questionnaire_section.hide();
    });

    $('#save_and_create').click(function () {

        if (DW.questionnaire_form_validate()) {
            if(DW.has_questions_changed(existing_questions)){
                DW.questionnaire_was_changed = true;
            }
            if( is_edit && questionnaireViewModel.hasDeletedOldQuestion  && !DW.has_submission_delete_warning.is_continue && DW.questionnaire_has_submission()){
                DW.has_new_submission_delete_warning.show_warning();
            } else {
                $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
                DW.post_project_data('Test', function (response) {
                    return '/project/overview/' + response.project_id;
                });
            }
        }
        return false;
    });

    $('#save_as_draft').click(function () {
        if (DW.questionnaire_form_validate()) {
            DW.post_project_data('Inactive', function (response) {
                return '/project/';
            });
        }
        return false;
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
