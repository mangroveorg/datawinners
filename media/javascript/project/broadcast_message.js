$(document).ready(function(){
    $('#messageCount').html($('#sms_content').val().length + "/160");
    $('#sms_content').keyup(function(){
        var message_length = $('#sms_content').val().length;
        if(message_length > 160){
            $('#messageCount').css('color', 'red');
        }else{
            $('#messageCount').css('color', 'green');
        }
        $('#messageCount').html(message_length + "/160 ");

    });
});