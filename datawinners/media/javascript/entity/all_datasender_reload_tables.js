function reload_tables(responseJSON) {
//    $("#subject_table tbody").html('');
    $("#imported_table").html('');
    $.each(responseJSON.all_data, function (index, element) {
        var datas = element.cols.join("</td><td>");
        if (element.short_code in responseJSON.imported_datasenders) {
            $('#imported_table').append("<tr><td>" + datas + "</td></tr>");
        }
    });
}
$(document).ready(function () {
//    if ($("div.table_container table#datasender_table").length) {
    var kwargs = {
        checkbox_locator: "#datasender_table input:checkbox",
        many_selected_msg: gettext("Please select only 1 Data Sender"),
        check_single_checked_locator: "#datasender_table tbody input:checkbox[checked=checked]",
        no_cb_checked_locator: "#datasender_table input:checkbox[checked=checked]",
        edit_link_locator: "#edit",
        container: document,
        checkall: "#checkall-datasenders"
    }
    DW.all_ds_action_dropdown = new DW.action_dropdown(kwargs);
//    }
});