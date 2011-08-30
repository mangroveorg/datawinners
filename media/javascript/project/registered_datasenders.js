$(document).ready(function() {
    var allIds = [];

    function updateIds() {
        allIds = [];
        $('#tbody :checked').each(function() {
            allIds.push($(this).val());
        });
    }

    $('#tbody input').click(updateIds);

    $('#action').change(function(){
        if ($(this).val()=='disassociate' && allIds.length > 0){
                $.post('/project/disassociate/',
                        {'ids':allIds,'project_id':$("#project_id").val()}
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

