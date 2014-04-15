$(function () {
    $.ajaxSetup({ cache: false });
    $('#page_hint_section').text($('#page_hint').find('>div:first').text());
    $(".ui-corner-all").removeClass("ui-corner-all");
    $(".ui-corner-top").removeClass("ui-corner-top");

    new DW.SubmissionAnalysisView().init();
    new DW.FilterSection().init();
});