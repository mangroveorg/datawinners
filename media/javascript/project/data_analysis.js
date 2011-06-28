$(document).ready(function() {
    var screen_width = $(window).width() - 50;
    DW.submit_data = function() {
        $("#dateErrorDiv").hide();
        var aggregation_selectBox_Array = $(".aggregation_type");
        aggregationArray = new Array();
        aggregation_selectBox_Array.each(function() {
            aggregationArray.push($(this).val())
        });
        var time_range = $("#dateRangePicker").val().split("/");
        if (time_range[0] != "Click to select a date range" && Date.parse(time_range[0]) == null) {
            $("#dateErrorDiv").html('<label class=error>' + "Enter a correct date. No filtering applied" + '</label>')
            $("#dateErrorDiv").show()
            time_range[0] = "";
            time_range[1] = "";
        }
        var start_time = time_range[0];
        var end_time = time_range[1];
        return [start_time , end_time]
    }
    DW.wrap_table = function() {
        $("#data_analysis").wrap("<div class='data_table' style='width:"+screen_width+"px'/>")
    }
    $("#dateRangePicker").daterangepicker({
                presetRanges: [
                    {text: 'Current month', dateStart: function() {
                        return Date.parse('today').moveToFirstDayOfMonth();
                    }, dateEnd: 'today' },
                    {text: 'Last Month', dateStart: function(){return Date.parse('last month').moveToFirstDayOfMonth();}, dateEnd: function(){return Date.parse('last month').moveToLastDayOfMonth();} },
                    {text: 'Year to date', dateStart: function() {
                        var x = Date.parse('today');
                        x.setMonth(0);
                        x.setDate(1);
                        return x;
                    }, dateEnd: 'today' }
                ],
                presets: {dateRange: 'Date Range'},
                earliestDate:'1/1/2011', latestDate:'21/12/2012', dateFormat:'dd-mm-yy', rangeSplitter:'/',
               
            });
    DW.dataBinding = function(data, destroy, retrive) {
        $('#data_analysis').dataTable({
                    "bDestroy":destroy,
                    "bRetrieve": retrive,
                    "sPaginationType": "full_numbers",
//        "sScrollX": "100%",
//        "sScrollXInner": "100%",
//        "bScrollCollapse": true,
                    "aaData": data
                });
    }

    DW.dataBinding(initial_data, false, true);
    DW.wrap_table();
    $('#data_analysis select').customStyle();

    $(".aggregation_type").live("change", function() {
        var time_list = DW.submit_data();
        $.ajax({
                    type: 'POST',
                    url: window.location.pathname,
                    data: {'aggregation-types':JSON.stringify(aggregationArray), 'start_time':time_list[0], 'end_time': time_list[1]},
                    success:function(response) {
                        var response_data = JSON.parse(response);
                        DW.dataBinding(response_data, true, false);
                        DW.wrap_table();
                    }});
    });


    $('#export_link').click(function() {
        var time_list = DW.submit_data();
        var path = window.location.pathname;
        var element_list = path.split("/");
        $("#aggregation-types").attr("value", JSON.stringify(aggregationArray));
        $("#questionnaire_code").attr("value", element_list[element_list.length - 2]);
        $("#start_time").attr("value", time_list[0]);
        $("#end_time").attr("value", time_list[1]);
        $('#export_form').submit();
    });

    $('#time_submit').click(function(){
        var time_list = DW.submit_data();
        $.ajax({
            type: 'POST',
            url: window.location.pathname,
            data: {'aggregation-types':JSON.stringify(aggregationArray), 'start_time':time_list[0], 'end_time': time_list[1]},
            success:function(response) {
                var response_data = JSON.parse(response);
                DW.dataBinding(response_data, true, false);
                DW.wrap_table();
            }});
    });
});
