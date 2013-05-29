$(document).ready(function () {
    $('.action li a').click(function (e) {
        $('#error').hide();
        var allIds = getEntityIdsToBeDeleted(this);
        var entity_type = getEntityType(this);
        var action = getActionValue(this);
        if (allIds.length == 0) {
            displayErrorMessage('Please select atleast 1 subject');
            return;
        }
        if (action == 'edit') {
            if (allIds.length > 1) {
                e.preventDefault();
                return false;
            }
            else {
                location.href = getEditURL() + entity_type + '/' + allIds[0] + '/';
            }

        }
        else if (action == "") {
            return;
        }
        else {
            warnThenDeleteDialogBox(allIds, entity_type, this);
        }
    });

    var subject_type = $("#entity_type").val();

    var kwargs = {
        trigger: "button.action",
        checkbox_locator:"#subjects-table input:checkbox",
        data_locator:"#action",
        none_selected_locator:"#none-selected",
        many_selected_msg: $.sprintf(gettext("Please select 1 %s only"), subject_type),
        check_single_checked_locator: "#subjects-table tbody input:checkbox[checked=checked]",
        no_cb_checked_locator: "#subjects-table input:checkbox[checked=checked]",
        edit_link_locator: "#edit"
    }

    var registered_subjects_action_dropdown = new DW.action_dropdown(kwargs);

    $("#checkall-subjects").bind("click", function(){
        var checked = $(this).attr("checked") == "checked";
        $("#subjects-table tbody input").attr("checked", checked);

        if (!checked) {
            registered_subjects_action_dropdown.deactivate_action();
        } else {
            registered_subjects_action_dropdown.update_edit_action();
        }

    });

    $("#subjects-table tbody input").bind("click", function(){
        $("#checkall-subjects").attr("checked", $("#subjects-table tbody input").length == $("#subjects-table tbody input:checkbox[checked]").length );
    });

    if ($("#subjects-table tbody input:checkbox").length == 0) {
        $("#checkall-subjects").attr("disabled", "disabled");
    }

});
// Can remove action_element
function getEntityIdsToBeDeleted(action_element) {
    var allIds = [];
    $('tbody input:checked').each(function () {
        allIds.push($(this).val());
    });
    return allIds;
}

// Can remove action_element
function getEntityType(action_element){
    return $('#entity_type').val();
}

function getEditURL(){
    return edit_url;
}

function getActionValue(action_element){
    var separated_values = $(action_element).attr('data-entity').split('-');
    return separated_values[separated_values.length-1];
}

function displayErrorMessage(errorMessage) {
    $('<div class="message-box" id="error">' + gettext(errorMessage) + '</div>').insertAfter($('#action_button'));
    return;
}

