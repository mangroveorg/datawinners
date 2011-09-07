$(document).ready(function() {
    $("#error_table").hide();
    
    var uploader = new qq.FileUploader({
        // pass the dom node (ex. $(selector)[0] for jQuery users)
        element: document.getElementById('file_uploader'),
        // path to server-side upload script
        action: window.location.pathname,
        onComplete: function(id, fileName, responseJSON) {
            $('#message').remove();
            $('#error_tbody').html('');
            $("#error_table").hide();
            $("#subject_table tbody").html('');
            $.each(responseJSON.all_data, function(index, element) {
                $("#subject_table tbody").append("<tr><td><input type='checkbox' id='" + element.short_name + "' value='"+ element.short_name +"/></td><td>" + element.short_name + "</td><td>" + element.name + "</td><td>" + element.type + "</td><td>" + element.location + "</td><td>"+ element.geocode + "</td><td>" + element.mobile_number + "</td><td>"+ element.projects +"</td></tr>")
            });
            if (responseJSON.success == true) {
                $('<div id="message" class="success_message success-message-box">' + responseJSON.message + '</div>').insertAfter($('#file-uploader'));

            }
            else {
                $('#error_tbody').html('');
//                $("#error_table").show();
                if (responseJSON.error_message)
                {
                    $('<div id="message" class="error_message message-box">' + responseJSON.error_message + '</div>').insertAfter($('#file-uploader'));
                }
                else{
                    $('<div id="message" class="error_message message-box">' + responseJSON.message + '</div>').insertAfter($('#file-uploader'));
                }
                if(responseJSON.failure_imports > 0)
                {
                    $("#error_table").show();
                }
                $.each(responseJSON.failure_imports, function(index, element) {
                    $("#error_table table tbody").append("<tr><td>" + element.row_num + "</td><td>" + JSON.stringify(element.row) + "</td><td>"
                            + element.error + "</td></tr>")
                });
                $("#error_table").show();
            }

        }
    });

    var allIds = [];

    function updateIds() {
        allIds = [];
        $('#all_data_senders :checked').each(function() {
            allIds.push($(this).val());
        });
    }

    $('#action').change(function(){
        updateIds();
        $('#error').remove()
        if ($(this).val()=='disassociate' && allIds.length > 0 && $('#project').val()!=''){
                $.post('/entity/disassociate/',
                        {'ids':allIds.join(';'),'project_id':$("#project").val()}
                ).success(function(data){
                            $('<div class="success-message-box" id="success_message">Data Senders Dis-Associated Successfully. Please Wait....</div>').insertAfter($('#action'))
                            $('#success_message').delay(4000).fadeOut(1000, function () {$('#success_message').remove();});
                            setTimeout(function(){window.location.href = data},5000);
                        }
                )
        }
        if ($(this).val()=='associate' && allIds.length > 0 && $('#project').val()!=''){
                $.post('/entity/associate/',
                        {'ids':allIds.join(';'),'project_id':$("#project").val()}
                ).success(function(data){
                            $('<div class="success-message-box" id="success_message">Data Senders Associated Successfully. Please Wait....</div>').insertAfter($('#action'))
                            $('#success_message').delay(4000).fadeOut(1000, function () {$('#success_message').remove();});
                            setTimeout(function(){window.location.href = data},5000);
                        }
                )
        }
        else if ($('#project').val()==''){
            $('<div class="message-box" id="error">Please select atleast 1 project</div>').insertAfter($(this))
            $('#project').val('')
            $(this).val("");
        }
        else if (allIds.length == 0){
            $('<div class="message-box" id="error">Please select atleast 1 data sender</div>').insertAfter($(this))
            $('#project').val('')
            $(this).val("");
        }
    })



});