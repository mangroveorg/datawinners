$(document).ready(function () {

    DW.charCount();
    $('#continue_project').live("click", DW.charCount);
    $('#question_form').live("keyup", DW.charCount);
    $('#question_form').live("click", DW.charCount);
//    $('#question_form').live("click", DW.smsPreview);
    $('.delete').live("click", DW.charCount);
});
