$(document).ready(function() {
    $('#dateRangePicker').monthpicker();
    var $subjectSelect = $('#subjectSelect');
    $(subjects_data).each(function(index, subject) {
        $('<option>' + subject[0] + '</option>').val(subject[0]).attr('code', subject[1]).appendTo($subjectSelect);
    });
    var emptyText = gettext("All") + ' ' + entity_type;
    $subjectSelect.dropdownchecklist({emptyText: emptyText ,
                                        firstItemChecksAll: false,
                                        explicitClose:gettext("OK"),
                                        width: $subjectSelect.width(),
                                        maxDropHeight: 200});

    var screen_width = $(window).width() - 50;
    DW.submit_data = function() {
        $("#dateErrorDiv").hide();
        var aggregation_selectBox_Array = $(".aggregation_type");
        var aggregationArray = [];
        aggregation_selectBox_Array.each(function() {
            aggregationArray.push($(this).val());
        });
        var time_range = $("#dateRangePicker").val().split("-");
        var subject_ids = $subjectSelect.attr('ids');

        if (time_range[0] == "" || time_range[0] == gettext("All Periods")) {
            return {'time_range':['', ''], 'aggregationArray': aggregationArray, 'subject_ids': subject_ids};
        }
        if (time_range[0] != gettext("All Periods") && Date.parse(time_range[0]) == null) {
            $("#dateErrorDiv").html('<label class=error>' + gettext("Enter a correct date. No filtering applied") + '</label>');
            $("#dateErrorDiv").show();
            time_range[0] = "";
            time_range[1] = "";
            return {'time_range':time_range, 'aggregationArray': aggregationArray, 'subject_ids': subject_ids};
        }
        if (time_range.length == 1) {
            time_range[1] = time_range[0];
            return {'time_range':time_range, 'aggregationArray': aggregationArray, 'subject_ids': subject_ids};
        }
        return {'time_range':time_range, 'aggregationArray': aggregationArray, 'subject_ids': subject_ids};
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

    function configureSettings(){
        var year_to_date_setting = {text: gettext('Year to date'), dateStart: function() {
            var x = Date.parse('today');
            x.setMonth(0);
            x.setDate(1);
            return x;
        }, dateEnd: 'today' };

        var settings = {
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
                } }
            ],
            presets: {dateRange: gettext('Choose Date(s)')},
            earliestDate:'1/1/2011',
            latestDate:'21/12/2012',
            dateFormat: getDateFormat(date_format),
            rangeSplitter:'-'

        };
        if(date_format.indexOf('dd') >= 0) {
            settings.presetRanges = settings.presetRanges.concat(year_to_date_setting);
        } else {
            settings.presets = {dateRange:gettext('Choose Month(s)')}
        }
        return settings;
    }
    $("#dateRangePicker").daterangepicker(configureSettings());

    DW.dataBinding = function(data, destroy, retrive) {
        $('#data_analysis').dataTable({
            "bDestroy":destroy,
            "bRetrieve": retrive,
            "sPaginationType": "full_numbers",
            "aaData": data,
            "bSort": true,
            "oLanguage":{
                "sProcessing": gettext("Processing..."),
                    "sLengthMenu": gettext("Show _MENU_ Submissions"),
                    "sZeroRecords": gettext("No matching records found"),
                    "sEmptyTable": gettext("No data available"),
                    "sLoadingRecords": gettext("Loading..."),
                    "sInfo": gettext("<span>_START_ - _END_</span> of _TOTAL_ Submissions"),
                    "sInfoEmpty": gettext("0 Submissions"),
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
        var time_list = data['time_range'];
        var path = window.location.pathname;
        var element_list = path.split("/");
        $("#questionnaire_code").attr("value", element_list[element_list.length - 2]);
        $("#start_time").attr("value", time_list[0]);
        $("#end_time").attr("value", time_list[1]);
        $("#subject_ids").attr("value", data['subject_ids']);

        $('#export_form').submit();
    });

    $('#time_submit').click(function() {
        var data = DW.submit_data();
        var time_list = data['time_range'];

        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>' ,css: { width:'275px'}});
        $.ajax({
            type: 'POST',
            url: window.location.pathname,
            data: {'start_time':time_list[0].trim(), 'end_time': time_list[1].trim(), 'subject_ids': data['subject_ids']},
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