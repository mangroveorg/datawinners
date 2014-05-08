$(document).on('init-edit-reporter-questionnaire', "#edit_data_sender_form", function(){
    $("#edit_data_sender_form #location").catcomplete({source: "/places"});
    var editDataSenderQuestionnaire = new DW.EditDataSenderQuestionnaire();
    editDataSenderQuestionnaire.init(reporterDetails);
    window.model = editDataSenderQuestionnaire;
    ko.applyBindings(editDataSenderQuestionnaire, $("#edit_data_sender_form")[0]);
});