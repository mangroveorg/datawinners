$(document).ready(function() {
    var screen_width = $(window).width() - 50;
    DW.submit_data = function() {
        $("#dateErrorDiv").hide();
        var aggregation_selectBox_Array = $(".aggregation_type");
        var aggregationArray = [];
        aggregation_selectBox_Array.each(function() {
            aggregationArray.push($(this).val());
        });
        var time_range = $("#dateRangePicker").val().split("-");

        if (time_range[0] == "" || time_range[0] == "All Periods") {
            time_range[0] = '01-01-1996';
            time_range[1] = '31-12-6000';
            return {'time_range':time_range, 'aggregationArray': aggregationArray};
        }
        if (time_range[0] != gettext("All Periods") && Date.parse(time_range[0]) == null) {
            $("#dateErrorDiv").html('<label class=error>' + gettext("Enter a correct date. No filtering applied") + '</label>');
            $("#dateErrorDiv").show();
            time_range[0] = "";
            time_range[1] = "";
            return {'time_range':time_range, 'aggregationArray': aggregationArray};
        }
        if (time_range.length == 1){
            time_range[1] = time_range[0];
            return {'time_range':time_range, 'aggregationArray': aggregationArray};
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
            {text: gettext('All Periods'), dateStart: function() {
                return Date.parse('1900.01.01')
            }, dateEnd: 'today', is_for_all_period: true },
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
        dateFormat: getDateFormat(date_format),
        rangeSplitter:'-'

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
            "bSort": false,
            "oLanguage":{
                "sProcessing": gettext("Processing..."),
                    "sLengthMenu": gettext("Show _MENU_ Data records"),
                    "sZeroRecords": gettext("No matching records found"),
                    "sEmptyTable": gettext("No data available in table"),
                    "sLoadingRecords": gettext("Loading..."),
                    "sInfo": gettext("<span>_START_ - _END_</span> of _TOTAL_ Data Records"),
                    "sInfoEmpty": gettext("0 Data Records"),
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
            },
           "sDom":'<"@dataTables_info"i>rtpl<"@dataTable_search"f>',
           "iDisplayLength": 25
        });
    };

    DW.dataBinding(initial_data, false, true);
    DW.wrap_table();
    $('#data_analysis select').customStyle();
    $(document).ajaxStop($.unblockUI);

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
        var report_period = $("#dateRangePicker").val()
        var for_all_period = (report_period == gettext("All Periods"))
        report_period = report_period.replace(/ /g,'')
        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>' ,css: { width:'275px'}});
        $.ajax({
            type: 'POST',
            url: window.location.pathname + (for_all_period ? "" : (report_period + '/')),
            success:function(response) {
                var response_data = JSON.parse(response);
                DW.dataBinding(response_data.data, true, false);
                DW.update_footer(response_data.footer);
                DW.wrap_table();

            }});
    });

    function getDateFormat(date_format) {
        return date_format.replace('yyyy', 'yy');
    };
});