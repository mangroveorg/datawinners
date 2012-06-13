
function getEntityIdsToBeDeleted(action_element) {
    var allIds = [];
    $('input:checked').each(function () {
        allIds.push($(this).val());
    });
    return allIds;
}

function getEntityType(action_element){
    return $('#entity_type').val();
}
