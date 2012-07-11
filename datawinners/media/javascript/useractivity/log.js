/**
 * Created by PyCharm.
 * User: herihaja
 * Date: 7/4/12
 * Time: 7:06 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    $("#dateRangePicker").daterangepicker({
        presetRanges: [],
        presets: {dateRange: gettext('Date Range')},
        dateFormat:'dd-mm-yy',
        rangeSplitter:gettext("to")
    });

    $('#log_data').dataTable({
        "bDestroy":false,
        "bRetrieve": true,
        "sPaginationType": "full_numbers",
        "aaData": log_data,
        "bFilter": false,
        "bLengthChange": false,
        "bSort": false,
        "asStripClasses": false,
        "iDisplayLength": 20,
        "oLanguage":{
            "sProcessing": gettext("Processing..."),
                "sLengthMenu": gettext("Show _MENU_ Data records"),
                "sZeroRecords": gettext("No matching records found"),
                "sEmptyTable": gettext("No data available in table"),
                "sLoadingRecords": gettext("Loading..."),
                "sInfo": gettext("Showing _START_ to _END_ of _TOTAL_ Data records"),
                "sInfoEmpty": gettext("Showing 0 to 0 of 0 Data records"),
                "sInfoFiltered": gettext("(filtered from _MAX_ total Data records)"),
                "sInfoPostFix": "",
                "sSearch": gettext("Search:"),
                "sUrl": "",
                "oPaginate": {
                    "sFirst":    gettext("First"),
                    "sPrevious": gettext("Previous"),
                    "sNext":     gettext("Next"),
                    "sLast":     gettext("Last")
                },
                "fnInfoCallback": null
        }
    });
});