$(document).ready(function () {
    $("#tabs").tabs();

    $('#delete_submission_warning_dialog').hide()

    var help_no_submission = $('#help_no_submissions').html();
    var message = gettext("No submissions available for this search. Try changing some of the filters.");
    var help_all_data_are_filtered = "<div class=\"help_accordion\" style=\"text-align: left;\">" + message + "</div>";

    $(document).ajaxStop($.unblockUI);

    addOnClickListener();

    function addOnClickListener() {
        $('#export_link').click(function () {
            var data = submit_data();

            for (var name in data) {
                $('input[name="' + name + '"]').val(data[name]);
            }
            $('#export_form').submit();
        });

        $('#go').click(function () {
                var data = submit_data();
                $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
                $.ajax({
                    type:'POST',
                    url:window.location.pathname,
                    data:data,
                    success:function (response) {
                        var response_data = JSON.parse(response);

                        dataBinding(response_data.data_list, true, false, help_all_data_are_filtered);

                        var emptyChartText = response_data.data_list.length == 0 ? gettext('No submissions available for this search. Try changing some of the filters.') : '';
                        drawChart(response_data.statistics_result,
                            response_data.data_list.length,
                            emptyChartText);
                        wrap_table();
                    }});
            }
        );
    }

    function get_date($datePicker, default_text) {
        var data = $datePicker.val().split("-");
        if (data[0] == "" || data[0] == default_text) {
            data = ['', ''];
        } else if (data[0] != default_text && Date.parse(data[0]) == null) {
            $datePicker.next().html('<label class=error>' + gettext("Enter a correct date. No filtering applied") + '</label>').show();
            data = ['', ''];
        } else if (data.length == 1) {
            data[1] = data[0];
        }
        return {start_time:data[0], end_time:data[1]};
    }

    var submit_data = function () {
        var reporting_period = get_date($('#reportingPeriodPicker'), gettext("All Periods"));
        var submission_date = get_date($('#submissionDatePicker'), gettext("All Dates"));
        var subject_ids = $('#subjectSelect').attr('ids');
        var submission_sources = $('#dataSenderSelect').attr('data');
        var keyword = $('#keyword').val();
        return {
            'start_time':$.trim(reporting_period.start_time),
            'end_time':$.trim(reporting_period.end_time),
            'submission_date_start':$.trim(submission_date.start_time),
            'submission_date_end':$.trim(submission_date.end_time),
            'subject_ids':subject_ids,
            'submission_sources':submission_sources,
            'keyword':keyword
        };
        $(".dateErrorDiv").hide();
    };

    var wrap_table = function () {
        $("#data_table").wrap("<div class='data_table' style='width:" + ($(window).width() - 65) + "px'/>");
    };

    var dataBinding = function (data, destroy, retrive, emptyTableText) {
        $dataTable = $('#data_table').dataTable({
            "aaSorting":default_sort_order,
//            "aoColumns":buildColumnTypes(),
            "bDestroy":destroy,
            "bRetrieve":retrive,
            "sPaginationType":"full_numbers",
            "aaData":data,
            "bSort":true,
            "oLanguage":{
                "sProcessing":gettext("Processing..."),
                "sLengthMenu":gettext("Show _MENU_ Submissions"),
                "sZeroRecords":emptyTableText,
                "sEmptyTable":emptyTableText,
                "sLoadingRecords":gettext("Loading..."),
                "sInfo":gettext("<span class='bold'>_START_ - _END_</span> of <span id='total_count'>_TOTAL_</span> Submissions"),
                "sInfoEmpty":gettext("0 Submissions"),
                "sInfoFiltered":gettext("(filtered from _MAX_ total Data records)"),
                "sInfoPostFix":"",
                "sSearch":gettext("Search:"),
                "sUrl":"",
                "oPaginate":{
                    "sFirst":gettext("First"),
                    "sPrevious":gettext("Previous"),
                    "sNext":gettext("Next"),
                    "sLast":gettext("Last")
                },
                "fnInfoCallback":null
            },
            "sDom":'<"@dataTables_info"i>rtpl<"@dataTable_search">',
            "iDisplayLength":25
        });
    };

    function buildColumnTypes() {
        return $(header_type_list).map(function (index, value) {
            var column_name = header_name_list[index];
            return (value && column_name == gettext("Submission Date")) ? { "sType":value} : {"sType":"string"};
        });
    }

    ;

    function init_page() {
        dataBinding(initial_data, false, true, help_no_submission);
        wrap_table();
    }

    init_page();
});

