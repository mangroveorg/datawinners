$(document).ready(function () {
    new DW.InitializeEditDataSender().init();
});

DW.InitializeEditDataSender = function () {
    var options = {
        bind_all_links:function () {
            $("a#cancel").bind('click', {self:this}, function (event) {
                var that = event.data.self;
                that.redirect_url = $(this).attr("href");

                if (that.is_form_changed() || that.form_has_errors()) {
                    $("#cancel_submission_warning_message").dialog("open");
                    return false;
                } else
                    return that.redirect();
            });
        },

        bind_yes_button_in_dialog:function () {
            $("#cancel_submission_warning_message .yes_button").bind('click', function () {
                $("#cancel_submission_warning_message").dialog("close");
                window.location.href = $('.back-to-list').attr("href");
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