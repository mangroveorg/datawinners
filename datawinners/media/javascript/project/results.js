$(document).ready(function () {
    $.ajaxSetup({ cache: false });
    DW.get_ids = function(){
        var ids = [];
        $(".selected_submissions:checked").each(function(){
            if($(this).val()!="None"){
                ids.push($(this).val());
            }
        });
        return ids;
    }
    $(document).ajaxStop($.unblockUI);
    var $no_submission_hint = $('.help_no_submissions');
    var $page_hint = $('#page_hint');
    var tab = ["all", "success", "error", "deleted"];
    var message = gettext("No submissions available for this search. Try changing some of the filters.");
    var help_all_data_are_filtered = "<div class=\"help_accordion\" style=\"text-align: left;\">" + message + "</div>";
    var active_tab_index;
    buildRangePicker();
    $("#tabs").tabs().find('>ul>li>a').click(function(){
        var tab_index = $(this).parent().index();
        if (active_tab_index != tab_index) {
            fetch_data(tab_index);
            active_tab_index = tab_index;
        }
    }).filter(':first').trigger('click');

    function update_table_header(header) {
        $("table.submission_table thead tr").html('');
        $.each(header, function(index, element) {
            $("table.submission_table thead tr").append("<th>" + element + "</th>");
        });
    }

    function buildRangePicker() {
        $('#reportingPeriodPicker').datePicker({header: gettext('All Periods')});
        $('#submissionDatePicker').datePicker();
    }

    $('#go').click(function () {
            var data = submit_data();
            $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
            $.ajax({
                type:'POST',
                url:window.location.pathname,
                data: data,
                success:function (response) {
                    var response_data = JSON.parse(response);
                    dataBinding(response_data.data_list, true, false, help_all_data_are_filtered);
                    var emptyChartText = response_data.data_list.length ==0 ? gettext('No submissions available for this search. Try changing some of the filters.'):'';
                    wrap_table();
                }});
        }
    );

    var submit_data = function () {
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

    var get_date = function($datePicker, default_text) {
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

    function fetch_data(active_tab_index) {
        DW.loading();
        $.ajax({
            type:'POST',
            url:window.location.pathname + '?type=' + tab[active_tab_index],
            data:{},
            success:function (response) {
                var response_data = JSON.parse(response);
                update_table_header(response_data.header_list);
                show_data(active_tab_index, response_data.data_list);
                $(".action").parent().clone().addClass("margin_top_null").appendTo(".data_table");
            }});
    }

    var dataBinding = function (data, destroy, retrive, emptyTableText) {
        $('.submission_table').dataTable({
            "bDestroy":destroy,
            "bRetrieve":retrive,
            "sPaginationType":"full_numbers",
            "aaData":data,
            "bSort":false,
            "aoColumnDefs": [
                {
                    "fnRender": function ( oObj ) {
                        return '<input type="checkbox" value="' + oObj.aData[0] +'" class="selected_submissions"/>' ;
                    },
                    "aTargets": [ 0 ]
                }
            ],
            "fnHeaderCallback": function( nHead, aData, iStart, iEnd, aiDisplay ) {
                nHead.getElementsByTagName('th')[0].innerHTML = '<input type="checkbox" id="master_checkbox"/>';
            },
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
            "sDom":'<"@dataTables_info"i>rtpl',
            "iDisplayLength":25
        });
    };

    function show_data(active_tab_index, data) {
        var index = (active_tab_index || 0) + 1;
        $page_hint.find('>div:nth-child(' + index + ')').show().siblings().hide();
        var emptyTableText = $no_submission_hint.filter(':eq(' + active_tab_index + ')').html();
        dataBinding(data, true, false, emptyTableText);
        wrap_table();
    }
    var wrap_table = function () {
        $(".submission_table").wrap("<div class='data_table' style='width:" + ($(window).width() - 65) + "px'/>");
    };

    //Checkbox on/off functionality
    $("#master_checkbox").live("click", function(){
        var status = $(this).attr('checked');
        $(".selected_submissions").each(function(){
            $(this).attr("checked", status);
        });

    });

    $('select.action').live("change", function(){
        var ids = DW.get_ids();
        if($(".selected_submissions:checked").length == 0){
            $("#message_text").html("<div class='message message-box'>" + gettext("Please select atleast one undeleted record") + "</div>");
            $('select.action>option:first').attr('selected', 'selected');
        }
        else{

            if(ids.length==0){
                $("#message_text").html("<div class='message message-box'>" + gettext("This data has already been deleted") + "</div>");
                $('select.action>option:first').attr('selected', 'selected');
            }
            else{
                DW.delete_submission_warning_dialog.show_warning();
                DW.delete_submission_warning_dialog.ids = ids;
            }
        }
        $("#message_text .message").delay(5000).fadeOut();
    });
    var kwargs = {container:"#delete_submission_warning_dialog",
        continue_handler:function () {
            var ids = this.ids;
            $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
            $.ajax({
                type: 'POST',
                url: window.location.pathname + "?rand="+ new Date().getTime(),
                data:  {'id_list': JSON.stringify(ids), 'page_number':DW.current_page},
                success:function(response) {
                    var data = JSON.parse(response);
                    if (data.success) {
                        $("#message_text").html("<div class='message success-box'>" + data.success_message + "</div>");
                        fetch_data(0);
                    } else {
                        $("#message_text").html("<div class='error_message message-box'>" + data.error_message + "</div>");
                    }
                    $("#message_text .message").delay(5000).fadeOut();
                    $('select.action>option:first').attr('selected', 'selected');
                    $.unblockUI();
                },
                error: function(e) {
                    $("#message_text").html("<div class='error_message message-box'>" + e.responseText + "</div>");
                    $('select.action>option:first').attr('selected', 'selected');
                    $.unblockUI();
                }
            });
            return false;
        },
        title:gettext("Your Submission(s) will be deleted"),
        cancel_handler:function () {
            $('select.action>option:first').attr('selected', 'selected');
        },
        height:150,
        width:550
    }

    DW.delete_submission_warning_dialog = new DW.warning_dialog(kwargs);

});

