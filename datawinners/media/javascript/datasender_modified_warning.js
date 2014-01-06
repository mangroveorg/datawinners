$(document).ready(function () {
    new DW.InitializeEditDataSender().init();
});

DW.InitializeEditDataSender = function () {
    var options = {
        bind_all_links:function () {
            $("a#cancel").bind('click', {self:this}, function (event) {
                var that = event.data.self;
                if (that.is_form_changed() || that.form_has_errors()) {
                    $("#cancel_submission_warning_message").dialog({modal:true}).dialog("open");
                } else
                    $("#datasender-popup").dialog("close");
                    $("#datasender_table").dataTable().fnReloadAjax();
            });
        },

        bind_yes_button_in_dialog:function () {
            $("#cancel_submission_warning_message .yes_button").bind('click', {self:this}, function (event) {
                $("#cancel_submission_warning_message").dialog("close");
                $("#datasender-popup").dialog("close");
                if ($("#datasender_table").dataTable == undefined) {
                    return event.data.self.redirect();
                } else {
                    $("#datasender_table").dataTable().fnReloadAjax();
                }
            });
        }
    };

    this.init = function () {
        DW.data_submission_handler = new DW.data_submission(options);
        DW.bind_project_links = function () {
            return;
        }
    }
};