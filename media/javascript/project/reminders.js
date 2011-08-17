$(document).ready(function(){
    $('.choice').change(function(){
        var is_reminder = $("input[@name='rdio']:checked").val();
        var project_id = $('#project_id').html();
        var url = '/project/reminderstatus/' + project_id+"/";
        $.post(url, {'is_reminder': is_reminder}, function(data){
            var message = "Reminders has been activated for the project"
            if(is_reminder === "False"){
                message = "Reminders has been de-activated for the project"
                $('#add_reminder').hide();
            }else{
                $('#add_reminder').show();
            }
            $('.success_message').show().html(message).fadeOut(10000);
        });
    });
});