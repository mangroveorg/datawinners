$(document).ready(function () {
    var $actionBar = $(".action_bar");
    var $dataTable = $('.submission_table');
    var tab = ["all", "success", "error", "deleted"];
    var active_tab_index;

    function TabOptions() {
        var defaultOptions = {
            "show_status": true,
            "show_actions": true,
            "show_deleting_check_box": true,
            "show_reply_sms": false
        };
        this._options = {
            'all': defaultOptions,
            'success': $.extend({}, defaultOptions, {"show_status": false}),
            'error': $.extend({}, defaultOptions, {"show_status": false, "show_reply_sms": true}),
            'deleted': $.extend({}, defaultOptions, {"show_actions": false, "show_deleting_check_box": false})
        }
    }

    TabOptions.prototype.show_status = function () {
        return this._options[active_tab].show_status;
    }

    TabOptions.prototype.show_actions = function () {
        return this._options[active_tab].show_actions;
    }

    TabOptions.prototype.show_deleting_check_box = function () {
        return this._options[active_tab].show_deleting_check_box;
    }

    TabOptions.prototype.show_reply_sms = function () {
        return this._options[active_tab].show_reply_sms;
    }
    var tabOptions = new TabOptions();

    bind_data();
    $.ajaxSetup({ cache: false });

    var $no_submission_hint = $('.help_no_submissions');
    var $page_hint = $('#page_hint');
    var $page_hint_section = $('#page_hint_section')
    $page_hint_section.text($page_hint.find('>div:first').text())
    var message = gettext("No submissions available for this search. Try changing some of the filters.");
    var help_all_data_are_filtered = "<div class=\"help_accordion\" style=\"text-align: left;\">" + message + "</div>";

    $("#tabs").tabs().find('>ul>li>a[href$=tab_template]').click(function () {
        if ($dataTable.parents('.dataTables_wrapper').length >= 1) {
            DW.current_sort_order = $dataTable.dataTable().fnSettings().aaSorting;
        } else {
            DW.current_sort_order = [
                [2, "desc"]
            ];
        }
        var tab_index = $(this).parent().index();

        if (active_tab_index === tab_index) {
            return;
        }
        active_tab_index = tab_index;
        window.location.href = window.location.pathname + '?type=' + tab[active_tab_index];
    });
    var all_tabs = $("#tabs").tabs().find('>ul>li>a[href$=tab_template]');
    for (var i = 0; i < all_tabs.length; i++) {
        if (all_tabs[i].text.toLowerCase().indexOf(active_tab) != -1) {
            $($(all_tabs[i]).parent()).addClass('ui-tabs-selected ui-state-active')
        } else {
            $($(all_tabs[i]).parent()).removeClass('ui-tabs-selected ui-state-active')
        }

    }
    $(".ui-corner-all").removeClass("ui-corner-all");
    $(".ui-corner-top").removeClass("ui-corner-top");


    $('.export_link').click(function () {
        var url = '/project/export/log' + '?type=' + tab[active_tab_index];
        $('#export_form').appendJson(DW.get_criteria()).attr('action', url).submit();
    });


    function bind_data(data) {
        var active_tab_index = tab.indexOf(active_tab);
        var action_handler = new DW.SubmissionLogActionHandler(active_tab_index, project_id);

        $(".submission_table").dwTable({
            "concept": "submissions",
            "sAjaxSource": render_table_url,
            "sAjaxDataIdColIndex": 1,
            "remove_id": true,
            "bServerSide": true,
            "oLanguage": {
                "sEmptyTable": $('#no_registered_subject_message').clone(true, true).html() //todo check getEmptyTableText()
            },
            "aaSorting": [
                [ 2, "desc"]
            ],
            "actionItems": [
                {"label": "Edit", handler: action_handler['edit'], "allow_selection": "single"},
                {"label": "Delete", handler: action_handler['delete'], "allow_selection": "multiple"}
            ]
        });

    }

    function getEmptyTableText() {
        return isFiltering() ? help_all_data_are_filtered : $no_submission_hint.filter(':eq(' + active_tab_index + ')').html();
    }

    function isFiltering() {
        return _.any(_.values(DW.get_criteria()), function (v) {
            return !_.isUndefined(v) && !_.isEmpty($.trim(v))
        })
    }

    function wrap_table() {
        $(".submission_table").wrap("<div class='data_table' style='width:" + ($(window).width() - 65) + "px'/>");
    }

    function get_ids() {
        return $(".selected_submissions:checked").map(function (index, value) {
            return $(value).val();
        }).get();
    }

//    $("#master_checkbox").live("click", function () {
//        $(".selected_submissions").attr("checked", $(this).attr('checked') == "checked");
//        submissions_action_dropdown.update_edit_action();
//    });

//    $('.delete').click(function () {
//        var ids = get_ids();
//        if (ids.length == 0) {
//            $("#message_text").html("<div class='message message-box'>" + gettext("Please select at least one undeleted record") + "</div>");
//        } else {
//            delete_submission_warning_dialog.show_warning();
//            delete_submission_warning_dialog.ids = ids;
//        }
//        $("#message_text .message").delay(5000).fadeOut();
//    });
//
//    $('#edit').click(function () {
//        var survey_response_id = get_ids();
//        var project_id = $(location).attr('href').split('/')[4];
//
//        if (survey_response_id.length > 1) {
//            return false;
//        } else {
//            $(this).attr('href', '/project/' + project_id + '/submissions/edit/' + survey_response_id + '/tab/' + active_tab_index)
//        }
//    });

    function removeRowsFromDataTable(ids) {
        $.each(ids, function (index, value) {
            $dataTable.fnDeleteRow($(':checkbox[value=' + $.trim(value) + ']').parents('tr').get(0));
        });
        if ($("table.submission_table tbody tr").length) {
            $("#master_checkbox").attr("disabled", "disabled");
        }
    }

    function getColumnDefinition() {
        var columns = [

            {
                "sClass": "center",
                "sTitle": "<input type='checkbox'id='checkall-checkbox' class='selected_submissions'></input>",
                "fnRender": function (data) {
                    return '<input type="checkbox" value=' + data.aData[0] + ' />';
                },
                "bSortable": false,
                "aTargets": [0]
            }
        ];
        return columns;
    }

    var options = {container: "#delete_submission_warning_dialog",
        continue_handler: function () {
            var selected_ids = this.ids;
            DW.loading();
            var project_id = $(location).attr('href').split('/')[4];
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
    }
});

//    var delete_submission_warning_dialog = new DW.warning_dialog(options);

//    var kwargs = {
//        checkbox_locator: "#tabs table.submission_table input:checkbox",
//        data_locator: "#action_menu",
//        none_selected_locator: "#none-selected",
//        many_selected_msg: gettext("Please select 1 Submission only"),
//        check_single_checked_locator: "#tabs table.submission_table tbody input:checkbox[checked=checked]",
//        no_cb_checked_locator: "#tabs table.submission_table input:checkbox[checked=checked]",
//        checkall: "#master_checkbox"
//    }
//    var submissions_action_dropdown = new DW.action_dropdown(kwargs);
//
//    $(".selected_submissions").live("click", function () {
//        $("#master_checkbox").attr("checked", $(".selected_submissions").length == $(".selected_submissions:checkbox[checked]").length);
//    });
//})
//;
