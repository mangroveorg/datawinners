$(document).ready(function() {
    var allIds = [];

    function updateIds() {
        allIds = [];
        $('#tbody :checked').each(function() {
            allIds.push($(this).val());
        });
    }

    $("input[type='checkbox']").each(function() {
        $(this).change(function(){
            var selected_count = $('#tbody :checked').length;
            if (selected_count > 1){
                $("select option[value='edit']").attr('disabled', 'disabled')
            }
            else{
                $("select option[value='edit']").removeAttr('disabled');
            }
        })
    });

    $('#action').change(function(){
        updateIds();
        $('#error').remove();
        var action = $(this).val();
        if (allIds.length == 0){
            $('<div class="message-box" id="error">' + gettext("Please select atleast 1 data sender") + '</div>').insertAfter($(this));
            $('#project').val('');
            $(this).val("");
        }
        else if (action=='disassociate'){
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
            warnThenDeleteDialogBox(allIds, "reporter", this)
        }
        else if(action=='edit'){
            if(allIds.length > 1){
                $('<div class="message-box" id="error">' + gettext("Please select only 1 data sender") + '</div>').insertAfter($(this));
                $(this).val('');
            }
            else{
                location.href = '/project/edit_datasender/' + $("#project_id").val() + '/' + allIds[0] + '/';
            }
        }
    });
});



