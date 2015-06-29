DW.bind_project_links = function () {
        if (!arguments[0]) { //the default behavior

            $(".sms_tester").on('click', function () {
                $(".sms_tester_form").removeClass("none");
                $(".sms_tester_form").dialog("open");
                return false;
            });

            $(".delete_project").on("click", function () {
                var is_poll = $(this).data("is_poll");
                if (is_poll == true) {
                    $("#delete_poll_block").dialog("open");
                    $('#confirm_delete_poll').attr('href', $(this).attr('href'));
                }
                else {
                    $("#delete_project_block").dialog("open");
                    $('#confirm_delete').attr('href', $(this).attr('href'));
                }
                $('#undelete_project_section').show().hide(50000);
                return false;
            });

            $(".change_setting").on("click", function () {
                DW.trackEvent('datasender-group', 'change-authorization');
                $("#change_ds_setting").dialog("open");
                $('#save_ds_setting').attr('href', $(this).attr('href'));
                $("#save_ds_setting").focus();
                return false;
            });

        }
    };

$(document).ready(function () {
    DW.bind_project_links();
});
