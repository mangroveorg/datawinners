$(function () {
    DW.data_submission.init();
});


DW.data_submission = {
    init:function () {
        DW.data_submission.init_warning_dialog();
        DW.data_submission.bind_cancel_link();
        DW.data_submission.bind_cancel_link_in_dialog();
        DW.data_submission.bind_confirm_link_in_dialog();
    },

    init_warning_dialog:function () {
        $("#cancel_submission_warning_message").dialog({
            title:gettext("Warning"),
            modal:true,
            autoOpen:false,
            height:180,
            width:400,
            closeText:'hide'
        });
    },

    bind_cancel_link:function () {
        $("#cancel").bind('click', function () {
            $("#cancel_submission_warning_message").dialog("open");
        });
    },

    bind_cancel_link_in_dialog:function () {
        $(".cancel_button").bind('click', function() {
            $("#cancel_submission_warning_message").dialog("close");
        })
    },

    bind_confirm_link_in_dialog:function() {
        $("#confirm").bind('click', function() {
            window.location.href = $(".back-to-project-list").attr("href");
        })
    }
};