$(document).ready(function () {
    var $actionBar = $(".action_bar");

    var dt = $('#subjects_table').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "bResetDisplay": true,
        "aLengthMenu": [10, 25, 50, 100],
        "iDisplayLength":25,
        "sDom":"ipfrtipl",
        "sInput":"",
        "aoColumnDefs": [{"bSortable":false,"aTargets":[0]}],
        "oLanguage":{"sInfoFiltered":"",
                     "sLengthMenu":"Show _MENU_ "+subject_type,
                     "sProcessing":"<img class=\"search-loader\"src=\"/media/images/ajax-loader.gif\"></img>","sInfo": "<b>_START_ to _END_</b> of _TOTAL_ " + subject_type,
                     "sInfoEmpty": "Showing 0 to 0 of 0 " + subject_type,
                     "oPaginate": {"sFirst": "", "sPrevious": "◀", "sNext": "▶", "sLast": ""}},
        "sPaginationType": "dw_pagination",
        "sAjaxSource": '/entity/subjects/' + subject_type.toLowerCase() + '/ajax/',
        "sAjaxDataProp": "subjects",
        "sServerMethod": "POST",
        "fnInitComplete":function(oSettings){
            $actionBar.clone(true).insertBefore(".dataTables_info").addClass('margin_top_10').show();
        },
        "aaSorting": [ [2, ["asc","desc"]] ],
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

    $("#subjects_table_filter").find("input").attr('placeholder','Enter any information you want to find')
});

