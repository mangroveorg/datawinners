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
            $.get($(window).location,
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

    $("#dateRangePicker").daterangepicker( { presetRanges: [
        {text: 'Past 7 days', dateStart: 'last week', dateEnd: 'Today' },
        {text: 'Past 30 days', dateStart: 'last month', dateEnd: 'Today' },
        {text: 'Past year', dateStart: 'last year', dateEnd: 'Today'}],
        earliestDate:'1/1/2011', latestDate:'12/21/2012'
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
        items_per_page:4,
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
});

