$(document).ready(function() {
    $("#new_reminder").dialog({
        autoOpen: false,
        modal: true,
        title: 'Reminder',
        width:500,
        beforeClose: function(){
            $('#error').remove();
        }
    });

    $("#new_reminder .cancel_link").bind("click", function() {
        $("#new_reminder").dialog("close");
    });

    $('#add_reminder').unbind("click").bind("click", function() {
        $("#new_reminder").dialog("open");
    });

    $('input[name="reminder_mode"]').change(function() {
        if ($(this).val() == 'before_deadline') {
            $('#days_before_deadline').attr("disabled", "")
            $('#days_after_deadline').attr("disabled", "disabled")
            $('#days_before_deadline').val(0)
            $('#days_after_deadline').val("")
        }
        else if ($(this).val() == 'on_deadline') {
            $('#days_before_deadline').attr("disabled", "disabled")
            $('#days_after_deadline').attr("disabled", "disabled")
            $('#days_before_deadline').val("")
            $('#days_after_deadline').val("")

        }
        else if ($(this).val() == 'after_deadline') {
            $('#days_before_deadline').attr("disabled", "disabled")
            $('#days_after_deadline').attr("disabled", "")
            $('#days_before_deadline').val("")
            $('#days_after_deadline').val(0)
        }
    });

    $('#message').keyup(function() {
        $('#message_count').html($('#message').val().length)
    });

    $('#new_reminder .button').bind("click", function() {
        $('#error').remove();
        if ($('#message').val().length == 0) {
            $('<div class="message-box" id="error">Message can not be blank</div>').insertBefore($('#new_reminder'))
        }
    });

//    function DW.makeJson(){
//        reminder={}
//        reminder['reminder_mode'] = $('input[name="reminder_mode"]').val()
//        if(reminder['reminder_mode'] == 'before_deadline'){
//            reminder['days'] = $('#days_before_deadline')
//        }
//        else if(reminder['reminder_mode'] == 'after_deadline'){
//            reminder['days'] = $('#days_after_deadline')
//        }
//        reminder['remind_to'] = $('input[name="target_datasenders"]').val()
//        reminder['message'] = $('#message')
//        return reminder
//    }

});