$(document).ready(function () {
    var help_no_submission = $('#help_no_submissions').html();
    var message = gettext("No submissions available for this search. Try removing some of your filters.")
    var help_all_data_are_filtered = "<div class=\"help_accordion\" style=\"text-align: left;\">" + message + "</div>";

    $('#time_submit').click(function () {
            var data = DW.submit_data();
            $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
            $.ajax({
                type:'POST',
                url:window.location.pathname,
                data: data,
                success:function (response) {
                    var response_data = JSON.parse(response);
                    DW.dataBinding(response_data.data, true, false, help_all_data_are_filtered);
                    DW.update_footer(response_data.footer);
                    DW.wrap_table();
                    DW.draw_chart(response_data.data, header_list);
                }});
        }
    );

    function addOnClickListener() {
        $('#export_link').click(function () {
            var data = DW.submit_data();
            var path = window.location.pathname;
            var element_list = path.split("/");
            $("#questionnaire_code").attr("value", element_list[element_list.length - 2]);

            for (name in data) {
                $('#' + name).val(data[name]);
            }
            $('#export_form').submit();
        });
    }

    DW.submit_data = function () {
        $("#dateErrorDiv").hide();
        var time_range = $("#dateRangePicker").val().split("-");
        var subject_ids = $('#subjectSelect').attr('ids');
        var submission_sources = $('#dataSenderSelect').attr('data');

        if (time_range[0] == "" || time_range[0] == gettext("All Periods")) {
            time_range = ['', ''];
        }else if (time_range[0] != gettext("All Periods") && Date.parse(time_range[0]) == null) {
            $("#dateErrorDiv").html('<label class=error>' + gettext("Enter a correct date. No filtering applied") + '</label>').show();
            time_range = ['', ''];
        }else if (time_range.length == 1) {
            time_range[1] = time_range[0];
        }
        return {
                'start_time':$.trim(time_range[0]),
                'end_time':$.trim(time_range[1]),
                'subject_ids':subject_ids,
                'submission_sources': submission_sources
                };
    };

    DW.wrap_table = function () {
        $("#data_analysis").wrap("<div class='data_table' style='width:" + ($(window).width() - 50) + "px'/>");
    };

    DW.update_footer = function (footer) {
        var index = 0;
        $("tfoot tr th").each(function () {
            $(this).text(footer[index]);
            index = index + 1;
        });
    };
    DW.dataBinding = function (data, destroy, retrive, emptyTableText) {
        $('#data_analysis').dataTable({
            "bDestroy":destroy,
            "bRetrieve":retrive,
            "sPaginationType":"full_numbers",
            "aaData":data,
            "bSort":true,
            "oLanguage":{
                "sProcessing":gettext("Processing..."),
                "sLengthMenu":gettext("Show _MENU_ Submissions"),
                "sZeroRecords":gettext("No matching records found"),
                "sEmptyTable":emptyTableText,
                "sLoadingRecords":gettext("Loading..."),
                "sInfo":gettext("<span>_START_ - _END_</span> of _TOTAL_ Submissions"),
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
            "sDom":'<"@dataTables_info"i>rtpl<"@dataTable_search"f>',
            "iDisplayLength":25
        });
    };
    DW.draw_chart = function (initial_data) {

    };
    function buildRangePicker() {
        function configureSettings() {
            var year_to_date_setting = {text:gettext('Year to date'), dateStart:function () {
                var x = Date.parse('today');
                x.setMonth(0);
                x.setDate(1);
                return x;
            }, dateEnd:'today' };

            var settings = {
                presetRanges:[
                    {text:gettext('All Periods'), dateStart:function () {
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
                onOpen: function(){
                    var $filterSelects = $('#subjectSelect').add('#dataSenderSelect');
                    $filterSelects.each(function(index, filter){
                        $(filter).dropdownchecklist("close");
                    })
                }

            };
            if (date_format.indexOf('dd') >= 0) {
                settings.presetRanges = settings.presetRanges.concat(year_to_date_setting);
            } else {
                settings.presets = {dateRange:gettext('Choose Month(s)')}
            }
            return settings;
        }

        function getDateFormat(date_format) {
            return date_format.replace('yyyy', 'yy');
        }

        $('#dateRangePicker').monthpicker();

        $("#dateRangePicker").daterangepicker(configureSettings());
    }

    DW.dataBinding(initial_data, false, true, help_no_submission);
    DW.wrap_table();

    DW.draw_chart(initial_data);
    $('#data_analysis select').customStyle();

    DW.chart_view_shown = false;
    $('#data_analysis_chart').hide();

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

    DW.toggle_view = function () {
        $('#data_analysis_chart').toggle();
        $('#data_analysis_wrapper').toggle();
    };

    addOnClickListener();
    buildRangePicker();
    buildFilters();

    if (initial_data.length == 0) {
        function disableFilters() {
            var filters = [$(".ui-dropdownchecklist"), $(".ui-dropdownchecklist-selector"),$(".ui-dropdownchecklist-text"),
                            $("#time_submit").attr('disabled', 'disabled').removeClass('button_blue').addClass('button_disabled'),
                            $("#dateRangePicker"),
                            $('#dataTable_search input')];

            $.each(filters, function (index, filter) {
                filter.addClass('disabled').attr('disabled', 'disabled');
                filter.unbind('click');
            })
            $('.filter_label').css({color:"#888"});
        }

        disableFilters();
        $('#no_filter_help').show();
    }

    $(document).ajaxStop($.unblockUI);

});

function buildFilters() {
    var $filterSelects = $('#subjectSelect').add('#dataSenderSelect');
    var subject_options = {emptyText:gettext("All") + ' ' + entity_type};
    var data_sender_options = {emptyText:gettext("All Data Senders")};
    var filter_options = [subject_options, data_sender_options];

    $filterSelects.each(function(index, filter){
        $(filter).dropdownchecklist($.extend({firstItemChecksAll:false,
            explicitClose:gettext("OK"),
            width:$(this).width(),
            maxDropHeight:200}, filter_options[index]));
        $("#ddcl-"+$(filter).attr("id")+" > span").bind("click", function(){
            if ($('.ui-daterangepicker:visible').length) {
                $("#dateRangePicker").trigger('click');
            }
        });
    });
}
