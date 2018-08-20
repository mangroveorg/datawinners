var initFilters = function() {
    $('#filter_section select').chosen("width: 30%");
    $('#filter_section input.date_filter').each(function() {
        $(this).daterangepicker({
            rangeSplitter: 'to',
            presets: {dateRange: 'Date Range'},
            dateFormat:'dd.mm.yy'
        });
    });
    $("#filter_button").click(function() {
        var report_id = $('#filter_section').attr("report_id");
        $.get(report_id, getFilters(), function(response) {
            $("#report_container").html(response);
        });
    });
}

var prepareExportableFilters = function() {
    var filters = getFilters();
    var transformedFilters = [['Filter Section']];
    Object.keys(filters).forEach(function(key, index) {
        var filterValue = filters[key].split(';')[2];
        if (filterValue) {
            var filterName = $(document.getElementById(key+ "_label")).text();
            filterValue = getLabelForFilterValue(key, filterValue);
            transformedFilters.push([filterName, filterValue]);
        }

    });
    return transformedFilters;
};

var getLabelForFilterValue = function(key, value) {
    // Not using jquery since jquery does not support 'dot' in id
    var filterElement = $(document.getElementById(key));
    var nodeName = filterElement[0].nodeName;
    switch (nodeName) {
        case 'SELECT':
            value = filterElement.find('option:selected').text();
            break;
        default:
            break;
    }
    return value;
};

var getFilters = function() {
    var values = $("#filter_section .filter").get().reduce(function(map, elem) {
            if($(elem).val() != "") {
                map['hasFilter'] = true
            }
            map[elem.id] = $(elem).attr("filter-type") + ";" + $(elem).attr("idnr-type") + ";" + $(elem).val()
            return map;
        }, {'hasFilter': false});
    values.hasFilter ? delete values['hasFilter'] : values = {};
    return values;
};

$(function(){
    initFilters();
});