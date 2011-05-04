$(document).ready(function() {
    $('#add_answer_filter').click(function() {
        $('p input[type=text].answer_filter:last').parent('p').clone().insertAfter($('p input[type=text].answer_filter:last').parent('p'));
    });
    $('#filter').click(function() {
        var answer_filters = function(){
            var filters = [];
            $('p:has(input[type=text].answer_filter)').each(function(){
                var p = $(this);
                if(p.find('input.answer_filter').val().trim().length > 0){
                    filters.push({question_code: p.find('select').val(), answer: p.find('input.answer_filter').val().trim()});
                }
            });
            return filters;
        };
        $.get($(window).location,
              {date_from: $('#date_from').val(), date_to: $('#date_to').val(), contains: $('#contains_text').val().trim(), filters: answer_filters()},
              function(data){
                if(data){
                    $('#results').replaceWith($(data).find('#results'));
                }
              }
             );
    });
});
