$(document).ready(function() {
    var count = function () {
        var len = $(this).val().length;
        var limitation = 160;
        if (len > limitation){
            $(this).val($(this).val().substring(0, limitation));
        }
        $('#counter').html($(this).val().length);
    };
    $('#sms_content').bind('keyup keydown', count);
});

function clear_sms_content() {
    $("#sms_content").val('');
    $('#counter').html('0');
}
