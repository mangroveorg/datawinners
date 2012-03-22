$(document).ready(function () {
    $("#delete_entity_block").dialog({
            title: gettext("Warning !!"),
            modal: true,
            autoOpen: false,
            height: 230,
            width: 450,
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
        $.post("/entity/delete/", {'all_ids':allIds.join(';'), 'entity_type':entity_type},
            function (json_response) {
                var response = $.parseJSON(json_response);
                if (response.success) {
                    window.location.href = path;
                }
            }
        );
        return false;
    });

    $('.action').change(function() {
        $('#error').hide();
        var allIds = getEntityIdsToBeDeleted(this);
        var entity_type = getEntityType(this);
        if (allIds.length == 0){
            $('<div class="message-box" id="error">' + gettext('Please select atleast 1 subject') + '</div>').insertAfter($(this));
            $(this).val("--");
            return;
        }
        openEntityWarningDialogBox(allIds, entity_type, this);
    });



});

function openEntityWarningDialogBox(allIds, entity_type, action_element) {
    $("#delete_entity_block").data("allIds", allIds);
    $("#delete_entity_block").data("entity_type", entity_type);
    $("#delete_entity_block").data("action_element", action_element);

    $("#delete_entity_block").dialog("open");
}
