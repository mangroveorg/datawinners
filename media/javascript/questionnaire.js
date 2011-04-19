// vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
$(document).ready(function(){

    $('#add-question').click(function(){
        // Copy question template to question
        var question = $('#question-template').clone().removeAttr('id').show();
        //Append the question to question list and detail to the detail
        var questionDetail = question.find('.question-detail').clone().removeClass('hide');
        $('#question-detail-panel').empty();
        $('#questions-panel').append(question);
        $('#question-detail-panel').append(questionDetail);

        $('#question-detail-panel .update-question').unbind('click').click(function(){
            question.find('.question-detail').replaceWith($('#question-detail-panel .question-detail').clone(true).hide());
            question.find('.question-master span.question-title').text(question.find('.question-detail input.question-title').val());
            question.find('.question-master span.question-code').text(question.find('.question-detail input.question-code').val());
        });

        question.find('.question-master a.question-link').unbind('click').click(function(){
            $('#question-detail-panel').empty();
            $('#question-detail-panel').append(question.find('.question-detail').clone(true).show());
            var option= question.find('#question-detail input[type=radio]:checked').val();
            $('#question-detail-panel input[type=radio][value=' + option + ']').checked();
        });
        
        $('#question-detail-panel input[value!=multiplechoice][type=radio]').unbind('click').click(function(){
            $('#question-detail-panel .choices').hide();
        });
        
        $('#question-detail-panel input[value=multiplechoice][type=radio]').unbind('click').click(function(){
            $('#question-detail-panel .choices input').remove();
            $('#question-detail-panel .choices').show();
            $('#question-detail-panel .choices .add-choice-link').unbind('click').click(function(){
                $('<p><input class="answer-choice"></p>').insertBefore($(this));
            });
        });
    });
})