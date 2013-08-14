//this file is being used as delete handler in datasenders/index.js and registered datasender
$(document).ready(function () {
    $("#delete_entity_block").dialog({
            title: gettext("Warning !!"),
            modal: true,
            autoOpen: false,
            width: 500,
            closeText: 'hide'
        }
    );

    $("#delete_entity_block .cancel_link").bind("click", function() {
        $("#delete_entity_block").dialog("close");
        $('#delete_entity_block').data("action_element").value = "";
        return false;
    });


    $("#ok_button").bind("click", function() {
        $("#delete_entity_block").dialog("close");
        var allIds = $('#delete_entity_block').data("allIds");
        var entity_type = $('#delete_entity_block').data("entity_type");
        var path = $(this).attr("href");
        post_data = {'all_ids':allIds.join(';'), 'entity_type':entity_type}
        if ($("#project_name").length)
            post_data.project = $("#project_name").val();
        if($('#select_all_link').attr('class') == 'selected')
            post_data.all_selected = true;
        $.post("/entity/delete/", post_data,
            function (json_response) {
                var response = $.parseJSON(json_response);
                if (response.success) {
                    if ($("#project_name").length) {
                        window.location.reload(true);
                    } else {
                        window.location.href = path;
                    }
                }
            }
        );
        return false;
    });

});

function warnThenDeleteDialogBox(allIds, entity_type, action_element) {
    $("#delete_entity_block").data("allIds", allIds);
    $("#delete_entity_block").data("entity_type", entity_type);
    $("#delete_entity_block").data("action_element", action_element);

    $("#delete_entity_block").dialog("open");
}
