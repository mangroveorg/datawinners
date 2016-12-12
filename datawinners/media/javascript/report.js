$(function(){
    var initPaginationWidget = function(anchorElement, pageSize, count, totalCount) {
        var loadData = function (pageNumber, callback) {
            $.get(anchorElement.attr("id"), {page_number: pageNumber}).done(function(response) {
                $("#report_container>.report_content").html(response.content);
                callback && callback(response.count);
            });
        };

        $("#report_container>.pagination_container").append('<div id="pagination-' + anchorElement.attr("id") + '"></div>');
        new PaginationWidget('#pagination-' + anchorElement.attr("id"), loadData, loadData, pageSize, count, totalCount);
    };

    var initFilters = function(anchorElement) {
        $('#report_container>.filter_container select').chosen();
        $('#report_container>.filter_container input.date_filter').each(function() {
            $(this).daterangepicker({
                rangeSplitter: 'to',
                presets: {dateRange: 'Date Range'},
                dateFormat:'dd-mm-yy'
            });
        });
        $("#filter_button").click(function() {
            var values = $("#report_container>.filter_container .filter").get().reduce(function(map, elem) {
                map[elem.id] = $(elem).attr("filter-type") + ";" + $(elem).attr("idnr-type") + ";" + $(elem).val()
                return map;
            }, {});
            $.get(anchorElement.attr("id"), values).done(function(response) {
                $("#report_container>.report_content").html(response.content);
            });
        });
    }

    var loadReportTabCallback = function(anchorElement, pageSize, count, totalCount) {
        $("#report_navigation li.active").addClass("inactive");
        $("#report_navigation li.active").removeClass("active");
        anchorElement.parent().addClass("active");
        initPaginationWidget(anchorElement, pageSize, count, totalCount);
    };

    $("#report_navigation a").click(function(){
        var anchorElement = $(this);
        $("#report_container>.pagination_container").empty();
        $("#report_container>.filter_container").load(anchorElement.attr("id") + "/filters/", function(){
            initFilters(anchorElement);
        });
        $.get(anchorElement.attr("id")).done(function(response) {
          $("#report_container>.report_content").html(response.content);
          loadReportTabCallback(anchorElement, response.pageSize, response.count, response.totalCount);
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