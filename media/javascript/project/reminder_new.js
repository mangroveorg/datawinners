$(document).ready(function() {
    $("#new_reminder").dialog({
        autoOpen: false,
        modal: true,
        title: 'Reminder',
        width:450,
        beforeClose: function() {
            $('#error').remove();
            $('#reminder_id').val("");
            $('#message').val("");
            $('#message_count').html("0");
            $('[name="reminder_mode"]')[1].checked = true;
            $('[name="target_datasenders"]')[0].checked = true;
            $('#days_before_deadline').attr("disabled", "disabled")
            $('#days_after_deadline').attr("disabled", "disabled")
            $('#days_before_deadline').val("")
            $('#days_after_deadline').val("")

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
        reminder['id'] = $('#reminder_id').val()
        reminder['day'] = 0
        if(reminder['reminder_mode'] == 'before_deadline'){
            reminder['day'] = $('#days_before_deadline').val()
        }
        else if(reminder['reminder_mode'] == 'after_deadline'){
            reminder['day'] = $('#days_after_deadline').val()
        }
        reminder['remind_to'] = $('input[name="target_datasenders"]:checked').val()
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
            var url = '/project/create_reminder/' + $('#project_id').val() + '/'
            $.post(url,{'reminder':JSON.stringify(DW.makeJson())},
                    function() {

                    }).success(function(data) {
                        window.location.href = data;
                    })
        }
    });

    $('.edit_reminder').unbind("click").bind("click", function() {
        url = '/project/get_reminder/' + $('#project_id').val() + '/'
        console.log(url)
        $.getJSON(url,{'id':$(this)[0].name},function(data){
                    $('#message').val(data.message)
                    $('#message_count').html(data.message.length)

                    $('[name="reminder_mode"][value="'+data.reminder_mode+'"]')[0].checked = true;
                    if (data.reminder_mode != 'on_deadline'){
                        var id = '#days_' + data.reminder_mode
                        $(id).val(data.day)
                        $(id)[0].disabled =false
                    }

                    $('[name="target_datasenders"][value="'+data.remind_to+'"]')[0].checked = true;

                    $('#reminder_id').val(data.id)
                    $("#new_reminder").dialog("open");
                })
    });

});