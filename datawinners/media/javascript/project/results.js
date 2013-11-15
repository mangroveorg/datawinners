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
                "concept": "Submission",
                "sAjaxSource": render_table_url,
                "sAjaxDataIdColIndex": 1,
                "remove_id": true,
                "bServerSide": true,
                "oLanguage": {
                    "sEmptyTable": $('.help_no_submissions').html()
                },
                "aaSorting": [
                    [ 2, "desc"]
                ],
                "aoColumnDefs": [
                    {"aTargets": [0], "sWidth": "30px"}
                ],
                "actionItems": [
                    {"label": "Edit", handler: action_handler['edit'], "allow_selection": "single"},
                    {"label": "Delete", handler: action_handler['delete'], "allow_selection": "multiple"}
                ],

                "fnDrawCallback": function (oSettings) {
                    var searchPlaceholderText = 'Enter any information you want to find';
                    $(this).find("thead input:checkbox").attr("disabled", oSettings.fnRecordsDisplay() == 0);
                    var nCols = $(this).find('thead>tr').children('th').length;
                    $(this).find('tbody').prepend('<tr style="display:none;"><td class ="table_message" colspan=' + nCols + '><div class="select_all_message"></div></td></tr>');
                    $(this).find(".select_all_message").data('all_selected', false);
                    $('#filters').append($('.dataTables_wrapper .dataTables_filter'))
                    $('#filters').find(".dataTables_filter input").attr('placeholder', gettext(searchPlaceholderText));
                }
            }

        );

    }
})
;



