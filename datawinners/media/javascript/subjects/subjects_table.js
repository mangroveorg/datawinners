$(document).ready(function () {
    var subjects_action_dropdown;
    $("#all_subjects .list_header").each(function (i) {
        var container = document;
        var data_locator_id = $("div.action", container).attr("id");
        var kwargs = {
            container:container,
            checkbox_locator:"table.styled_table input:checkbox",
            check_single_checked_locator:".styled_table tbody input:checkbox[checked=checked]",
            no_cb_checked_locator:".styled_table input:checkbox[checked=checked]",
            edit_link_locator:"div.action ul li a.edit",
            checkall:".styled_table thead input:checkbox",
            is_on_trial:true
        };
        subjects_action_dropdown = new DW.action_dropdown(kwargs);
    });

    var $actionBar = $(".action_bar");

    var dt = $('#subjects_table').dataTable({
        "bProcessing": true,
        "bServerSide": true,
        "bResetDisplay": true,
        "aLengthMenu": [10, 25, 50, 100],
        "iDisplayLength": 25,
        "sDom": "ipfrtipl",
        "sInput": "",
        "aoColumnDefs": [
            {"bSortable": false, "aTargets": [0]}
        ],
        "oLanguage": {"sInfoFiltered": "",
            "sLengthMenu": "Show _MENU_ " + subject_type,
            "sProcessing": "<img class=\"search-loader\"src=\"/media/images/ajax-loader.gif\"></img>",
            "sInfo": "<b>_START_ to _END_</b> of _TOTAL_ " + subject_type,
            "sInfoEmpty": "<b> 0 to 0</b> of 0 " + subject_type,
            "oPaginate": {"sFirst": "", "sPrevious": "◀", "sNext": "▶", "sLast": ""}},
        "sPaginationType": "dw_pagination",
        "sAjaxSource": '/entity/subjects/' + subject_type.toLowerCase() + '/ajax/',
        "sAjaxDataProp": "subjects",
        "sServerMethod": "GET",
        "fnInitComplete": function (oSettings) {
            $actionBar.clone(true).insertBefore(".dataTables_info").addClass('margin_top_10').show();
        },
        "fnPreDrawCallback": function (oSettings) {
            subjects_action_dropdown.uncheck_all();
        },
        "fnDrawCallback": function (oSettings) {
            subjects_action_dropdown.update_edit_action();
        },
        "aaSorting": [ [2, ["asc","desc"]] ],
        "fnServerData": function (sSource, aoData, fnCallback, oSettings) {
            oSettings.jqXHR = $.ajax({
                "dataType": 'json',
                "type": "GET",
                "url": sSource,
                "data": aoData,
                "success": fnCallback,
                "error": function () {
                },
                "global": false
            });
        }
    });
    $("select[name='subjects_table_length']").change(function () {
        $('#subjects_table').dataTable({"bRetrieve": true}).fnPageChange("first")
    });

    $("#subjects_table_filter").find("input").attr('placeholder','Enter any information you want to find');
});

