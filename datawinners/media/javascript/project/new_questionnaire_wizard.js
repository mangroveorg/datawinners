
$(document).ready(function() {
    var activity_report_question = $('#question_title').val();
    DW.charCount();
    $('#question_form').live("keyup", DW.charCount);
    $('#question_form').live("click", DW.charCount);
    $('#question_form').live("click", DW.smsPreview);
    $('.delete').live("click", DW.charCount);

    $.validator.addMethod('spacerule', function(value, element, params) {
        var list = $.trim($('#' + element.id).val()).split(" ");
        if (list.length > 1) {
            return false;
        }
        return true;
    }, gettext("Space is not allowed in question code"));

    $.validator.addMethod('regexrule', function(value, element, params) {
        var text = $('#' + element.id).val();
        var re = new RegExp('^[A-Za-z0-9 ]+$');
        return re.test(text);
    }, gettext("Only letters and digits are valid"));

    $.validator.addMethod('naturalnumberrule', function(value, element, params) {
        var num = $('#' + element.id).val();
        return num != 0;
    }, gettext("Answer cannot be of length less than 1"));

    $("#question_form").validate({
        messages: {
            max_length:{
                digits: gettext("Please enter positive numbers only")
            }

        },
        rules: {
            question_title:{
                required: true
            },
            code:{
                required: true,
                spacerule: true,
                regexrule: true
            },
            type:{
                required: true
            },
            max_length:{
                digits:true
            },
            range_min:{
                number: true
            },
            range_max:{
                number: true
            },
            choice_text:{
                required: "#choice_text:visible"
            }
        },
        wrapper: "div",
        errorPlacement: function(error, element) {
            var offset = element.offset();
            error.insertAfter(element);
            error.addClass('error_arrow');  // add a class to the wrapper

        }

    });
    $("#learn_more").dialog({
        title: gettext("Learn More"),
        modal: true,
        autoOpen: false,
        width: 800
    });
   $("#delete_question").dialog({
        title: "Warning!!",
        modal: true,
        autoOpen: false,
        height: 275,
        width: 300,
        closeText: 'hide'
      }
   );
    $("#edit_question").dialog({
        title: "Warning!!",
        modal: true,
        autoOpen: false,
        height: 275,
        width: 300,
        closeText: 'hide'
      }
   );
    $("#questionnaire_code_change").dialog({
        title: "Warning!!",
        modal: true,
        autoOpen: false,
        height: 200,
        width: 300,
        closeText: 'hide'
      }
   );
    $('#questionnaire-code').blur(function(){
        if ($('#project-state').val() == "Test" && $('#saved-questionnaire-code').val() != $('#questionnaire-code').val()){
            $("#questionnaire_code_change").dialog("open");
        }
    });
    $("#ok_button").bind("click", function(){
         $("#questionnaire_code_change").dialog("close");
        return false;
    });



    $(".cancel_link").bind("click", function(){
         $("#questionnaire_code_change").dialog("close");
        var old_questionnaire_code = $('#saved-questionnaire-code').val();
        $('#questionnaire-code').val(old_questionnaire_code);
        return false;
    });

    $("#question_title").blur(function(){
        if (questionnaireViewModel.selectedQuestion().event_time_field_flag()){
            $("#edit_question").dialog("open");
        }
    });
    $("#yes_button").bind("click", function(){
        activity_report_question = $('#question_title').val();
        questionnaireViewModel.selectedQuestion().title($('#question_title').val());
        $("#edit_question").dialog("close");
        return true;
    });
    $("#no_link").bind("click", function(){
        questionnaireViewModel.selectedQuestion().title(activity_report_question);
        $("#question_title").val(activity_report_question);
        $("#edit_question").dialog("close");
        return false;
    });

    $(".learn_more_link").bind("click", function(){
       $("#learn_more").dialog("open");
    });

    $('input[name=text_length]:radio').change(
            function() {
                questionnaireViewModel.selectedQuestion().max_length("");
            }
    );
});
