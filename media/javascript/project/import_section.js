$(document).ready(function(){

    $(".import_subject_form").dialog({
        autoOpen: false,
        width: "auto",
        modal: true,
        title: 'Import a List',
        close: function() {
            $('#message').remove();
            $('#error_tbody').html('');
            $("#error_table").hide();
        }
    });

    $("#import_subjects").unbind('click').click(function() {
           $(".import_subject_form").dialog("open");
       });

    var uploader = new qq.FileUploader({
        // pass the dom node (ex. $(selector)[0] for jQuery users)
        element: document.getElementById('file_uploader'),
        // path to server-side upload script
        action: $('#post_url').val(),
        onComplete: function(id, fileName, responseJSON) {
            $('#message').remove();
            $('#error_tbody').html('');
            $("#error_table").hide();
            if (responseJSON.success == true) {
                $('<span id="message" class="success_message">' + responseJSON.message + '</span>').insertAfter($('#file-uploader'));
            }
            else {
                $('<span id="message" class="error_message">' + responseJSON.message + '</span>').insertAfter($('#file-uploader'));
                if (responseJSON.error_message)
                {
                    $('<span id="message" class="error_message">' + responseJSON.error_message + '</span>').insertAfter($('#file-uploader'));
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

    $("#file_uploader input").addClass("button");

});
