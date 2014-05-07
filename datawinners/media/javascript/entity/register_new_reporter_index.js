$(function(){
    $("#location").catcomplete({source: "/places"});
    ko.applyBindings(new DW.DataSenderQuestionnaire());
});
