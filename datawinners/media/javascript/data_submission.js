$(document).ready(function () {
    if(typeof advance_questionnaire === "undefined"){
        is_advance_questionnaire = 'False'
    }else
        is_advance_questionnaire = advance_questionnaire;
    if(is_advance_questionnaire == 'False'){
        new DW.data_submission().init();
    }
});