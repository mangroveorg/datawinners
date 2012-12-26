$(document).ready(function () {
    var help_no_submission = $('#help_no_submissions').html();
    var message = gettext("No submissions available for this search. Try changing some of the filters.");
    var help_all_data_are_filtered = "<div class=\"help_accordion\" style=\"text-align: left;\">" + message + "</div>";
    var $filterSelects = $('#subjectSelect, #dataSenderSelect');
    var $datepicker_inputs = $('#reportingPeriodPicker, #submissionDatePicker');

    buildFilters();
    buildRangePicker();
    $(document).ajaxStop($.unblockUI);

    addOnClickListener();

    function addOnClickListener() {
        $('#export_link').click(function () {
            $('#export_form').appendJson(DW.get_criteria()).submit();
        });

        $('#go').click(function () {
                var data = DW.get_criteria();
                $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
                $.ajax({
                    type:'POST',
                    url:window.location.pathname,
                    data: data,
                    success:function (response) {
                        var response_data = JSON.parse(response);
                        DW.dataBinding(response_data.data_list, true, false, help_all_data_are_filtered);
                        var emptyChartText = response_data.data_list.length ==0 ? gettext('No submissions available for this search. Try changing some of the filters.'):'';
                        drawChart(response_data.statistics_result,
                            response_data.data_list.length,
                            emptyChartText);
                        DW.wrap_table();
                        if(DW.chart_view_shown){
                            $('#data_analysis_wrapper').hide();
                        }
                    }});
            }
        );
    }

    DW.wrap_table = function () {
        $("#data_analysis").wrap("<div class='data_table' style='width:" + ($(window).width() - 65) + "px'/>");
    };

    DW.dataBinding = function (data, destroy, retrive, emptyTableText) {
        $dataTable = $('#data_analysis').dataTable({
            "aaSorting":default_sort_order,
            "aoColumns": buildColumnTypes(),
            "bDestroy":destroy,
            "bRetrieve":retrive,
            "sPaginationType":"full_numbers",
            "aaData":data,
            "bSort":true,
            "aoColumnDefs": [
                {
                    "bVisible":false,
                    "aTargets": [ 0 ]
                }
            ],
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
        return $(header_type_list).map(function(index, value){
            var column_name = header_name_list[index];
            return (value && column_name == gettext("Submission Date"))  ? { "sType":  value} : {"sType": "string"};
        });
    };

    function closeFilterSelects() {
        $filterSelects.dropdownchecklist('close')
    }

    function buildRangePicker() {
        $('#reportingPeriodPicker').datePicker({header: gettext('All Periods'), eventCallback: closeFilterSelects});
        $('#submissionDatePicker').datePicker({eventCallback: closeFilterSelects});
    }

    function init_page() {
        DW.dataBinding(initial_data, false, true, help_no_submission);
        DW.wrap_table();
        drawChart(statistics, initial_data.length, initial_data.length == 0 ? help_no_submission: '');
        $('#data_analysis select').customStyle();
        DW.chart_view_shown = false;
        $('#data_analysis_chart').hide();
        $('#chart_info').hide();
        $('#chart_info_2').hide();

        if (initial_data.length == 0) {
            disableFilters = function () {
                var filters = [$(".ui-dropdownchecklist"), $(".ui-dropdownchecklist-selector"), $(".ui-dropdownchecklist-text"),
                    $("#go").removeClass('button_blue').addClass('button_disabled'),
                    $('#keyword')].concat($datepicker_inputs);

                $.each(filters, function (index, filter) {
                    filter.attr('disabled', 'disabled');

                    if (filter.is("span")) {
                        $("> span", filter).addClass('disabled');
                    } else {
                        filter.addClass('disabled');
                    }

                    filter.unbind('click');
                })
                $('.filter_label').css({color:"#888"});
            }();
        }
    };

    DW.toggle_view = function () {
        $('#dataTables_info').toggle();
        $('#chart_info').toggle();
        $('#chart_info_2').toggle();
        $('#data_analysis_chart').toggle();
        $('#data_analysis_wrapper').toggle();
    };

    DW.show_data_view = function() {
        if(DW.chart_view_shown){
            $("#table_view").addClass("active");
            $("#chart_view").removeClass("active-right");
            DW.toggle_view();
            DW.chart_view_shown = false;
        }
    };

    DW.show_chart_view = function() {
        if(!DW.chart_view_shown){
            $("#table_view").removeClass("active");
            $("#chart_view").addClass("active-right");
            DW.toggle_view();
            DW.chart_view_shown = true;
        }
    };

    function buildFilters() {
        var subject_options = {emptyText:gettext("All") + ' ' + entity_type};
        var data_sender_options = {emptyText:gettext("All Data Senders")};
        var filter_options = [subject_options, data_sender_options];

        $filterSelects.each(function(index, filter) {
            $(filter).dropdownchecklist($.extend({firstItemChecksAll:false,
                explicitClose:gettext("OK"),
                explicitClear:gettext("Clear"),
                width:$(this).width(),
                eventCallback : function(){$('.ui-daterangepicker:visible').hide();},
                maxDropHeight:200}, filter_options[index]));

        });
    }

    $('#keyword').keypress(function(e) {
        if (e.which == 13) {
            $('#go').click();
        }
    });

    init_page();
});
