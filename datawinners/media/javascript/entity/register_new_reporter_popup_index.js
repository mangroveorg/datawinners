$(document).on('init-questionnaire', "#datasender_reg_popup_section", function(){
    $("#datasender_reg_popup_section #location").catcomplete({source: "/places"});
    var dataSenderQuestionnaire = new DW.DataSenderQuestionnaire();
    dataSenderQuestionnaire.init();
    dataSenderQuestionnaire.showCancelLink(true);
    ko.applyBindings(dataSenderQuestionnaire, $("#datasender_reg_popup_section")[0]);
});