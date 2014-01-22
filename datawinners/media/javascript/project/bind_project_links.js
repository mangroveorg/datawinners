DW.bind_project_links = function () {
        if (!arguments[0]) { //the default behavior
            $(".sms_tester").unbind('click').click(function () {
                $(".sms_tester_form").removeClass("none");
                $(".sms_tester_form").dialog("open");
                return false;
            });

            $(".activate_project").unbind().bind("click", function () {
                $("#activate_project_block").dialog("open");
                $('#confirm').attr('href', $(this).attr('href'));
                return false;
            });

            $(".delete_project").unbind().bind("click", function () {
                $("#delete_project_block").dialog("open");
                var project_id = $(this).attr('href').split('/')[3];
                $('#confirm_delete').attr('href', $(this).attr('href'));
                $('#undo_delete_project').attr('href', '/project/undelete/' + project_id + "/");
                $('#undelete_project_section').show().hide(50000);
                return false;
            });

        } else { // bind to the data changed warning dialog
            $(".sms_tester, .activate_project, .delete_project, .printLink").unbind().bind("click", function () {
                DW.edit_submission_modified_data_handler.click_after_reload = $(this).attr("class");
                $("#cancel_submission_warning_message").dialog("open");
                return false;
            });
        }
    };

$(document).ready(function () {
    DW.bind_project_links();
});
