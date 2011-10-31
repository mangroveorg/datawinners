
$(document).ready(function() {
    
    DW.charCount();
    $('#question_form').live("keyup", DW.charCount);
    $('#question_form').live("click", DW.charCount);
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
            offset = element.offset();
            error.insertAfter(element);
            error.addClass('error_arrow');  // add a class to the wrapper

        }

    });
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
    });

    $("#submit-button").click(function() {

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

        if (!$('#question_form').valid()) {
            $("#message-label").show().html("<label class='error_message'> " + gettext("This questionnaire has an error") + ".</label> ");
            hide_message();
            return;
        }

        var post_data = {'questionnaire-code':$('#questionnaire-code').val(),'question-set':data,'pid':$('#project-id').val()};

        $.post('/project/questionnaire/save', post_data,
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

    function hide_message() {
        $('#message-label').delay(5000).fadeOut();
    }

    $('input[name=type]:radio').change(
            function() {
                viewModel.selectedQuestion().range_min("");
                viewModel.selectedQuestion().range_max("");
                viewModel.selectedQuestion().min_length(1);
                viewModel.selectedQuestion().max_length("");
                viewModel.selectedQuestion().length_limiter("length_unlimited");
                viewModel.selectedQuestion().choices([
                    {text:gettext("default"), val:'a'}
                ]);
            }
    );
    $('input[name=text_length]:radio').change(
            function() {
                viewModel.selectedQuestion().max_length("");
            }
    );
});
