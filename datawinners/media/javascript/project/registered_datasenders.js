$(document).ready(function() {
    var allIds = [];

    function updateIds() {
        allIds = [];
        $('#tbody :checked').each(function() {
            allIds.push($(this).val());
        });
    }


    $('#action').change(function(){
        updateIds();
        $('#error').remove();
        var action = $(this).val();
        if (action=='disassociate' && allIds.length > 0){
                $.post('/project/disassociate/',
                        {'ids':allIds.join(';'),'project_id':$("#project_id").val()}
                ).success(function(data){
                            $('<div class="success-message-box" id="success_message">' + gettext("Data Senders dissociated Successfully") +'. ' + gettext("Please Wait") + '....</div>').insertAfter($('#action'));
                            $('#success_message').delay(4000).fadeOut(1000, function () {$('#success_message').remove();});
                            setTimeout(function(){window.location.href = data;},5000);
                        }
                );
        }
        else if(action=='delete'){
            openEntityWarningDialogBox(allIds, "reporter", this)
        }
        else if (allIds.length == 0){
            $('<div class="message-box" id="error">' + gettext("Please select at least 1 data sender") + '</div>').insertAfter($(this));
            $('#project').val('');
            $(this).val("");
        }
    });
});


function openEntityWarningDialogBox(allIds, entity_type, action_element) {
    $("#delete_entity_block").data("allIds", allIds);
    $("#delete_entity_block").data("entity_type", entity_type);
    $("#delete_entity_block").data("action_element", action_element);

    $("#delete_entity_block").dialog("open");
}



