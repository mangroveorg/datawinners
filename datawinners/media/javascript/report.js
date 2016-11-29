$(function(){
    var initPaginationWidget = function(anchorElement) {
        var loadData = function (pageNumber, callback) {
            $("#report_container>.report_content").load($('#report_navigation li.active a').attr('id') + "?page_number=" + pageNumber);
        };
        $("#report_container>.pagination_container").append('<div id="pagination-' + anchorElement.attr("id") + '"></div>');
        new PaginationWidget('#pagination-' + anchorElement.attr("id"), loadData, loadData);
    };

    var loadReportTabCallback = function(anchorElement) {
        $( document ).ajaxComplete(function() {
          $.unblockUI();
        });
        $("#report_navigation li.active").addClass("inactive");
        $("#report_navigation li.active").removeClass("active");
        anchorElement.parent().addClass("active");
        initPaginationWidget(anchorElement);
        $('#report_container>.report_content select').chosen({width: "20%"});
    };

    $("#report_navigation a").click(function(){
        var anchorElement = $(this);
        $("#report_container>.pagination_container").empty();
        $("#report_container>.report_content").load(anchorElement.attr("id"), function() {loadReportTabCallback(anchorElement);});
        $(document).ajaxStart(function() {
            $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
        });
    });

    initPaginationWidget($('#report_navigation li.active a'));

    $('#report_container>.report_content select').chosen();

    $('input.filter').daterangepicker({
        rangeSplitter: 'to',
        presets: {dateRange: 'Date Range'},
        dateFormat:'dd-mm-yy'
    });
});