$(document).ready(function () {
    $.ajaxSetup({ cache: false });
    var submissionTabs = new DW.SubmissionTabs();
    submissionTabs.setToSuccessTab();

    var _initTable = function(submissionTabs){
        var submission_table_options = {
            header_url: render_table_url + "/headers",
            table_source_url: render_table_url + '?type=' + submissionTabs.getActiveTabName(),
            row_check_box_visible: false,
            actions_menu: [],
            tabName: submissionTabs.getActiveTabName()
        };
        new DW.SubmissionLogTable(submission_table_options);
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

    $(".ui-corner-all").removeClass("ui-corner-all");
    $(".ui-corner-top").removeClass("ui-corner-top");


    $('.export_link').click(function () {
        var url = '/project/export/log' + '?type=' + submissionTabs.getActiveTabName();
        $('#export_form').appendJson({"search_filters":JSON.stringify(filter_as_json())}).attr('action', url).submit();
    });
})


