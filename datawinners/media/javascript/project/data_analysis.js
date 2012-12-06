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
            var data = DW.submit_data();

            for (var name in data) {
                $('input[name="' + name + '"]').val(data[name]);
            }
            $('#export_form').submit();
        });

        $('#go').click(function () {
                var data = DW.submit_data();
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
        return {start_time: data[0], end_time: data[1]};
    }

    DW.submit_data = function () {
        var reporting_period = get_date($('#reportingPeriodPicker'), gettext("All Periods"));
        var submission_date = get_date($('#submissionDatePicker'), gettext("All Dates"));
        var subject_ids = $('#subjectSelect').attr('ids');
        var submission_sources = $('#dataSenderSelect').attr('data');
        var keyword = $('#keyword').val();
        return {
            'start_time': $.trim(reporting_period.start_time),
            'end_time': $.trim(reporting_period.end_time),
            'submission_date_start': $.trim(submission_date.start_time),
            'submission_date_end': $.trim(submission_date.end_time),
            'subject_ids': subject_ids,
            'submission_sources': submission_sources,
            'keyword': keyword
        };
        $(".dateErrorDiv").hide();
    };

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

    function buildColumnTypes(){
        return $(header_type_list).map(function(index, value){
            var column_name = header_name_list[index];
            return (value && column_name == gettext("Submission Date"))  ? { "sType":  value} : {"sType": "string"};
        });
    };

    function showDatePicker($input) {
        var $monthpicker = $('#monthpicker_start, #monthpicker_end', $('.ranges'));
        if ($input.data('ismonthly')) {
            $monthpicker.show();
        } else {
            $monthpicker.hide();
        }
        var $visible_datepickers = $('.ui-daterangepicker:visible');
        $visible_datepickers.each(function (index, picker) {
            if ($(picker).data('for') != $input.attr('id')) {
                $(picker).hide();
            }
        });
    }

    function buildRangePicker() {
        function configureSettings(header, ismonthly) {
            var year_to_date_setting = {text:gettext('Year to date'), dateStart:function () {
                var x = Date.parse('today');
                x.setMonth(0);
                x.setDate(1);
                return x;
            }, dateEnd:'today' };
            var settings = {
                presetRanges:[
                    {text:header, dateStart:function () {
                        return Date.parse('1900.01.01')
                    }, dateEnd:'today', is_for_all_period:true },
                    {text:gettext('Current month'), dateStart:function () {
                        return Date.parse('today').moveToFirstDayOfMonth();
                    }, dateEnd:'today' },
                    {text:gettext('Last Month'), dateStart:function () {
                        return Date.parse('last month').moveToFirstDayOfMonth();
                    }, dateEnd:function () {
                        return Date.parse('last month').moveToLastDayOfMonth();
                    } }
                ],
                presets:{dateRange:gettext('Choose Date(s)')},
                earliestDate:'1/1/2011',
                latestDate:'21/12/2012',
                dateFormat:getDateFormat(date_format),
                rangeSplitter:'-',
                onOpen: function() {
                    $filterSelects.dropdownchecklist("close");
                }
            };
            if (ismonthly) {
                settings.presets = {dateRange:gettext('Choose Month(s)')}
            } else {
                settings.presetRanges = settings.presetRanges.concat(year_to_date_setting);
                if (typeof(ismonthly) == "undefined") {
                    settings.dateFormat = 'dd.mm.yy';
                }
            }
            return settings;
        }

        function getDateFormat(date_format) {
            return date_format.replace('yyyy', 'yy');
        }

        var date_picker_headers = [gettext('All Periods'), gettext('All Dates')];
        $datepicker_inputs.each(function(index, input){
            var $input = $(input);
            $input.daterangepicker(configureSettings(date_picker_headers[index], $input.data('ismonthly'))).monthpicker();
            $input.click(function() {
                showDatePicker($input);
                $filterSelects.dropdownchecklist("close");
            });
        });
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
                maxDropHeight:200}, filter_options[index]));

        });
        hide_date_pickers_when_filter_show();
    }

    function hide_date_pickers_when_filter_show() {
        $('.ui-dropdownchecklist-selector').click(function () {
            $('.ui-daterangepicker:visible').hide();
        });
    }
    
    $('#keyword').keypress(function(e) {
        if (e.which == 13) {
            $('#go').click();
        }
    });

    init_page();
});
