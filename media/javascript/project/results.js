(function(){
    DW.show_data = function(page_number){
        //        this.date_from = $('#date_from').val();
        //        this.date_to = $('#date_to').val();
        //        this.contains =$('#contains_text').val().trim();
        this.page_number = page_number;
        this._init();
        this._addAnswerFilter();
    }
    DW.show_data.prototype = {
        _init : function(){
            $.get(window.location,
                  {
//                      date_from: this.date_from,
//                      date_to: this.date_to,
//                      contains: this.contains,
                      'filters': JSON.stringify(this._answerFilter(), null, 2),
                      page_number: this.page_number,
                      rand: Math.floor(Math.random()*10000000)
                  },
                  function(data){
                    if(data){
                        $('#results').replaceWith($(data).find('#results'));
                    }
                  }
                 );
            },
        _answerFilter : function(){
            var filters = [];
            $('p:has(input[type=text].answer_filter)').each(function(){
                var p = $(this);
                if(p.find('input.answer_filter').val().trim().length > 0){
                    filters.push({code: p.find('select').val(), answer: p.find('input.answer_filter').val().trim()});
                }
            });
            return filters
        },
        _addAnswerFilter : function(){
            $('#add_answer_filter').click(function() {
                $('li input[type=text].answer_filter:last').parent('li').clone().insertAfter($('li input[type=text].answer_filter:last').parent('li'));
            });
        }
    }

})();

$(document).ready(function(){

    $.ajaxSetup({ cache: false });
    var screen_width = $(window).width() - 50;
     $("#data_record").wrap("<div class='data_table' style='width:"+screen_width+"px'/>")
    DW.wrap_table = function() {
        $("#data_analysis").wrap("<div class='data_table' style='width:"+screen_width+"px'/>")
    };
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
                earliestDate:'1/1/2011', latestDate:'21/12/2012', dateFormat:'dd-mm-yy', rangeSplitter:'/'

            });

    //Checkbox on/off functionality
    $("#master_checkbox").live("click", function(){
        $(".selected_submissions").each(function(){
           $(this).attr("checked", !$(this).attr('checked'))
        })

    })
    DW.current_page = 0;
    //$('#total_rows').val() is the total number of results which needs to be sent for every pagination click(total_rows).val(), don't take that out
    $("#pagination").pagination($('#total_rows').val().trim(),{
        items_per_page:10,
        num_display_entries : 5,
        num_edge_entries:2,
        callback : function(page_number) {
            new DW.show_data(page_number + 1);
            DW.current_page = page_number + 1
        }
    });
    $('#action').change(function(){
       var ids = [];
       if($(".selected_submissions:checked").length == 0){
            $("#message_text").html("<span class='error_message'>" + "Please select atleast one undeleted record" + "</span>");
            $('#action').val(0);
       }
       else{
       $(".selected_submissions:checked").each(function(){
           if($(this).val()!="None")
                ids.push($(this).val());
       });
       if(ids.length==0){
            $("#message_text").html("<span class='error_message'>" + "This data has already been deleted" + "</span>");
            $('#action').val(0);
       }
       else{
            var answer = confirm("Are you sure you want to delete the selected record/s?");
           if(answer){
               $.ajax({
                  type: 'POST',
                  url: window.location.pathname + "?rand="+ new Date().getTime(),
                  data:  {'id_list': JSON.stringify(ids), 'current_page':DW.current_page},
                  success:function(response) {
                               $('#submission_table').empty();
                               $('#submission_table').append(response);
                               $('#action').val(0);

                    },
                 error: function(e) {
                    $("#message_text").html("<span class='error_message'>" + e.responseText + "</span>");
                    $('#action').val(0);
                }
             });
           }
           else $("action").val(0);
        }
       }
   });
   DW.submit_data = function() {
        var time_range = $("#dateRangePicker").val().split("/");
        if(time_range[0] == ""){
            time_range[0]='01-01-1996';
            time_range[1]=Date.parse('today').toString('dd-MM-yyyy');
            return time_range;
        }
        if (time_range[0] != "Click to select a date range" && Date.parse(time_range[0]) == null) {
            $("#dateErrorDiv").html('<label class=error>' + "Enter a correct date. No filtering applied" + '</label>')
            $("#dateErrorDiv").show();
            time_range[0] = "";
            time_range[1] = "";
        }
        return time_range;
   };
    $('#export_link').click(function(){
//        var path = window.location.pathname;
//        var element_list = path.split("/");
//        $("#questionnaire_code").attr("value", element_list[element_list.length - 2]);
        var time_range = DW.submit_data()
        $("#start_time").attr("value", time_range[0]);
        $("#end_time").attr("value", time_range[1]);
        $('#export_form').submit();
    });

    $('#time_filter').click(function() {
        var time_range = DW.submit_data()
        $.ajax({
            type: 'POST',
            url: '/project/datarecords/filter',
            data: {'questionnaire_code': $('#questionnaire_id').val(), 'start_time':time_range[0], 'end_time': time_range[1]},
            success:function(response) {
                if (response) {
                    $('#results').html(response);
                }
            }
        });
    });
});

