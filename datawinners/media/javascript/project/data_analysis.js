$(document).ready(function() {
    var screen_width = $(window).width() - 50;
    DW.submit_data = function() {
        $("#dateErrorDiv").hide();
        var aggregation_selectBox_Array = $(".aggregation_type");
        var aggregationArray = [];
        aggregation_selectBox_Array.each(function() {
            aggregationArray.push($(this).val());
        });
        var time_range = $("#dateRangePicker").val().split("/");
        if (time_range[0] == "" || time_range[0] == "Click to select a date range") {
            time_range[0] = '01-01-1996';
            time_range[1] = Date.parse('today').toString('dd-MM-yyyy');
            return {'time_range':time_range, 'aggregationArray': aggregationArray};
        }
        if (time_range[0] != "Click to select a date range" && Date.parse(time_range[0]) == null) {
            $("#dateErrorDiv").html('<label class=error>' + gettext("Enter a correct date. No filtering applied") + '</label>');
            $("#dateErrorDiv").show();
            time_range[0] = "";
            time_range[1] = "";
        }
        return {'time_range':time_range, 'aggregationArray': aggregationArray};
    };
    DW.wrap_table = function() {
        $("#data_analysis").wrap("<div class='data_table' style='width:" + screen_width + "px'/>");
    };
    DW.update_footer = function(footer) {
        var index = 0;
        $("tfoot tr th").each(function() {
            $(this).text(footer[index]);
            index = index + 1;
        });
    };
    $("#dateRangePicker").daterangepicker({
        presetRanges: [
            {text: gettext('Current month'), dateStart: function() {
                return Date.parse('today').moveToFirstDayOfMonth();
            }, dateEnd: 'today' },
            {text: gettext('Last Month'), dateStart: function() {
                return Date.parse('last month').moveToFirstDayOfMonth();
            }, dateEnd: function() {
                return Date.parse('last month').moveToLastDayOfMonth();
            } },
            {text: gettext('Year to date'), dateStart: function() {
                var x = Date.parse('today');
                x.setMonth(0);
                x.setDate(1);
                return x;
            }, dateEnd: 'today' }
        ],
        presets: {dateRange: gettext('Date Range')},
        earliestDate:'1/1/2011',
        latestDate:'21/12/2012',
        dateFormat:'dd-mm-yy',
        rangeSplitter:'/'

    });
    DW.dataBinding = function(data, destroy, retrive) {
        $('#data_analysis').dataTable({
            "bDestroy":destroy,
            "bRetrieve": retrive,
            "sPaginationType": "full_numbers",
//        "sScrollX": "100%",
//        "sScrollXInner": "100%",
//        "bScrollCollapse": true,
            "aaData": data,
            "oLanguage":{
                "sProcessing": gettext("Processing..."),
                    "sLengthMenu": gettext("Show _MENU_ Data records"),
                    "sZeroRecords": gettext("No matching records found"),
                    "sEmptyTable": gettext("No data available in table"),
                    "sLoadingRecords": gettext("Loading..."),
                    "sInfo": gettext("Showing _START_ to _END_ of _TOTAL_ Data records"),
                    "sInfoEmpty": gettext("Showing 0 to 0 of 0 Data records"),
                    "sInfoFiltered": gettext("(filtered from _MAX_ total Data records)"),
                    "sInfoPostFix": "",
                    "sSearch": gettext("Search:"),
                    "sUrl": "",
                    "oPaginate": {
                        "sFirst":    gettext("First"),
                        "sPrevious": gettext("Previous"),
                        "sNext":     gettext("Next"),
                        "sLast":     gettext("Last")
                    },
                    "fnInfoCallback": null
            }
        });
    };

    DW.dataBinding(initial_data, false, true);
    DW.wrap_table();
    $('#data_analysis select').customStyle();
    $(document).ajaxStop($.unblockUI);

    $(".aggregation_type").live("change", function() {
        var data = DW.submit_data();
        var aggregationArray = data['aggregationArray'];
        var time_list = data['time_range'];
        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>' ,css: { width:'275px'}});
        $.ajax({
            type: 'POST',
            url: window.location.pathname,
            data: {'aggregation-types':JSON.stringify(aggregationArray), 'start_time':time_list[0], 'end_time': time_list[1]},
            success:function(response) {
                var response_data = JSON.parse(response);
                DW.dataBinding(response_data.data, true, false);
                DW.update_footer(response_data.footer);
                DW.wrap_table();
            }});
    });


    $('#export_link').click(function() {
        var data = DW.submit_data();
        var aggregationArray = data['aggregationArray'];
        var time_list = data['time_range'];
        var path = window.location.pathname;
        var element_list = path.split("/");
        $("#aggregation-types").attr("value", JSON.stringify(aggregationArray));
        $("#questionnaire_code").attr("value", element_list[element_list.length - 2]);
        $("#start_time").attr("value", time_list[0]);
        $("#end_time").attr("value", time_list[1]);
        $('#export_form').submit();
    });

    $('#time_submit').click(function() {
        var data = DW.submit_data();
        var aggregationArray = data['aggregationArray'];
        var time_list = data['time_range'];
        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>' ,css: { width:'275px'}});
        $.ajax({
            type: 'POST',
            url: window.location.pathname,
            data: {'aggregation-types':JSON.stringify(aggregationArray), 'start_time':time_list[0], 'end_time': time_list[1]},
            success:function(response) {
                var response_data = JSON.parse(response);
                DW.dataBinding(response_data.data, true, false);
                DW.update_footer(response_data.footer);
                DW.wrap_table();

            }});
    });
});