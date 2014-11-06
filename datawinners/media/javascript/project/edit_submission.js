$(document).ready(function(){
    var options = {
        ignore_links: "#edit_ds_popup .cancel_link, #save_ds",

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
                    $("#click_after_reload").val(DW.edit_submission_modified_data_handler.click_after_reload);
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

    if ($(".cancel-editing-link").length) {
        DW.edit_submission_modified_data_handler = new DW.data_submission(options);
    }

    if ($("#click_after_reload").val() && !DW.edit_submission_modified_data_handler.form_has_errors()) {
        var element = $("." + $("#click_after_reload").val());
        element.trigger("click");
    }

    var popup = $("#edit_ds_popup").dialog({
        title: gettext("Change Data Sender"),
        modal: true,
        autoOpen: false,
        height: 'auto',
        width: 550
    });
    popup.parent().appendTo($("#edit_submission_form"));

    var change_datasender_link = $("#change_ds_link");

    change_datasender_link.on("click", function(){
        DW.trackEvent('edit-submission', 'change-datasender');
        $("#edit_ds_popup").dialog("open");
    });

    var change_ds_dropdown = $("#id_dsid");

    $("#edit_ds_popup .cancel_link").bind("click", function(){
        datasender_id = $(".datasender").text();
        change_ds_dropdown.val(datasender_id);
        $("#edit_ds_popup").dialog("close");
    });
    $("#save_ds").bind("click", function(){
        selected_ds = $('#id_dsid option:selected').text();
        selected_ds_split = selected_ds.split("  ");
        datasender_name = selected_ds_split[0].replace(/^\w/, function($0) { return $0; });
        datasender_id = selected_ds_split[1].replace(')','').replace('(','')

        $(".datasender").text(datasender_id);
        $(".ds_id").text(datasender_name);
        $(".datasender_error_message").addClass("none");
        $("#edit_ds_popup").dialog("close");
    });

    change_ds_dropdown.on('change', function(){
       DW.trackEvent('edit-submission', 'choose-datasender-from-list');
    });
    

});
