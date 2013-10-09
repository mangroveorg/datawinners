$(document).ready(function () {
    $('#datasender_table').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "sAjaxSource": '/entity/datasenders/ajax/',
        "sAjaxDataProp": "results",
        "sServerMethod": "GET",
        "aLengthMenu": [5, 25, 50, 100],
        "iDisplayLength": 5,
        "bPaginate": true,
        "sPaginationType": "full_numbers",
        "fnServerData": function (sSource, aoData, fnCallback, oSettings) {
            oSettings.jqXHR = $.ajax({
                "dataType": 'json',
                "type": "GET",
                "url": sSource,
                "data": aoData,
                "success": fnCallback
            });
        }
    });
});