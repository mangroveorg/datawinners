DW.SubmissionLogActionHandler = function (submission_type, project_id) {
    this["delete"] = function (table, selected_ids, all_selected) {
        handle_submission_log_delete(table, selected_ids, all_selected, project_id, submission_type);
    };
    this["edit"] = function (table, selected_ids, all_selected) {
        handle_submission_log_edit(table, selected_ids, all_selected, submission_type, project_id);
    };
}

var filter_as_json = function () {
                var dateQuestionFilters = {
                };
                $(".date-question-filter").each(function(){
                    var dateFilter = $(this);
                    dateQuestionFilters[dateFilter.data('question-code')] = dateFilter.val();
                });

                var unique_id_filters = {};
                $(".subject_filter").each(function(){
                    var filter = $(this);
                    unique_id_filters[filter.attr('entity_type')] = filter.data('value');
                })
                return {"submissionDatePicker": $('#submissionDatePicker').val(),
                        "datasenderFilter": $("#data_sender_filter").data('ds_id'),
                        "reportingPeriodPicker": $('#reportingPeriodPicker').val(),
                        "search_text":$('#search_text').val(),
                        "dateQuestionFilters": dateQuestionFilters,
                        "uniqueIdFilters": unique_id_filters,
                        "duplicatesForFilter": $('#duplicates_for').val()
                };
};

function handle_submission_log_delete(table, selected_ids, all_selected, project_id, submission_type) {
    if (selected_ids.length == 0) {
        $("#message_text").html("<div class='message message-box'>" + gettext("Please select at least one undeleted record") + "</div>");
    } else {
        var options = {container: "#delete_submission_warning_dialog",
            continue_handler: function () {
                DW.loading();
                $.ajax({
                        type: 'POST',
                        url: '/project/' + project_id + '/submissions/delete/',
                        data: {
                            'id_list': JSON.stringify(selected_ids),
                            'all_selected': all_selected,
                            'search_filters':JSON.stringify(filter_as_json()),
                            'submission_type':submission_type
                        },
                        success: function (response) {
                            var data = JSON.parse(response);
                            $("#message_text").show();
                            if (data.success) {
                                $("#message_text").html("<div class='message success-box'>" + data.success_message + "</div>");
                                table.fnSettings()._iDisplayStart = get_updated_table_page_index(table,selected_ids,all_selected);
                                table.fnReloadAjax();
                            } else {
                                $("#message_text").html("<div class='error_message message-box'>" + data.error_message + "</div>");
                            }
                            $("#message_text .message").delay(5000).fadeOut();
                        },
                        error: function (e) {
                            $("#message_text").show();
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
            height: 170,
            width: 550
        };

        var delete_submission_warning_dialog = new DW.warning_dialog(options);
        delete_submission_warning_dialog.show_warning();
        delete_submission_warning_dialog.ids = selected_ids;
    }
    $("#message_text .message").delay(5000).fadeOut();
}

function handle_submission_log_edit(table, selected_ids, all_selected, active_tab_index, project_id) {
    survey_response_id = selected_ids[0];
    if (is_advance_questionnaire != 'True') {
        location.href = '/project/' + project_id + '/submissions/edit/' + survey_response_id + '/tab/' + active_tab_index
    } else {
        location.href = '/xlsform/' + project_id + '/web_submission/' + survey_response_id
    }
}

function removeRowsFromDataTable(ids) {
    $.each(ids, function (index, value) {
        $('.submission_table').dataTable().fnReloadAjax();
    });
}

