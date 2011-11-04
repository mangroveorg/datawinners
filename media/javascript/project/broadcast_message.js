$(document).ready(function(){
    $('#messageCount').html($('#id_text').val().length + "/160");
    $('#id_text').keyup(function(){
        var message_length = $('#id_text').val().length;
        if(message_length > 160){
            $('#messageCount').css('color', 'red');
        }else{
            $('#messageCount').css('color', 'green');
        }
        $('#messageCount').html(message_length + "/160 ");

    });
});