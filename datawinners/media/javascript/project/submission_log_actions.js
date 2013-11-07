DW.SubmissionLogActionHandler = function (submission_type, project_id) {
    this["delete"] = function (table, selected_ids, all_selected) {
        handle_submission_log_delete(table, selected_ids, all_selected);
    };
    this["edit"] = function (table, selected_ids, all_selected) {
        handle_submission_log_edit(table, selected_ids, all_selected, submission_type, project_id);
    };
}

var options = {container: "#delete_submission_warning_dialog",
    continue_handler: function () {
        var selected_ids = this.ids;
        DW.loading();
        var project_id = project_id;
        $.ajax({
                type: 'POST',
                url: '/project/' + project_id + '/submissions/delete/',
                data: {
                    'id_list': JSON.stringify(selected_ids)
                },
                success: function (response) {
                    var data = JSON.parse(response);
                    if (data.success) {
                        $("#message_text").html("<div class='message success-box'>" + data.success_message + "</div>");
                        removeRowsFromDataTable(selected_ids);
                    } else {
                        $("#message_text").html("<div class='error_message message-box'>" + data.error_message + "</div>");
                    }
                    $("#message_text .message").delay(5000).fadeOut();
                },
                error: function (e) {
                    $("#message_text").html("<div class='error_message message-box'>" + e.responseText + "</div>");
                }
            }
        )
        ;

        return false;
    },
    title: gettext("Your Submission(s) will be deleted"),
    cancel_handler: function () {
    },
    height: 150,
    width: 550
};

var delete_submission_warning_dialog = new DW.warning_dialog(options);

function handle_submission_log_delete(table, selected_ids, all_selected) {
    if (selected_ids.length == 0) {
        $("#message_text").html("<div class='message message-box'>" + gettext("Please select at least one undeleted record") + "</div>");
    } else {
        delete_submission_warning_dialog.show_warning();
        delete_submission_warning_dialog.ids = selected_ids;
    }
    $("#message_text .message").delay(5000).fadeOut();
}

function handle_submission_log_edit(table, selected_ids, all_selected, active_tab_index, project_id) {
    survey_response_id = selected_ids[0];
//    if (survey_response_id.length > 1) {
//        return false;
//    } else {
    location.href = '/project/' + project_id + '/submissions/edit/' + survey_response_id + '/tab/' + active_tab_index
//    }
}
