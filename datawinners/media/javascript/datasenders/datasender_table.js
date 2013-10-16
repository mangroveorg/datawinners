$(document).ready(function () {
    $("#datasender_table_filter").find("input").attr('placeholder', gettext('Enter any information you want to find'));
});

DW.DataSenderTable = function (options){
      var name_column_index = 1;
      var checkbox_column_index = 0;
      $('#datasender_table').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "bResetDisplay": true,
        "aLengthMenu": [10, 25, 50, 100],
        "iDisplayLength": 25,
        "sDom": "ipfrtipl",
        "sInput": "",
        "aoColumnDefs": [
            { "sClass": "center",
                "fnRender": function (data) {
                    return '<input type="checkbox" value=' + data.aData[2] + ' />';
                },
                "aTargets": [checkbox_column_index]
            },
            {"bSortable": false, "aTargets": options.non_sortable_columns}
        ],
        "oLanguage": {"sInfoFiltered": "",
            "sLengthMenu": gettext("Show") + " _MENU_ " + gettext("Data Senders"),
            "sProcessing": "<img class=\"search-loader\"src=\"/media/images/ajax-loader.gif\"></img>",
            "sInfo": interpolate(gettext("<b>%(start)s to %(end)s</b> of %(total)s datasenders"),
                {'start': '_START_', 'end': '_END_', 'total': '_TOTAL_'}, true),
            "sInfoEmpty": gettext("<b> 0 to 0</b> of 0") + " " + gettext("Data Senders"),
            "sSearch": "<strong>" + gettext("Search:") + "</strong>",
            "oPaginate": {"sFirst": "", "sPrevious": "◀", "sNext": "▶", "sLast": ""}},
        "sPaginationType": "dw_pagination",
        "sAjaxSource": options.url,
        "sAjaxDataProp": "datasenders",
        "sServerMethod": "GET",
        "aaSorting": [
            [  name_column_index, "asc"]
        ],
        "fnInitComplete": function (oSettings) {
            var cloned_element = $("#action_dropdown").clone(true);
            $("#action_dropdown").remove();
            cloned_element.insertBefore(".dataTables_info").addClass('margin_top_10').find('.action_button').removeClass('none');
            var kwargs = {select_all_text: "Select all <b> %(total_number_of_records)s </b>datasenders",
                current_selected_text: "You have selected <b>%(number_of_records)s</b> Datasenders on this page.",
                all_entities_selected_text: "All %(total_number_of_records)s Datasenders selected."};

            oSettings.select_all_checkbox = new DW.EntitySelectAllCheckbox(this, kwargs);
            $(".styled_table").wrap('<div class="table_container" />');
        },

        "fnPreDrawCallback": function (oSettings) {
            if (oSettings.select_all_checkbox) oSettings.select_all_checkbox.un_check();
        },
        "fnDrawCallback": function (oSettings) {
            $(".styled_table thead input:checkbox").attr("disabled", oSettings.fnRecordsDisplay() == 0);
            var nCols = $('table#datasender_table>thead>tr').children('th').length;
            $('table#datasender_table>tbody').prepend('<tr style="display:none;"><td class ="table_message" colspan=' + nCols+ '><div id="select_all_message"></div></td></tr>');
        },
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
    })
};