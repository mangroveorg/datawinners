var loadReportTabCallback = function(anchorElement, response) {
    $("#report_navigation li.active").addClass("inactive");
    $("#report_navigation li.active").removeClass("active");
    anchorElement.parent().addClass("active");
    $("#report_container").html(response);
};

$(function(){
    $("#report_navigation a").click(function(){
        var anchorElement = $(this);
        $.get(anchorElement.attr("id")).done(function(response) {
            loadReportTabCallback(anchorElement, response);
        });
    });

    $(document).ajaxStart(function() {
        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
    });

    $( document ).ajaxStop(function() {
        $.unblockUI();
    });

    $("#report_navigation a")[0].click();
});