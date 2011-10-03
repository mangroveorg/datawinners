$(document).ready(function() {
    $(".sms_tester_form").dialog({
        autoOpen: false,
        width: 1200,
        modal: true,
        title: 'SMS Tester',
        zIndex:1100,
        open: function(){
            $(".questionnaire_preview1").load(quessionarie_preview_link, function() {
                $('.printBtn').addClass('none');
                $('.displayText').hide();
            });
        }
    });
    $("#sms_tester").unbind('click').click(function() {
        $(".sms_tester_form").removeClass("none");
        $(".sms_tester_form").dialog("open");
    });


    $("#send_sms").unbind('click').click(function() {
        $.post('/submission', {'message':$("#id_message").val(), 'test_mode':true}, function(response) {
                    $("#id_message").val(response);
                });
    });
    $("#clear_sms").unbind('click').click(function() {
                    $("#id_message").val("");
    });
    
});