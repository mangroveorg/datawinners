DW.additional_column = function(){
    if($('#id_to').val() == "Additional"){
        $('#additional_people_column').removeClass('none');
    }
    else{
        $('#additional_people_column').addClass('none');
    }
}

$(document).ready(function(){
    DW.additional_column();
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
    $('#id_to').change(function(){
        DW.additional_column();
    });
    $('#clear_broadcast_sms_form').click(function(){
        $('#broadcast_sms_form')[0].reset();
        $('#messageCount').html($('#sms_content').val().length + "/160 ");
    });
});