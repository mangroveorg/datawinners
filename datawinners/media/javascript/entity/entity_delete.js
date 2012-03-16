$(document).ready(function () {

    $('.action').change(function() {
        var typeCodeList = $(this).val().split('-');
        var entity_type = typeCodeList[0];
        var entity_code = typeCodeList[1];
        var allIds = getEntityIdsToBeDeleted(entity_code);
        $.post("/entity/delete/", {'all_ids':allIds.join(';'), 'entity_type':entity_type},
                function(json_response){
                    var response = $.parseJSON(json_response);
                    if (response.success){
                        window.location.reload();
                    }
                }
        );
    });


    function getEntityIdsToBeDeleted(entity_code) {
        var allIds = [];
        var tbody_id = entity_code + "-table";
        $('#' + tbody_id + ' :checked').each(function () {
            allIds.push($(this).val());
        });
        return allIds;
    }
});