$(document).ready(function(){
     //The Questionnarie left navigation toggle functions
    $("#questions-panel .add_question .add_link").click(function() {
        $('.question_list ol > div:last').toggleClass("question_selected");
        $('.question_list ol > div:last').find(".selected_question_arrow").show();
    });
    $('.question_list ol > div:first').toggleClass("question_selected");
    $('.question_list ol > div:first').find(".selected_question_arrow").show();

    $('.question_list ol div .delete_link').live("click", function(event) {
        event.stopPropagation();
        if ($('#question_form').valid()) {
            $('.question_list ol > div:first').toggleClass("question_selected");
        }
    });


    $('.question_list ol > div').live("click", function() {
        var selected = $(this).index() + 1;
        var selected_div = $('.question_list ol').find("div:nth-child(" + selected + ")");
        if ($('#question_form').valid()) {
            selected_div.toggleClass("question_selected");
            selected_div.find(".selected_question_arrow").show();
        }
    });
})