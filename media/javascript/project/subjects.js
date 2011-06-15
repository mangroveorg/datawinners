$(document).ready(function(){
    $("#question-detail-panel > div").hide();
    $('.question_list ol > div:first').toggleClass("question_selected");
    $('.question_list ol > div:first').find(".selected_question_arrow").show();
    $("#question-detail-panel > div.answer1").show();
    $('.question_list ol > div').live("click", function(){
        $("#question-detail-panel > div").hide();
        $('.question_list ol > div').removeClass("question_selected")
        $('.question_list ol > div li span.selected_question_arrow').hide()
        $(this).toggleClass("question_selected");
        $(this).find(".selected_question_arrow").show();

        var question_class = $(this).attr('class').match(/question[0-9]+/);
        var answer_class = question_class[0].replace(/question/,"answer");
        $("#question-detail-panel > div."+answer_class).show();
    });
});