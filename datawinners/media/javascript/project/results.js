$(document).ready(function () {

    function load_table(tab_name) {
        var url = render_table_url + "/headers";
        $.ajax({
            url: url,
            data: {"type":tab_name },
            success: function(columnDef){
                init_submission_log_table(columnDef)
            },
            dataType: "json"
        });
    }

    function activate_tab(tab_name){

        $('#filters .dataTables_filter').remove();
        $('.submission_table').dataTable().fnDestroy();
        $('.submission_table').empty();
        load_table(tab_name);
    }

    var $actionBar = $(".action_bar");
    var $dataTable = $('.submission_table');
    var tab = ["all", "success", "error", "deleted"];
    var active_tab_index = 0;
    var match = window.location.pathname.match(/tab\/([^/]+)\//);
    if (match) active_tab_index = tab.indexOf(match[1]);

//    function TabOptions() {
//        var defaultOptions = {
//            "show_status": true,
//            "show_actions": true,
//            "show_deleting_check_box": true,
//            "show_reply_sms": false
//        };
//        this._options = {
//            'all': defaultOptions,
//            'success': $.extend({}, defaultOptions, {"show_status": false}),
//            'error': $.extend({}, defaultOptions, {"show_status": false, "show_reply_sms": true}),
//            'deleted': $.extend({}, defaultOptions, {"show_actions": false, "show_deleting_check_box": false})
//        }
//    }
//
//    TabOptions.prototype.show_status = function () {
//        return this._options[active_tab].show_status;
//    }
//
//    TabOptions.prototype.show_actions = function () {
//        return this._options[active_tab].show_actions;
//    }
//
//    TabOptions.prototype.show_deleting_check_box = function () {
//        return this._options[active_tab].show_deleting_check_box;
//    }
//
//    TabOptions.prototype.show_reply_sms = function () {
//        return this._options[active_tab].show_reply_sms;
//    }
//    var tabOptions = new TabOptions();

    $.ajaxSetup({ cache: false });
    load_table(tab[active_tab_index]);

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
        //window.location.href = window.location.pathname + '?type=' + tab[active_tab_index];
        activate_tab(tab[active_tab_index]);
        return true;
    });
    var all_tabs = $("#tabs").tabs().find('>ul>li>a[href$=tab_template]');
    for (var i = 0; i < all_tabs.length; i++) {
        if (i == active_tab_index) {
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

    function init_submission_log_table(cols) {

        var action_handler = new DW.SubmissionLogActionHandler(tab[active_tab_index], project_id);
         var url = render_table_url + '?type=' + tab[active_tab_index];

        $(".submission_table").dwTable({
                aoColumns: cols,
                "concept": "Submission",
                "sAjaxSource": url,
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
                "fnInitComplete":function(){
                    $('#filters').append($('.dataTables_wrapper .dataTables_filter'));
                },
                "fnHeaderCallback":function(head){}
            }

        );
        var display_check_box = active_tab_index != 3;
        $(".submission_table").dataTable().fnSetColumnVis(0,display_check_box)

    }


//    $(".export_link").click(function(){
//        DW.loading();
//        alert("export");
//        $('#export_form').appendJson(DW.get_criteria()).attr('action', url).submit();
//    })
})
;



