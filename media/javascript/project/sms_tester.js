$(document).ready(function() {
    $(".sms_tester_form").dialog({
        autoOpen: false,
        width: 600,
        modal: true,
        title: 'SMS Tester'
    });
    $("#sms_tester").unbind('click').click(function() {
        $(".sms_tester_form").dialog("open");
    });

    $("#send_sms").unbind('click').click(function() {
        $.post('/submission', {'message':$("#id_message").val(), 'test_mode':true}, function(response) {
                    $("#id_message").val(response);
                });
    });
});