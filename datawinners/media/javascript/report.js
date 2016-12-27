$(function(){
    var pageSize = 25;
    var data = [];
    var totalCount, currentPageCount;

    var initPaginationWidget = function(anchorElement, pageSize, count, totalCount) {
        var loadData = function (pageNumber, callback) {
            updateCurrentPageData(pageNumber - 1);
            callback(currentPageCount);
        };

        $("#report_container>.pagination_container").empty();
        $("#report_container>.pagination_container").append('<div id="pagination-' + anchorElement.attr("id") + '"></div>');
        new PaginationWidget('#pagination-' + anchorElement.attr("id"), loadData, loadData, pageSize, currentPageCount, totalCount);
    };

    var preparePaginatedData = function(htmlData, sortColumns) {
        var DOM = $(htmlData);
        data = DOM.find('tr:has(td)');
        DOM.find('tr:has(td)').remove();
        totalCount = data.length;
        if (sortColumns.length) {
            data = doSort(data, sortColumns);
        }

        $("#report_container>.report_content").html(DOM);
    };

    var doSort = function(htmlData, sortColumns) {
        var obj = prepareSortObject(sortColumns, data);
        var sortedKeys = Object.keys(obj).sort(function(prev, next){ return prev < next ? -1 : prev == next ? 0 : 1 });
        return sortedData = sortedKeys.reduce(function(acc, key) { return acc.concat(obj[key]); }, []);
    };

    var prepareSortObject = function(sortColumns, htmlData) {
        var obj = {};
        htmlData.each(function(i, element) {
            var key = sortColumns.reduce(function(acc, colIndex) { return acc + $($(element).find('td')[colIndex]).text() }, "").toLowerCase();
            if (!obj[key]) {
                obj[key] = [];
            }
            obj[key].push(element);
        });
        return obj;
    };

    var loadReportTabCallback = function(anchorElement, response) {
        $("#report_navigation li.active").addClass("inactive");
        $("#report_navigation li.active").removeClass("active");
        anchorElement.parent().addClass("active");
        preparePaginatedData(response.content, response.sortColumns);
        updateCurrentPageData(0);
        initPaginationWidget(anchorElement, pageSize, currentPageCount, totalCount);
    };

    var updateCurrentPageData = function (pageNumber = 0) {
        var currentPageData = data.slice((pageNumber*pageSize), (pageNumber*pageSize) + pageSize);
        $("#report_container>.report_content").find('table').find('tr:has(td)').remove();
        $("#report_container>.report_content").find('table').append(currentPageData);
        currentPageCount = currentPageData.length;
    };

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