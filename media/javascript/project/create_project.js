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

    $($('input[name="frequency_enabled"]')).change(function() {
        if (this.value == "True") {
            $('#id_frequency_period').attr('disabled', false);
        }
        else {
            $('#id_frequency_period').attr('disabled', true);
        }
    });

    $($('input[name="activity_report"]')).change(function() {
        if (this.value == "no") {
            DW.init_view_model(subject_report_questions);
            $('#id_category').attr('disabled', false);
            $('#id_entity_type').attr('disabled', false);
        }
        else {
            DW.init_view_model(activity_report_questions);
            $('#id_category').attr('disabled', true);
            $('#id_entity_type').attr('disabled', true);
        }
    });

    $("#create_project_form").validate({
        rules: {
            name:{
                required: true
            }
        },
        wrapper: "span",
        errorPlacement: function(error, element) {
            offset = element.offset();
            error.insertAfter(element);
            error.addClass('errorlist');  // add a class to the wrapper

        }

    });


    $("#save_in_test_mode").click(function() {
        var data = JSON.stringify(ko.toJS(viewModel.questions()), null, 2);
        if ($.trim($("#questionnaire-code").val()) == "") {
            $("#questionnaire-code-error").html("<label class='error_message'> "+gettext("The Questionnaire code is required")+".</label>");
            return;
        }

        var list = $.trim($('#questionnaire-code').val()).split(" ");
        if (list.length > 1) {
            $("#questionnaire-code-error").html("<label class='error_message'> "+gettext("Space is not allowed in questionnaire code")+".</label>");
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
//            hide_message();
        }
        if (!is_questionnaire_form_valid || !is_project_form_valid){
            return;
        }

        var post_data = {'questionnaire-code':$('#questionnaire-code').val(),'question-set':data,'pid':$('#project-id').val()};

        $.post('#', post_data,
                function(response) {
                    $("#message-label").removeClass("none");
                    $("#message-label").removeClass("message-box");
                    $("#message-label").addClass("success-message-box");
                    $("#message-label").show().html("<label class='success'>" + gettext("The question has been saved.") + "</label");
                    hide_message();
                    redirect();
                }).error(function(e) {
                    $("#message-label").removeClass("none");
                    $("#message-label").removeClass("success-message-box");
                    $("#message-label").addClass("message-box");
                    $("#message-label").show().html("<label class='error_message'>" + e.responseText + "</label>");
                });
        return false;
    });
});