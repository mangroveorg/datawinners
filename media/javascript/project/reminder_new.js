$(document).ready(function() {
    $('#message_count').html($('#message').val().length);
    $("#new_reminder").dialog({
        autoOpen: false,
        modal: true,
        title: 'Reminder',
        width:450,

        beforeClose: function() {
            $('#days_before_deadline').attr("disabled", "disabled");
            $('#days_after_deadline').attr("disabled", "disabled");
            $('#reminder_form')[0].reset();
            var validator = $('#reminder_form').validate();
            validator.resetForm();
            $('#message_count').html($('#message').val().length);
        }
    });

    $("#new_reminder .cancel_link").bind("click", function() {
        $("#new_reminder").dialog("close");
    });

    $('#add_reminder').unbind("click").bind("click", function() {
        $("#new_reminder").dialog("open");
    });

    $('input[name="reminder_mode"]').change(function() {
        $('#when_block label.error').each(function(){
            $(this).remove();
        })
        if ($(this).val() == 'before_deadline') {
            $('#days_before_deadline').attr("disabled", "");
            $('#days_after_deadline').attr("disabled", "disabled");
        }
        else if ($(this).val() == 'on_deadline') {
            $('#days_before_deadline').attr("disabled", "disabled");
            $('#days_after_deadline').attr("disabled", "disabled");
        }
        else if ($(this).val() == 'after_deadline') {
            $('#days_before_deadline').attr("disabled", "disabled");
            $('#days_after_deadline').attr("disabled", "");
        }
        $('#days_before_deadline').val("");
        $('#days_after_deadline').val("");
    });

    $('#message').keyup(function() {
        $('#message_count').html($('#message').val().length);
    });

    $('#new_reminder .button').bind("click", function() {
        var validator = $('#reminder_form').validate();
        if ($('#reminder_form').valid()) {
            $('#reminder_form').submit();
        }
        else {
            $('input.error').each(function() {
                $(this).removeClass('error');
            });
            $('#message_count').html($('#message').val().length);
        }
    });

    $('.edit_reminder').unbind("click").bind("click", function() {
        url = '/project/get_reminder/' + $('#project_id').val() + '/'
        $.getJSON(url, {'id':$(this)[0].name}, function(data) {
            $('#message').val(data.message);
            $('#message_count').html(data.message.length);

            $('[name="reminder_mode"][value="' + data.reminder_mode + '"]')[0].checked = true;
            if (data.reminder_mode != 'on_deadline') {
                var id = '#days_' + data.reminder_mode;
                $(id).val(data.day);
                $(id)[0].disabled = false;
            }

            $('[name="remind_to"][value="' + data.remind_to + '"]')[0].checked = true;

            $('#reminder_id').val(data.id);
            $("#new_reminder").dialog("open");
        })
    });

});