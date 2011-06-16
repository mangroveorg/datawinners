$(document).ready(function() {
    $("#question-detail-panel > div").hide();
    $('.question_list ol > div:first').toggleClass("question_selected");
    $('.question_list ol > div:first').find(".selected_question_arrow").show();
    $("#question-detail-panel > div.answer1").show();
    $('.question_list ol > div').live("click", function() {
        $("#question-detail-panel > div").hide();
        $('.question_list ol > div').removeClass("question_selected")
        $('.question_list ol > div li span.selected_question_arrow').hide()
        $(this).toggleClass("question_selected");
        $(this).find(".selected_question_arrow").show();

        var question_class = $(this).attr('class').match(/question[0-9]+/);
        var answer_class = question_class[0].replace(/question/, "answer");
        $("#question-detail-panel > div." + answer_class).show();
    });
    $(".add_subject_form").dialog({
        autoOpen: false,
        width: 500,
        modal: true});
    $(".import_subject_form").dialog({
        autoOpen: false,
        width: 500,
        modal: true});
    $("#add_subject").unbind('click').click(function() {
       $(".add_subject_form").dialog("open"); 
    });
    $("#import_subjects").unbind('click').click(function() {
       $(".import_subject_form").dialog("open");
    });
    $('#register_entity').unbind('click').click(function() {
        if ($('#question_form').valid()) {
            var message = {'form_code':'REG',
                't':$('#id_entity_type').val(),
                's':$('#short_name').val(),
                'l':$('#location').val(),
                'd':$('#description').val(),
                'm':$('#mobile_number').val(),
                'n':$('#entity_name').val(),
                'g':$('#geo_code').val()
            }
            var data = {'message':message,'transport': 'web','source': 'web','destination': 'mangrove'}
            $.post('/submit', {'format': 'json', 'data': JSON.stringify(data, null, 1)},
                    function(response) {
                        var d = JSON.parse(response);
                        $('#message').remove();
                        if (d.success) {
                            $('<span id="message" class="success_message">' + d.message + '</span>').insertBefore($('#question_form'));
                            $('#message').delay(10000).fadeOut();
                        }
                        else {
                            $('<span id="message" class="error_message">' + d.message + '</span>').insertBefore($('#question_form'));
                        }
                    }
            );
        }
    }
    );
});
