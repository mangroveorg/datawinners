$(document).ready(function () {
    $('#datasender_table').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "bResetDisplay": true,
        "aLengthMenu": [5, 25, 50, 100],
        "iDisplayLength": 5,
        "sDom": "ipfrtipl",
        "sInput": "",
        "aoColumnDefs": [
            { "sClass": "center",
                "sTitle": "<input type='checkbox'id='checkall-checkbox'></input>",
                "fnRender": function (data) {
                    return '<input type="checkbox" value=' + data.aData[2] + ' />';
                },
                "aTargets": [0]
            },
            {"bSortable": false, "aTargets": [0, $('#datasender_table th.devices').index('#datasender_table th')]}
        ],
        "oLanguage": {"sInfoFiltered": "",
            "sLengthMenu": gettext("Show") + " _MENU_ " + gettext("Data Senders"),
            "sProcessing": "<img class=\"search-loader\"src=\"/media/images/ajax-loader.gif\"></img>",
            "sInfo": interpolate(gettext("<b>%(start)s to %(end)s</b> of %(total)s %(subject_type)s(s)"),
                {'start': '_START_', 'end': '_END_', 'total': '_TOTAL_', 'subject_type': "Data Senders"}, true),
            "sInfoEmpty": gettext("<b> 0 to 0</b> of 0") + " " + gettext("Data Senders"),
//            "sEmptyTable": $('#no_registered_subject_message').clone(true, true).removeAttr("hidden").html(),
            "sSearch": "<strong>" + gettext("Search:") + "</strong>",
            "oPaginate": {"sFirst": "", "sPrevious": "◀", "sNext": "▶", "sLast": ""}},
        "sPaginationType": "dw_pagination",
        "sAjaxSource": '/entity/datasenders/ajax/',
        "sAjaxDataProp": "datasenders",
        "sServerMethod": "GET",
        "aaSorting": [
            [ 1, "asc"]
        ],
        "fnServerData": function (sSource, aoData, fnCallback, oSettings) {
            lastXHR = oSettings.jqXHR;
            lastXHR && lastXHR.abort && lastXHR.abort();
            oSettings.jqXHR = $.ajax({
                "dataType": 'json',
                "type": "GET",
                "url": sSource,
                "data": aoData,
                "success": function (result) {
                    $.each(result.datasenders, function (i, datasender) {
                        datasender.unshift('')
                    });
                    fnCallback(result);
                },
                "error": function () {
                },
                "global": false
            });
        }
    });
});