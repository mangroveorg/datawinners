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

function is_activity_report_selected() {
    return $('input[name="activity_report"]:checked').val() == "no";
}

function is_subject_selected() {
    return !is_activity_report_selected()
}

$(document).ready(function() {
    DW.init_view_model(existing_questions);
    ko.applyBindings(viewModel);
    DW.current_type = $('#id_entity_type').val();
    
    $($('input[name="frequency_enabled"]')).change(function() {
        if (this.value == "True") {
            $('#id_frequency_period').attr('disabled', false);
        }
        else {
            $('#id_frequency_period').attr('disabled', true);
        }
    });

    $("#subject_warning_message").dialog({
        title: gettext("Warning !!"),
        modal: true,
        autoOpen: false,
        height: 225,
        width: 325,
        closeText: 'hide'
    });

    $(".cancel_link").bind("click", function(){
          if (is_subject_selected())
          {
              if ($('#id_activity_report_0').attr('checked')){
                $('#id_activity_report_1').attr("checked",true);
              }
              else{
                $('#id_activity_report_0').attr("checked",true);
              }
          }
          else
          {
              $('#id_entity_type').val(DW.current_type);
          }
          $("#subject_warning_message").dialog("close");
    });

    $("#continue").bind("click", function(){
        if (is_activity_report_selected()) {
            DW.init_view_model(subject_report_questions);
            $('#id_entity_type').attr('disabled', false);
        }
        else {
            DW.init_view_model(activity_report_questions);
            $('#id_entity_type').attr('disabled', true);
        }
        DW.current_type = $('#id_entity_type').val();
        $("#subject_warning_message").dialog("close");
    });

    var entity_type = '';
    $('#id_entity_type').change(function() {
        entity_type = $('#id_entity_type').val();
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
                    $("#message-label").removeClass("none");
                    $("#message-label").removeClass("message-box");
                    $("#message-label").addClass("success-message-box");
                    $("#message-label").show().html("<label class='success'>" + gettext("The question has been saved.") + "</label");
                    hide_message();
                    window.location.href = $.parseJSON(response).redirect_url;
                }).error(function(e) {
                    $("#message-label").removeClass("none");
                    $("#message-label").removeClass("success-message-box");
                    $("#message-label").addClass("message-box");
                    $("#message-label").show().html("<label class='error_message'>" + e.responseText + "</label>");
                });
        return false;
    });

    function hide_message() {
        $('#message-label').delay(5000).fadeOut();
    }
});