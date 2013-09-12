function reload_tables(responseJSON) {
    $("#subject_table tbody").html('');
    $("#imported_table").html('');
    $.each(responseJSON.all_data, function (index, element) {
        var html = "<td><input type='checkbox' id='" + element.short_code + "' value='" + element.short_code + "'/></td>";
        var datas = element.cols.join("</td><td>");
        html += "<td>" + datas + "</td><td>" + element.projects + "</td><td>" + element.email + "</td>";
        $("#subject_table tbody").append("<tr>" + html + "</tr>");
        if(element.short_code in responseJSON.imported_datasenders){
            $('#imported_table').append("<tr><td>" + datas + "</td></tr>");
        }
    });
}
$(document).ready(function(){
    if ($("div.table_container table#subject_table").length) {
        DW.all_ds_action_dropdown = new DW.action_dropdown({checkall: "#checkall-datasenders"});
    }
});