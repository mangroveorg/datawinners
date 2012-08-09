$(document).ready(function(){
    $("#dateRangePicker").daterangepicker({
        presetRanges: [],
        presets: {dateRange: gettext('Date Range')},
        dateFormat:'dd-mm-yy',
        rangeSplitter:gettext("to")
    });

    $('#exportProjectBtn').click(function() {
        var questionnaire_code = $("#project_select").val();
        var time_range = getDateRange();
        var download_link = '/api/get_for_form/'+questionnaire_code +
            (time_range[0] == null ? '': '/'+time_range[0]) +
            (time_range[1] == null ? '': '/'+time_range[1]);

        window.location.href = download_link;
    });

    function getDateRange() {
        var results=[null, null]

        var time_range = $("#dateRangePicker").val().split("to");
        if(time_range.length == 2){
         var start_date = Date.parse(time_range[0]);
         var end_date = Date.parse(time_range[1]);
            console.log(start_date);
            console.log(end_date);

            if(start_date == null) return results;
            results[0] =time_range[0].trim();
            if(end_date == null) return results;
            results[1] =time_range[1].trim();
            return results;
        }
        return results;
    };

});