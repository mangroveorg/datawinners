DW.bind_project_links = function () {
        if (!arguments[0]) { //the default behavior
            $(".sms_tester").unbind('click').click(function () {
                $(".sms_tester_form").removeClass("none");
                $(".sms_tester_form").dialog("open");
                return false;
            });

            $(".delete_project").unbind().bind("click", function () {
                $("#delete_project_block").dialog("open");
                $('#confirm_delete').attr('href', $(this).attr('href'));
                $('#undelete_project_section').show().hide(50000);
                return false;
            });

        }
    };

$(document).ready(function () {
    DW.bind_project_links();
});
