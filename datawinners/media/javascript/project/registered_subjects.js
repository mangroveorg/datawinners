$(document).ready(function () {
    $('.action li a').click(function () {
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
                displayErrorMessage('Please select only 1 subject');
                return;
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
});
// Can remove action_element
function getEntityIdsToBeDeleted(action_element) {
    var allIds = [];
    $('input:checked').each(function () {
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

