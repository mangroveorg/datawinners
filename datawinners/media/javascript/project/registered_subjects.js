
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
