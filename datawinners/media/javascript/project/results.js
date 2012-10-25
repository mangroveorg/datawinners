
$(document).ready(function(){

    $.ajaxSetup({ cache: false });


    DW.init_pagination = function () {
        DW.current_page = 0;
        $("#pagination").pagination($('#total_rows').val(), {
            items_per_page:10,
            num_display_entries : 5,
            num_edge_entries:2,
            load_first_page:false,
            next_text: gettext("Next"),
            prev_text: gettext("Prev"),
            callback : function(page_number) {
                new DW.show_data(page_number + 1);
                DW.current_page = page_number + 1;
            }
        });
    };

    DW.submit_data = function() {
        var time_range = $($("#dateRangePicker").val().split("/")).map(function(i, e) {return $.trim(e)});

        if(time_range[0] == "") {
            time_range[0]='01-01-1996';
            time_range[1]=Date.parse('today').toString('dd-MM-yyyy');
            return time_range;
        }
        if (time_range[0] != "Click to select a date range" && Date.parse(time_range[0]) == null) {
            $("#dateErrorDiv").html('<label class=error>' + "Enter a correct date. No filtering applied" + '</label>');
            $("#dateErrorDiv").show();
            time_range[0] = "";
            time_range[1] = "";
        }
        return time_range;
   };


    DW.show_data = function(page_number) {
        this.page_number = page_number;
        this._init();
    };
    DW.show_data.prototype = {
        _init : function(){
            var time_range = DW.submit_data();
            $.get('/project/datarecords/filter',
                  {
                      questionnaire_code: $('#questionnaire_id').val(),
                      start_time:time_range[0],
                      end_time: time_range[1],
                      page_number: this.page_number,
                      rand: Math.floor(Math.random()*10000000)
                  }).success(
                  function(data){
                    if(data){
                        $('#submission_table').html(data);
                    }
                  }
);
            }
    };


   DW.screen_width = $(window).width() - 50;
     $("#data_record").wrap("<div class='data_table' style='width:"+DW.screen_width+"px'/>");
    DW.wrap_table = function() {
        $("#data_analysis").wrap("<div class='data_table' style='width:"+DW.screen_width+"px'/>");
    };
    $("#dateRangePicker").daterangepicker({
                presetRanges: [
                    {text: gettext('Current month'), dateStart: function() {
                        return Date.parse('today').moveToFirstDayOfMonth();
                    }, dateEnd: 'today' },
                    {text: gettext('Last Month'), dateStart: function(){return Date.parse('last month').moveToFirstDayOfMonth();}, dateEnd: function(){return Date.parse('last month').moveToLastDayOfMonth();} },
                    {text: gettext('Year to date'), dateStart: function() {
                        var x = Date.parse('today');
                        x.setMonth(0);
                        x.setDate(1);
                        return x;
                    }, dateEnd: 'today' }
                ],
                presets: {dateRange: 'Date Range'},
                earliestDate:'1/1/2011', latestDate:'21/12/2012', dateFormat:'dd-mm-yy', rangeSplitter:'/'

            });

    //Checkbox on/off functionality
    $("#master_checkbox").live("click", function(){
        $(".selected_submissions").each(function(){
           $(this).attr("checked", !$(this).attr('checked'));
        });

    });

    $('#action').change(function(){
       var ids = [];
       if($(".selected_submissions:checked").length == 0){
            $("#message_text").html("<div class='error_message message-box'>" + gettext("Please select atleast one undeleted record") + "</div>");
            $('#action').val(0);
       }
       else{
       $(".selected_submissions:checked").each(function(){
           if($(this).val()!="None"){
               ids.push($(this).val());
           }
       });
       if(ids.length==0){
            $("#message_text").html("<div class='error_message message-box'>" + gettext("This data has already been deleted") + "</div>");
            $('#action').val(0);
       }
       else{
           var answer = confirm(gettext("Are you sure you want to delete the selected record/s?"));
           if(answer){
               $.ajax({
                  type: 'POST',
                  url: window.location.pathname + "?rand="+ new Date().getTime(),
                  data:  {'id_list': JSON.stringify(ids), 'page_number':DW.current_page},
                  success:function(response) {
                        $('#submission_table').empty();
                        $('#submission_table').append(response);
                    },
                  error: function(e) {
                        $("#message_text").html("<div class='error_message message-box'>" + e.responseText + "</div>");
                  }
             });
           }
           $("#action").val(0);
        }
       }
   });
    $('#export_link').click(function(){
        var time_range = DW.submit_data();
        $("#start_time").attr("value", time_range[0]);
        $("#end_time").attr("value", time_range[1]);
        $('#export_form').submit();
    });

    $('#time_filter').click(function() {
        var time_range = DW.submit_data();

        var start_time = time_range[0];
        var end_time = time_range[1];

//        if (start_time && end_time) {
//            var start = new Date(start_time);
//            var end = new Date(end_time);
//            if (end < start) {
//                alert("aaa");
//                return;
//            }
//        }

        $.ajax({
            type: 'GET',
            url: '/project/datarecords/filter',
            data: {'questionnaire_code': $('#questionnaire_id').val(), 'start_time':start_time, 'end_time': end_time},
            success:function(response) {
                if (response) {
                    $('#submission_table').html(response);
                    DW.init_pagination();
                }
            }
        });
    });

    DW.init_pagination();
});

