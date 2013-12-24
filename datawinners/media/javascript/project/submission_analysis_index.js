$(function () {
    $.ajaxSetup({ cache: false });
    $('#page_hint_section').text($('#page_hint').find('>div:first').text());
    $(".ui-corner-all").removeClass("ui-corner-all");
    $(".ui-corner-top").removeClass("ui-corner-top");

    new DW.SubmissionAnalysisView().init();
});

DW.SubmissionAnalysisView = function(){

    var self = this;
    var tableViewOption = $("#table_view_option");
    var chartViewOption = $("#chart_view_option");
    var tableView = $("#submission_logs");
    var chartView = $('#chart_ol');
    var isChartViewShown = false;
    var submissionTabs = new DW.SubmissionTabs();
    var chartGenerator = new DW.SubmissionAnalysisChartGenerator();

    self.init = function(){
       submissionTabs.setToAnalysisTab();
       _initializeSubmissionTable(submissionTabs);
       _initializeSubmissionTableFilters();
       _initializeEvents();
       _initializeExport();
    };

    var _initializeExport = function(){
        new DW.SubmissionLogExport().init(submissionTabs.getActiveTabName());
    };

    var _initializeSubmissionTable = function(submissionTabs){
        var submission_table_options = {
            header_url: render_table_url + "/headers",
            table_source_url: render_table_url + '?type=' + submissionTabs.getActiveTabName(),
            row_check_box_visible: false,
            actions_menu: [],
            tabName: submissionTabs.getActiveTabName()
        };
        new DW.SubmissionLogTable(submission_table_options);
    };

    var _initializeSubmissionTableFilters = function() {
        new DW.FilterSubmissionTableByDate().init();
        new DW.FilterSubmissionTableByDataSender().init();
        new DW.FilterSubmissionTableBySubject().init();
        new DW.FilterSubmissionTableBySearchText().init();
    };

    var _initializeSubmissionChartFilters = function(){
        new DW.FilterSubmissionChartsBySearchText().init();
    };

    var _initializeEvents = function(){
        tableViewOption.on("click", _showDataTableView);
        chartViewOption.on("click", _showChartView);
    };

    var _showDataTableView = function () {
        if (!isChartViewShown)
            return;
        tableViewOption.addClass("active");
        chartViewOption.removeClass("active-right");
        _reinitializeSubmissionTableView();
        _initializeSubmissionTable(submissionTabs);
        chartView.hide();
        isChartViewShown = false;
    };

    var _reinitializeSubmissionTableView = function(){
        tableView.show();
        $('.submission_table').dataTable().fnDestroy();
        $('.submission_table').empty();
        $('#chart_info').empty();
        $('#chart_info_2').empty();
        chartView.empty();
    };

    var _showChartView = function () {
        if (isChartViewShown)
            return;
        tableViewOption.removeClass("active");
        chartViewOption.addClass("active-right");
        isChartViewShown = true;
        tableView.hide();
        chartGenerator.generateCharts();
    };

};

DW.SubmissionAnalysisChartGenerator = function(){
    var self = this;
    var chartView = $('#chart_ol');

    self.generateCharts = function(){
         $.ajax({
                "dataType": 'json',
                "type": "POST",
                "url": analysis_stats_url,
                "data": {'search_filters': JSON.stringify(filter_as_json())},
                "success": function (response) {
                       chartView.show();
                      _draw_bar_charts(response);
                },
                "error": function () {
                },
                "global": false
            });
    };

    var _draw_bar_charts = function(response){
        if (response.total == 0) {
            showNoSubmissionExplanation(chartView);
            return;
        }
        var $chart_ol = chartView.attr('style', 'width:' + ($(window).width() - 85) + 'px').empty();
        var i = 0;
        $.each(response.result, function (index, ans) {
            drawChartBlockForQuestions(index, ans, i, $chart_ol);
            drawChart(ans, i, response.total, "");
            i++;
        });
    };
};

DW.FilterSubmissionChartsBySearchText = function () {
};
DW.FilterSubmissionChartsBySearchText.prototype = new DW.SearchTextFilter();
DW.FilterSubmissionChartsBySearchText.prototype.postFilterSelection = function () {
    new DW.SubmissionAnalysisChartGenerator().generateCharts();
};