//DW.init_has_new_submission_delete_warning = function(){
//    kwargs = {container: "#new_submission_exists",
//        is_continue: !is_edit,
//        title: gettext('Warning: Your Collected Data Will be Lost'),
//        continue_handler: function(){
//            $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
//            DW.post_project_data('Test', function (response) {
//                return '/project/overview/' + response.project_id;
//            });
//        }
//    }
//    DW.has_new_submission_delete_warning = new DW.warning_dialog(kwargs);
//}


DW.init_delete_periodicity_question_warning = function(){
    var kwargs = {container: "#delete_periodicity_question_warning",
        title: gettext('Warning: Your Collected Data Will be Lost'),
        width: 700,
        continue_handler: function(){
            question = questionnaireViewModel.selectedQuestion();
            questionnaireViewModel.removeQuestion(question);
        }
    };
    DW.delete_periodicity_question_warning = new DW.warning_dialog(kwargs);
}

//var questionnaire_form = new DW.questionnaire_form('#question_form');

basic_project_info = function(){
        var name = questionnaireViewModel.projectName() || '';
        var language = questionnaireViewModel.language();
        var activity_report = 'yes';
        return JSON.stringify({'name':name, 'language':language, 'activity_report':activity_report});
};

DW.post_project_data = function (state, function_to_construct_redirect_url_on_success) {
    var questionnaire_data = JSON.stringify(ko.toJS(questionnaireViewModel.questions()), null, 2);

    var post_data = {
                      'questionnaire-code':questionnaireViewModel.questionnaireCode(),
                      'question-set':questionnaire_data,
                      'profile_form':basic_project_info(),
                      'project_state':state,
                      'csrfmiddlewaretoken':$('#question_form input[name=csrfmiddlewaretoken]').val()
                    };

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
            questionnaireViewModel.errorInResponse(true);
            questionnaireViewModel.responseErrorMsg(responseJson.error_message);
        }
    });
};

//Used in qns instruction and preview - replace and delete
//DW.questionnaire_form_validate = function(){
//   if (!questionnaireViewModel.validateForSubmission()) {
//        questionnaireViewModel.errors.showAllMessages();
//        questionnaireViewModel.questionnaireHasErrors(questionnaireViewModel.errors());
//        return false;
//    }
//
//    if(!DW.check_empty_questionnaire()) return false;
//
//    return questionnaire_form.processValidation();
//};

DW.controllers = {
    "questionnaire_load_controller":function () {
            questionnaireViewModel.questions([]);
            var project_details = DW.getTemplateData(this.params.template_id);

            questionnaireViewModel.projectName(project_details.project_name);
            questionnaireViewModel.language(project_details.project_language);
            questionnaireViewModel.questionnaireCode(project_details.questionnaire_code);
            DW.existing_questions = $.parseJSON(project_details.existing_questions);
            $($.parseJSON(project_details.existing_questions)).each(function (index, question) {
                questionnaireViewModel.loadQuestion(new DW.question(question));
            });
            questionnaireViewModel.showQuestionnaireForm(true);
            questionnaireHelperModel.showQuestionnaireCreationOptions(false);
    },
    "blank_questionnaire": function () {
            questionnaireViewModel.projectName('');
            questionnaireViewModel.questions([]);
            questionnaireViewModel.showQuestionnaireForm(true);
            questionnaireHelperModel.showQuestionnaireCreationOptions(false);
            questionnaireViewModel.questionnaireCode(questionnaire_code);
    }
};


DW.projectRouter = Sammy(function () {
        this.get('#:questionnaire/new', DW.controllers.blank_questionnaire);

        this.get('#:questionnaire/load/:template_id', DW.controllers.questionnaire_load_controller);

        this.get('project/wizard/create/$', function () {
            questionnaireViewModel.showQuestionnaireForm(false);
            questionnaireHelperModel.showQuestionnaireCreationOptions(true);
        });
});

function _initializeViewModel() {
    ko.setTemplateEngine(new ko.nativeTemplateEngine());
    ko.applyBindings(questionnaireViewModel, $('#create_questionnaire')[0]);
    ko.applyBindings(questionnaireHelperModel, $('#project_profile')[0]);
}

$(document).ready(function () {
    _initializeViewModel();
    DW.option_warning_dialog.init();
    DW.init_delete_periodicity_question_warning();
    DW.init_empty_questionnaire_warning();

    $("#save_and_create").bind("click", function () {
        if(!DW.check_empty_questionnaire())
            return false;

        if (questionnaireViewModel.validateForSubmission()) {
            $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
            DW.post_project_data('Test', function (response) {
                return '/project/overview/' + response.project_id;
            });
        }
    });

    DW.projectRouter.run();

//    if (is_edit){
//        $('.report_type').find('input,select').prop('disabled',true);
//        $("#add_subject_type").empty();
//        DW.init_has_submission_delete_warning();
//        DW.init_has_new_submission_delete_warning();
//        DW.init_inform_datasender_about_changes();
//    }
//    var activity_report_question = $('#question_title').val();

//    $('input[name="date_format"]').change(function () {
//        if ($('input[name="date_format"]:checked').val() == 'mm.yyyy')
//            DW.change_question_title_for_reporting_period('period', 'month');
//        else
//            DW.change_question_title_for_reporting_period('month', 'period');
//    });

//    $("#delete_question").dialog({
//            title:gettext("Warning !!"),
//            modal:true,
//            autoOpen:false,
//            height:275,
//            width:300,
//            closeText:'hide'
//        }
//    );

//    $("#edit_question").dialog({
//            title:gettext("Warning !!"),
//            modal:true,
//            autoOpen:false,
//            height:275,
//            width:300,
//            closeText:'hide'
//        }
//    );

//    $('#questionnaire-code').blur(function () {
//        if ($('#project-state').val() == "Test" && $('#saved-questionnaire-code').val() != $('#questionnaire-code').val()) {
//            DW.questionnaire_was_changed = true;
//        }
//    });

//    $("#question_title").focus(function () {
//        if (questionnaireViewModel.selectedQuestion().event_time_field_flag()) {
//            $(this).addClass("blue_frame");
//            $("#periode_green_message").show();
//        }
//    });

//    $("#yes_button").bind("click", function () {
//        activity_report_question = $('#question_title').val();
//        questionnaireViewModel.selectedQuestion().title($('#question_title').val());
//        $("#edit_question").dialog("close");
//        return true;
//    });

//    $("#no_link").bind("click", function () {
//        questionnaireViewModel.selectedQuestion().title(activity_report_question);
//        $("#question_title").val(activity_report_question);
//        $("#edit_question").dialog("close");
//        return false;
//    });



//    $("#delete_periodicity_question_warning .show_link").bind("click", function () {
//        var help_container = $("#delete_periodicity_question_warning > p.warning_message > span");
//        help_container.fadeIn();
//        $(this).hide();
//    })
//
//    $("#delete_periodicity_question_warning .hide_link").bind("click", function () {
//        var help_container = $("#delete_periodicity_question_warning > p.warning_message > span");
//        help_container.fadeOut();
//        $("#delete_periodicity_question_warning .show_link").show();
//    })
//
//    $("#delete_periodicity_question_warning > p.warning_message > span").hide();


});


