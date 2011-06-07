(function(){
    DW.show_data = function(page_number){
        this.date_from = $('#date_from').val();
        this.date_to = $('#date_to').val();
        this.contains =$('#contains_text').val().trim();
        this.page_number = page_number;
        this._init();
        this._addAnswerFilter();
    }
    DW.show_data.prototype = {
        _init : function(){
            $.get($(window).location,
                  {
                      date_from: this.date_from,
                      date_to: this.date_to,
                      contains: this.contains,
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

    // For filtering results,right now its incomplete
    $('#filter').unbind('click').click(function() {
        new show_data(1);
    });

    //$('#total_rows').val() is the total number of results which needs to be sent for every pagination click(total_rows).val(), don't take that out
    $("#pagination").pagination($('#total_rows').val().trim(),{
        items_per_page:10,
        num_display_entries : 5,
        num_edge_entries:2,
        callback : function(page_number) {
            new DW.show_data(page_number + 1);
        }
    });
    
});

