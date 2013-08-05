$(document).ready(function () {

    $('#subjects_table').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "aLengthMenu": [10, 25, 50],
        "sPaginationType": "four_button",
        "sAjaxSource": window.location.pathname + 'ajax/',
        "sAjaxDataProp": "subjects",
        "sServerMethod": "POST",
        "aaSorting": [ [1, "asc", 0] ],
        "fnServerData": function (sSource, aoData, fnCallback, oSettings) {
            oSettings.jqXHR = $.ajax({
                "dataType": 'json',
                "type": "POST",
                "url": sSource,
                "data": aoData,
                "success": fnCallback,
                "error": function () {
                },
                "global": false
            });
        }
    });
});

