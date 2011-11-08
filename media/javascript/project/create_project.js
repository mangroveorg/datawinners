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


$(document).ready(function() {
    DW.init_view_model(existing_questions);
    ko.applyBindings(viewModel);
    DW.subject_warning_dialog_module.init();

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


    $("#create_project_form").validate({
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


    $('.right_aligned_button input:button').click(function() {
        var data = JSON.stringify(ko.toJS(viewModel.questions()), null, 2);
        if ($.trim($("#questionnaire-code").val()) == "") {
            $("#questionnaire-code-error").html("<label class='error_message'> " + gettext("The Questionnaire code is required") + ".</label>");
            return;
        }

        var list = $.trim($('#questionnaire-code').val()).split(" ");
        if (list.length > 1) {
            $("#questionnaire-code-error").html("<label class='error_message'> " + gettext("Space is not allowed in questionnaire code") + ".</label>");
            return;
        }
        else {
            $('#questionnaire-code').val($.trim($('#questionnaire-code').val()))
        }

        var text = $('#questionnaire-code').val();
        var re = new RegExp('^[A-Za-z0-9 ]+$');
        if (!re.test(text)) {
            $("#questionnaire-code-error").html("<label class='error_message'> " + gettext("Only letters and digits are valid") + ".</label>");
            return;
        }

        $("#questionnaire-code-error").html("");
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