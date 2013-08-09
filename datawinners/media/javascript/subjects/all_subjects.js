$(document).ready(function () {
    $('#web_preivew').toggle();
    $('#subject_registration_preview').live('click', function (eventObject) {
        $('#wrapper_div_for_table').toggle();
        $('#web_preivew').toggle();
        $('.secondary_tab li:first').attr('class', 'inactive');
        $('.secondary_tab li:last').attr('class', 'active');
        eventObject.preventDefault();
    });

    $("#all_subjects .list_header").each(function (i) {
        var container = document;//$(this).parent().next();
        var data_locator_id = $("div.action", container).attr("id");
        //var html = container.html();

        var kwargs = {
            container: container,
            checkbox_locator: "table.styled_table input:checkbox",
            //data_locator: "#" + data_locator_id,
            //none_selected_locator: "#" + none_selected_id,
            //many_selected_msg: $.sprintf(gettext("Select 1 %s only"), subject_type),
            check_single_checked_locator: ".styled_table tbody input:checkbox[checked=checked]",
            no_cb_checked_locator: ".styled_table input:checkbox[checked=checked]",
            edit_link_locator: "div.action ul li a.edit",
            checkall: ".styled_table thead input:checkbox",
            is_on_trial: true
        };


        new DW.action_dropdown(kwargs);
    });

    $("table.styled_table thead input:checkbox").click(function (event) {
        self = event.target;
        $("table.styled_table tbody input:checkbox").attr('checked', $(self).is(":checked"));
    });

    $('#action li a').click(function (e) {
        if ($(this).parent().hasClass("disabled")) {
            e.preventDefault();
            return false;
        }
        var action = this.className;

        var ids = $(".styled_table tbody input:checkbox:checked").map(function(i, el){return $(el).val()});
        if (action == "delete") {
            doDelete(ids);
        } else if (action == "edit") {
            location.href = '/entity/subject/edit/' + subject_type.toLowerCase() + '/' + ids[0] + '/';
        }
    });
});
