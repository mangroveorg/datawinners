var pageSize = 25;
var currentPageCount;

var updateCurrentPageData = function (pageNumber, rows) {
    var currentPageData = rows.slice((pageNumber*pageSize), (pageNumber*pageSize) + pageSize);
    $("#report_container").find('table').find('tr:has(td)').remove();
    $("#report_container").find('table').append(currentPageData);
    currentPageCount = currentPageData.length;
};

var initPaginationWidget = function(report_id, rows) {
    var loadData = function (pageNumber, callback) {
        updateCurrentPageData(pageNumber - 1, rows);
        callback(currentPageCount);
    };
    new PaginationWidget('#pagination-' + report_id, loadData, loadData, pageSize, currentPageCount, rows.length);
};