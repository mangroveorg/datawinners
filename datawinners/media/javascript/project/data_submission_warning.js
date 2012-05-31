$(function () {
    DW.data_submission.init();
});


DW.data_submission = {
    init:function () {
        DW.data_submission.init_warning_dialog();
        DW.data_submission.initial_form_values();
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

    initial_form_values:function () {
        $('form :input').each(function () {
            $(this).data('initialValue', $(this).val());
        });
    },

    bind_cancel_link:function () {
        var that = this;
        $("#cancel").bind('click', function () {
            if (that.is_form_changed())
                $("#cancel_submission_warning_message").dialog("open");
            else
                that.go_to_project_list();
        });
    },

    is_form_changed:function () {
        var is_change = false;
        $('form :input').each(function () {
            if ($(this).data("initialValue") !== $(this).val()) {
                is_change = true;
            }
        });
        return is_change;
    },

    bind_cancel_link_in_dialog:function () {
        $(".cancel_button").bind('click', function () {
            $("#cancel_submission_warning_message").dialog("close");
        })
    },

    bind_confirm_link_in_dialog:function () {
        var that = this;
        $("#confirm").bind('click', function () {
            that.go_to_project_list();
        })
    },

    go_to_project_list:function () {
        window.location.href = $(".back-to-project-list").attr("href");
    }
};