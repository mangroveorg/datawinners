$(document).ready(function(){
    var options = {
        bind_cancel_link_in_dialog:function () {
            $("#cancel_submission_warning_message #cancel_leave").bind('click', function () {
                $("#cancel_submission_warning_message").dialog("close");
            })
        },

        bind_yes_button_in_dialog:function () {
            $("#cancel_submission_warning_message .yes_button").bind('click', function (){
                if (DW.edit_submission_modified_data_handler.click_after_reload) {
                    $("#click_after_reload").val(DW.edit_submission_modified_data_handler.click_after_reload);
                    $("#redirect_url").val("");
                } else {
                    var redirect_url = (DW.edit_submission_modified_data_handler.redirect_url != "#") ? DW.edit_submission_modified_data_handler.redirect_url: "";
                    $("#redirect_url").val(redirect_url);
                    $("#click_after_reload").val();
                }

                $("form:first").trigger("submit");
            })
        },

        bind_no_button_in_dialog:function () {
            $("#cancel_submission_warning_message .no_button").bind('click', {self:this}, function (event) {
                var self = event.data.self;
                if (DW.edit_submission_modified_data_handler.click_after_reload) {
                    $("#cancel_submission_warning_message").dialog("close");
                    DW.edit_submission_modified_data_handler.discard_changes();
                    var click_after_reload = $("." + DW.edit_submission_modified_data_handler.click_after_reload);
                    DW.bind_project_links();
                    click_after_reload.trigger("click");
                    return false;
                } else
                    self.redirect();
            })
        }
    };

    DW.edit_submission_modified_data_handler = new DW.data_submission(options);

    if ($("#click_after_reload").val() && !DW.edit_submission_modified_data_handler.form_has_errors()) {
        var element = $("." + $("#click_after_reload").val());
        element.prop("href", "javascript:void(0);");
        element.trigger("click");
    }
});
