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
                $("#subject_table tbody").append("<tr><td>" + element.short_name + "</td><td>" + element.name + "</td><td>"  + element.type + "</td><td>" + element.location + "</td><td>" + element.description + "</td><td>" + element.mobile_number + "</td></tr>")
            });
            if (responseJSON.success == true) {
                $('<span id="message" class="success_message">' + responseJSON.message + '</span>').insertAfter($('#register_link'));

            }
            else {
                $('#error_tbody').html('');
                $('<span id="message" class="error_message">' + responseJSON.message + '</span>').insertAfter($('#register_link'));
                if (responseJSON.error_message)
                {
                    $('<span id="message" class="error_message">' + responseJSON.error_message + '</span>').insertAfter($('#register_link'));
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
});