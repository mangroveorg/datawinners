$(document).ready(function () {
    var is_advance_questionnaire = is_advance_questionnaire || false;
    if(is_advance_questionnaire == 'False' || is_advance_questionnaire==false){
        new DW.data_submission().init();
    }
});