$(document).ready(function () {

    var dt = $('#subjects_table').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "bResetDisplay": true,
        "aLengthMenu": [10, 25, 50, 100],
        "iDisplayLength":25,
        "sDom":"ipfrtipl",
        "oLanguage":{"sInfoFiltered":"",
                     "sProcessing":"<img class=\"search-loader\"src=\"/media/images/ajax-loader.gif\"></img>","sInfo": "<b>_START_ to _END_</b> of _TOTAL_ Subject",
                     "sInfoEmpty": "Showing 0 to 0 of 0 Subjects",
                     "oPaginate": {"sFirst": "", "sPrevious": "◀", "sNext": "▶", "sLast": ""}},
        "sPaginationType": "dw_pagination",
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

    $("select[name='subjects_table_length']").change(function(){
        $('#subjects_table').dataTable({"bRetrieve":true}).fnPageChange("first")
    });
});

