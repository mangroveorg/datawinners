$(document).ready(function() {
    $.validator.addMethod('regexrule', function(value, element) {
        var text = $('#' + element.id).val();
        var re = new RegExp('^[0-9 ,]+$');
        return re.test(text);
    }, gettext("Only letters are valid"));

    var defaults = $("#broadcast_sms_form").validate({
        rules: {
            text:{
                required:true
            }
        },
        wrapper: "div",
        errorPlacement: function(error, element) {
            var offset = element.offset();
            error.insertAfter(element);
            error.addClass('error_arrow');  // add a class to the wrapper
        }
    });

    DW.additional_column = function() {
        if ($('#id_to').val() == "Additional") {
            $('#additional_people_column').removeClass('none');
            $('#id_others').rules("add", "regexrule");
            $('#id_others').rules("add", "required");
        }
        else {
            $('#additional_people_column').addClass('none');
            $('#id_others').rules("remove", "regexrule");
            $('#id_others').rules("remove", "required");
        }
    };

    //every time page loads do these 2lines
    DW.additional_column();
    $('#messageCount').html($('#sms_content').val().length + "/160");

    $('#sms_content').keyup(function() {
        var message_length = $('#sms_content').val().length;
        if (message_length > 160) {
            $('#messageCount').css('color', 'red');
        } else {
            $('#messageCount').css('color', 'green');
        }
        $('#messageCount').html(message_length + "/160 ");
    });

    $('#id_to').change(function() {
        DW.additional_column();
    });

    $('#clear_broadcast_sms_form').click(function() {
        $('#broadcast_sms_form')[0].reset();
        $('#messageCount').html($('#sms_content').val().length + "/160 ");
    });
});