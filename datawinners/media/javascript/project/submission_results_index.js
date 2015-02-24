$(document).ready(function () {
    $.ajaxSetup({ cache: false });
    var submissionTabs = new DW.SubmissionTabs();
    submissionTabs.updateActiveTabIndexBasedOnCurrentLocation();
    submissionTabs.initialize_tabs();

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
            tabName: submissionTabs.getActiveTabName(),
            sortCol : 2
        };
        new DW.SubmissionLogTable(submission_table_options);
    };

    function _activate_tab(submissionTabs) {

        $('#search_box .dataTables_filter').remove();
        $.each($(".repeat_ans").find('.repeat_qtn_label'), function (index, element) {

                $(element).removeData('tooltip').unbind();

        });
        $('.submission_table').dataTable().fnDestroy();
        $('.submission_table').empty();
        DW.loading();
        _initTable(submissionTabs);
    }

    var _initialize_filters = function(){
        new DW.DateFilter(_postFilterSelection).init();
        new DW.DataSenderFilter(_postFilterSelection).init();
        new DW.SubjectFilter(_postFilterSelection).init();
        new DW.SearchTextFilter(_postFilterSelection).init();
    };

    var _postFilterSelection = function(){
        $(".submission_table").dataTable().fnDraw();
    };

    _initTable(submissionTabs);
    _initialize_filters();
    $('#page_hint_section').text($('#page_hint').find('>div:first').text());

    var submissionLogExport = new DW.SubmissionLogExport();
    submissionLogExport.update_tab(submissionTabs.getActiveTabName());
    submissionLogExport.init();

    $("#tabs").tabs().find('>ul>li>a[href$=tab_template]').click(function () {
        var tab_index = $(this).parent().index();

        if (submissionTabs.getActiveTabIndex() === tab_index) {
            return;
        }
        submissionTabs.setActiveTabIndex(tab_index);
        submissionLogExport.update_tab(submissionTabs.getActiveTabName());
        _activate_tab(submissionTabs);
        return true;
    });

    $(".ui-corner-all").removeClass("ui-corner-all");
    $(".ui-corner-top").removeClass("ui-corner-top");

//    new DW.SubmissionLogExport().init(submissionTabs.getActiveTabName());
    new DW.FilterSection().init();
});









