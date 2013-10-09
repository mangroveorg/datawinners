$(document).ready(function () {
    var dt = $('#subjects_table').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "bResetDisplay": true,
        "aLengthMenu": [10, 25, 50, 100],
        "iDisplayLength": 25,
        "sDom": "ipfrtipl",
        "sInput": "",
        "aoColumnDefs": [
            { "sClass": "center",
                "sTitle": "<input type='checkbox'id='checkall-checkbox'></input>",
                "fnRender": function (data) {
                    return '<input type="checkbox" value=' + data.aData[data.aData.length - 1] + ' />';
                },
                "aTargets": [0]
            },
            {"bSortable": false, "aTargets": [0]}
        ],
        "oLanguage": {"sInfoFiltered": "",
            "sLengthMenu": gettext("Show") + " _MENU_ "  + subject_type,
            "sProcessing": "<img class=\"search-loader\"src=\"/media/images/ajax-loader.gif\"></img>",
            "sInfo": interpolate(gettext("<b>%(start)s to %(end)s</b> of %(total)s %(subject_type)s(s)"),
                {'start':'_START_','end':'_END_', 'total':'_TOTAL_', 'subject_type':subject_type}, true),
            "sInfoEmpty": gettext("<b> 0 to 0</b> of 0")+ " " + subject_type,
            "sEmptyTable": $('#no_registered_subject_message').clone(true, true).html(),
            "sSearch":"<strong>" + gettext("Search:") + "</strong>",
            "oPaginate": {"sFirst": "", "sPrevious": "◀", "sNext": "▶", "sLast": ""},
            "sZeroRecords": gettext("No matching records found")},
        "sPaginationType": "dw_pagination",
        "sAjaxSource": '/entity/subjects/' + subject_type.toLowerCase() + '/ajax/',
        "sAjaxDataProp": "subjects",
        "sServerMethod": "GET",
        "fnInitComplete": function (oSettings) {
            var cloned_element = $("#action_dropdown").clone(true);
            $("#action_dropdown").remove();
            cloned_element.insertBefore(".dataTables_info").addClass('margin_top_10').removeClass('none');
            new DW.ActionsMenu();
            oSettings.select_all_checkbox = new DW.SubjectSelectAllCheckbox(this);
            $(".styled_table").wrap('<div class="table_container" />');
        },
        "fnPreDrawCallback": function (oSettings) {
            if (oSettings.select_all_checkbox) oSettings.select_all_checkbox.un_check();
        },
        "fnDrawCallback": function (oSettings) {
            $(".styled_table thead input:checkbox").attr("disabled", oSettings.fnRecordsDisplay() == 0);
            var nCols = $('table#subjects_table>thead>tr').children('th').length;
            $('table#subjects_table>tbody').prepend('<tr style="display:none;"><td class ="table_message" colspan=' + nCols+ '><div id="select_all_message"></div></td></tr>');
        },
        "aaSorting": [
            [ $('#subjects_table th.name').index('#subjects_table th'), "asc"]
        ],
        "fnServerData": function (sSource, aoData, fnCallback, oSettings) {
            lastXHR = oSettings.jqXHR;
            lastXHR && lastXHR.abort && lastXHR.abort();
            aoData.push({"name":"disable_cache","value":new Date().getTime()});
            oSettings.jqXHR = $.ajax({
                "dataType": 'json',
                "type": "GET",
                "url": sSource,
                "data": aoData,
                "success": function (result) {
                    $.each(result.subjects, function (i, subject) {
                        subject.unshift('')
                    });
                    fnCallback(result);
                },
                "error": function () {
                },
                "global": false
            });
        }
    });

    $("select[name='subjects_table_length']").change(function () {
        $('#subjects_table').dataTable({"bRetrieve": true}).fnPageChange("first")
    });

    $("#subjects_table_filter").find("input").attr('placeholder', gettext('Enter any information you want to find'));

    $('#subjects_table_filter').live('change', function () {
            new DW.SubjectPagination().disable();
        }
    );
});


