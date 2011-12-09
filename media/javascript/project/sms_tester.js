$(document).ready(function() {
    $(document).ajaxStop($.unblockUI);
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
    $(".sms_tester").unbind('click').click(function() {
        $(".sms_tester_form").removeClass("none");
        $(".sms_tester_form").dialog("open");
        return false;
    });

    $("#send_sms").unbind('click').click(function() {
        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>' ,css: { width:'275px', zIndex:1000000}});
        $.post('/submission', {'message':$("#id_message").val(), 'test_mode':true}, function(response) {
                    $("#id_message").val(response);
                });
    });
    $("#clear_sms").unbind('click').click(function() {
                    $("#id_message").val("");
    });
    
});