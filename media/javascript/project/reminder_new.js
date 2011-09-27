$(document).ready(function() {
    $("#new_reminder").dialog({
        autoOpen: false,
        modal: true,
        title: 'Reminder',
        width:450,
        beforeClose: function() {
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
            $('#days_before_deadline').val("")
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
            $('#days_after_deadline').val("")
        }
    });

    $('#message').keyup(function() {
        $('#message_count').html($('#message').val().length)
    });


    DW.makeJson = function(){
        reminder={}
        reminder['reminder_mode'] = $('input[name="reminder_mode"]:checked').val()
        if(reminder['reminder_mode'] == 'before_deadline'){
            reminder['days'] = $('#days_before_deadline').val()
        }
        else if(reminder['reminder_mode'] == 'after_deadline'){
            reminder['days'] = $('#days_after_deadline').val()
        }
        reminder['remind_to'] = $('input[name="target_datasenders"]').val()
        reminder['message'] = $('#message').val()
        return reminder
    }

    $('#new_reminder .button').bind("click", function() {
        $('#error').remove();
        if ($('#message').val().length == 0) {
            $('<div class="message-box" id="error">Message can not be blank</div>').insertBefore($('#new_reminder'))
        }
//        else if($('#new_reminder input:text:enabled').val().trim() == "" || isNaN($('#new_reminder input:text:enabled').val())){
//            $('<div class="message-box" id="error">The days can not be blank</div>').insertBefore($('#new_reminder'))
//        }
        else {
            var url = '/project/' + $('#project_id').val() + '/create_reminder/'
            $.post(url,{'reminder':JSON.stringify(DW.makeJson())},
                    function() {

                    }).success(function(data) {
                        window.location.href = data;
                    })
        }

    });

});