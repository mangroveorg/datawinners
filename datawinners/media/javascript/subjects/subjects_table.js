$(document).ready(function () {
    var subjects_action_dropdown;
    var select_across_pages_enabled = false;
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
            is_on_trial:true,
            select_all_link:"#select_all_link"
        };
        subjects_action_dropdown = new DW.action_dropdown(kwargs);
    });

    var $actionBar = $(".action_bar");

    var dt = $('#subjects_table').dataTable({
        "bProcessing":true,
        "bServerSide":true,
        "bResetDisplay":true,
        "aLengthMenu":[10, 25, 50, 100],
        "iDisplayLength":25,
        "sDom":"ipfrtipl",
        "sInput":"",
        "aoColumnDefs":[
            { "sClass": "center",
                "sTitle": "<input type='checkbox'id='checkall-checkbox'></input>",
                "fnRender": function (data) {
                    return '<input type="checkbox" value='+ data.aData[5] +' />';
                },
                "aTargets":[0]
            },
            {"bSortable":false, "aTargets":[0]}
        ],
        "oLanguage":{"sInfoFiltered":"",
            "sLengthMenu":"Show _MENU_ " + subject_type,
            "sProcessing":"<img class=\"search-loader\"src=\"/media/images/ajax-loader.gif\"></img>",
            "sInfo":"<b>_START_ to _END_</b> of _TOTAL_ " + subject_type,
            "sInfoEmpty":"<b> 0 to 0</b> of 0 " + subject_type,
            "oPaginate":{"sFirst":"", "sPrevious":"◀", "sNext":"▶", "sLast":""}},
        "sPaginationType":"dw_pagination",
        "sAjaxSource":'/entity/subjects/' + subject_type.toLowerCase() + '/ajax/',
        "sAjaxDataProp":"subjects",
        "sServerMethod":"GET",
        "fnInitComplete":function (oSettings) {
            $actionBar.clone(true).insertBefore(".dataTables_info").addClass('margin_top_10').show();
            select_across_pages_enabled = false;
        },
        "fnPreDrawCallback":function (oSettings) {
            if (!select_across_pages_enabled) {
                subjects_action_dropdown.uncheck_all();
                deactivate_select_across_pages();
            }
        },
        "fnDrawCallback":function (oSettings) {
            if (select_across_pages_enabled) {
                subjects_action_dropdown.check_all();
            }
            subjects_action_dropdown.update_edit_action();
        },
        "aaSorting":[
            [1, ["asc", "desc"]]
        ],
        "fnServerData":function (sSource, aoData, fnCallback, oSettings) {
            oSettings.jqXHR = $.ajax({
                "dataType": 'json',
                "type": "GET",
                "url": sSource,
                "data": aoData,
                "success": fnCallback,
                "error": function () {
                },
                "global":false
            });
        }
    });
    $("select[name='subjects_table_length']").change(function () {
        $('#subjects_table').dataTable({"bRetrieve":true}).fnPageChange("first")
    });

    $("#subjects_table_filter").find("input").attr('placeholder', 'Enter any information you want to find');

    $("#checkall-checkbox").click(function (event) {
        self = event.target;
        $("table.styled_table tbody input:checkbox").attr('checked', $(self).is(":checked"));
        if ($(self).is(":checked")) {
            var no_of_records_on_page = dt.fnGetData().length;
            var total_number_of_records = dt.fnSettings().fnRecordsDisplay()
            if (no_of_records_on_page != total_number_of_records) {
                display_select_across_pages_message(no_of_records_on_page,total_number_of_records);
            }
        }
        else {
            deactivate_select_across_pages();
        }
    });

    function display_select_across_pages_message(no_of_records_on_page,total_number_of_records) {
        if (no_of_records_on_page != total_number_of_records) {
            select_all_link = "<a id='select_all_link' class=''> Select all <b>" + total_number_of_records + "</b> subjects</a>"
            select_across_pages_message = "All <b>" + no_of_records_on_page + "</b> Subjects on this page are selected." + select_all_link;
            $("#subjects_table").before("<div id='select_all_message'>" + select_across_pages_message + "</div>");

            $('#select_all_link').click(function () {
                select_across_pages_enabled = true;
                $('#select_all_link').addClass('selected');
                subjects_action_dropdown.update_edit_action();
            });
        }
    }

    $('#subjects_table_filter').keyup(function () {
        deactivate_select_across_pages();
    })

    function deactivate_select_across_pages() {
        $("#select_all_message").remove();
        select_across_pages_enabled = false;
        $('#select_all_link').removeClass('selected');
    }
});


