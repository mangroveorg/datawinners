$(document).ready(function () {
   // $('#all_subjects .subject-container').hide();

  /*  $('#all_subjects .list_header').click(function () {
        $(this).toggleClass('highlight').siblings('.list_header').removeClass('highlight');
        $('#all_subjects .subject-container:visible').not($(this).next()).hide();
        $(this).next().slideToggle('fast').scrollTop(0);
    });*/

    /*$(".checkall-subjects").bind("click", function(){
        var type = $(this).attr("id").substr(9);

        var checked = $(this).attr("checked") == "checked";

        $($.sprintf("#%s-table tr td:first-child input:checkbox", type)).attr("checked", checked);
    });

    $(".subject-container table tbody tr td:first-child input:checkbox").bind("click", function(){
        var holding_container = $(this).closest('.subject-container');
        var check_all = holding_container.find('tbody[id$=table] input:checkbox[checked]').length == holding_container.find('tbody[id$=table] input:checkbox').length;
        holding_container.find('.checkall-subjects').attr('checked', check_all);
    });*/
/*

    $("#all_subjects div.list_header span.header").each(function(i){
        var subject_type = $(this).html();
        var container = $(this).parent().next();
        var none_selected_id = $(".none_selected", container).attr("id");
        var data_locator_id = $("div.action", container).attr("id");
        var html = container.html();

        var kwargs = {
            container: container,
            checkbox_locator:"table.styled_table input:checkbox",
            data_locator: "#" + data_locator_id,
            none_selected_locator: "#" + none_selected_id,
            many_selected_msg: $.sprintf(gettext("Select 1 %s only"), subject_type),
            check_single_checked_locator: ".styled_table tbody input:checkbox[checked=checked]",
            no_cb_checked_locator: ".styled_table input:checkbox[checked=checked]",
            edit_link_locator: "div.action ul li a.edit",
            checkall: ".styled_table thead input:checkbox"
        };


        new DW.action_dropdown(kwargs);
    });*/
});