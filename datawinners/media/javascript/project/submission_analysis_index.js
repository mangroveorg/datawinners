$(function () {
    $.ajaxSetup({ cache: false });
    var submissionTabs = new DW.SubmissionTabs();
    submissionTabs.setToAnalysisTab();

    var _initTable = function (submissionTabs) {
        var submission_table_options = {
            header_url: render_table_url + "/headers",
            table_source_url: render_table_url + '?type=' + submissionTabs.getActiveTabName(),
            row_check_box_visible: false,
            actions_menu: [],
            tabName: submissionTabs.getActiveTabName()
        };
        new DW.SubmissionLogTable(submission_table_options);
    };

    var _initialize_filters = function () {
        new DW.FilterSubmissionTableByDate().init();
        new DW.FilterSubmissionTableByDataSender().init();
        new DW.FilterSubmissionTableBySubject().init();
        new DW.FilterSubmissionTableBySearchText().init();
    };

    _initTable(submissionTabs);
    _initialize_filters();
    $('#page_hint_section').text($('#page_hint').find('>div:first').text());

    $(".ui-corner-all").removeClass("ui-corner-all");
    $(".ui-corner-top").removeClass("ui-corner-top");

    new DW.SubmissionLogExport().init(submissionTabs.getActiveTabName());
    DW.chart_view_shown = false;

    DW.show_data_view = function () {
        if (DW.chart_view_shown) {
            $("#table_view").addClass("active");
            $("#chart_view").removeClass("active-right");
            reinitialize_table_view();
            _initTable(submissionTabs);
            $("#chart_ol").hide();
            DW.chart_view_shown = false;
        }
    };

    DW.show_chart_view = function () {
        if (!DW.chart_view_shown) {
            $("#table_view").removeClass("active");
            $("#chart_view").addClass("active-right");
            DW.chart_view_shown = true;
            $.ajax({
                "dataType": 'json',
                "type": "POST",
                "url": analysis_stats_url,
                "data": {'search_filters': JSON.stringify(filter_as_json())},
                "success": function (response) {
                    $("#submission_logs").hide();
                    $('#chart_ol').show();
                    draw_bar_charts(response);
                },
                "error": function () {
                },
                "global": false
            })
        }
    };
});


function draw_bar_charts(response) {
    if (response.total == 0) {
        return showNoSubmissionExplanation($('#chart_ol'));
    }
    $chart_ol = $('#chart_ol').attr('style', 'width:' + ($(window).width() - 85) + 'px').empty();
    var i = 0;
    $.each(response.result, function (index, ans) {
        drawChartBlockForQuestions(index, ans, i, $chart_ol);
        drawChart(ans, i, response.total, "");
        i++;
    });
}

function reinitialize_table_view() {
    $("#submission_logs").show();
    $('.submission_table').dataTable().fnDestroy();
    $('.submission_table').empty();
    $('#chart_info').empty();
    $('#chart_info_2').empty();
    $('#chart_ol').empty();
}
