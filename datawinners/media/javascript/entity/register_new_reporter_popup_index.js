$(document).on('init-questionnaire', "#datasender_reg_popup_section", function(){
    $("#datasender_reg_popup_section #location").catcomplete({source: "/places"});
    ko.applyBindings(new DW.DataSenderQuestionnaire(), $("#datasender_reg_popup_section")[0]);
});