$(document).ready(function() {

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

    var get_data = function(date_from, date_to, contains, page_number){
        $.get($(window).location,
              {date_from: $('#date_from').val(), date_to: $('#date_to').val(), contains: $('#contains_text').val().trim(), 'filters': JSON.stringify(answer_filters(), null, 2), page_number: page_number, rand: Math.floor(Math.random()*10000000)},
              function(data){
                if(data){
                    $('#results').replaceWith($(data).find('#results'));
                    $('#results a.page_number').unbind('click').click(function(){
                        get_data($('#date_from').val(),$('#date_to').val(), $('#contains_text').val().trim(), $(this).text().trim());
                    });
                }
              }
             );
    };

    $('#add_answer_filter').click(function() {
        $('p input[type=text].answer_filter:last').parent('p').clone().insertAfter($('p input[type=text].answer_filter:last').parent('p'));
    });
    $('#filter').unbind('click').click(function() {
        get_data($('#date_from').val(),$('#date_to').val(), $('#contains_text').val().trim(), 1);
    });
    $('#results a.page_number').unbind('click').click(function(){
        get_data($('#date_from').val(),$('#date_to').val(), $('#contains_text').val().trim(), $(this).text().trim());
    });
});
