$(document).ready(function () {
    $.ajaxSetup({ cache: false });
    var submissionTabs = new DW.SubmissionTabs();
    submissionTabs.updateActiveTabIndexBasedOnCurrentLocation();

    var _getTableActionsMenu = function(submissionTabs){
      var action_handler = new DW.SubmissionLogActionHandler(submissionTabs.getActiveTabName(), project_id);
      var table_actions_menu = submissionTabs.isTableEntriesCheckable() ? [
            {"label": "Edit", handler: action_handler['edit'], "allow_selection": "single"},
            {"label": "Delete", handler: action_handler['delete'], "allow_selection": "multiple"}
        ] : [];
      return table_actions_menu;
    };

    var _initTable = function(submissionTabs){
        var submission_table_options = {
            header_url: render_table_url + "/headers",
            table_source_url: render_table_url + '?type=' + submissionTabs.getActiveTabName(),
            row_check_box_visible: submissionTabs.isTableEntriesCheckable(),
            actions_menu: _getTableActionsMenu(submissionTabs),
            tabName: submissionTabs.getActiveTabName()
        };
        new DW.SubmissionLogTable(submission_table_options);
    };

    function _activate_tab(submissionTabs) {

        $('#search_box .dataTables_filter').remove();
        $('.submission_table').dataTable().fnDestroy();
        $('.submission_table').empty();
        DW.loading();
        _initTable(submissionTabs);
    };

    var _initialize_filters = function(){
        new DW.FilterSubmissionTableByDate().init();
        new DW.FilterSubmissionTableByDataSender().init();
        new DW.FilterSubmissionTableBySubject().init();
        new DW.FilterSubmissionTableBySearchText().init();
    };

    _initTable(submissionTabs);
    _initialize_filters();
    $('#page_hint_section').text($('#page_hint').find('>div:first').text())

    $("#tabs").tabs().find('>ul>li>a[href$=tab_template]').click(function () {
        var tab_index = $(this).parent().index();

        if (submissionTabs.getActiveTabIndex() === tab_index) {
            return;
        }
        submissionTabs.setActiveTabIndex(tab_index);
        _activate_tab(submissionTabs);
        return true;
    });

//    var all_tabs = $("#tabs").tabs().find('>ul>li>a[href$=tab_template]');
//    for (var i = 0; i < all_tabs.length; i++) {
//        if (i == submissionTabs.getActiveTabIndex()) {
//            $($(all_tabs[i]).parent()).addClass('ui-tabs-selected ui-state-active')
//        } else {
//            $($(all_tabs[i]).parent()).removeClass('ui-tabs-selected ui-state-active')
//        }
//
//    };

    $(".ui-corner-all").removeClass("ui-corner-all");
    $(".ui-corner-top").removeClass("ui-corner-top");


    $('.export_link').click(function () {
        var url = '/project/export/log' + '?type=' + submissionTabs.getActiveTabName();
        $('#export_form').appendJson({"search_filters":JSON.stringify(filter_as_json())}).attr('action', url).submit();
    });
});









