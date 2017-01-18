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