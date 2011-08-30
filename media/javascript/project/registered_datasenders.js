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
        if ($(this).val()=='disassociate' && allIds.length > 0){
                $.post('/project/disassociate/',
                        {'ids':allIds.join(';'),'project_id':$("#project_id").val()}
                ).success(function(data){
                            window.location.href = data
                        }
                )
        }
        else if ($(this).val()=='disassociate'){
            $(this).val("");
        }
    })

});

