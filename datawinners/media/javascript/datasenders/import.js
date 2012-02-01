$(document).ready(function () {
    $("#error_table").hide();
    var project_id = ($("#project_id").length) ? $("#project_id").val() : 0;
    var uploader = new qq.FileUploader({
        // pass the dom node (ex. $(selector)[0] for jQuery users)
        element:document.getElementById('file_uploader'),
        // path to server-side upload script
        action:"/entity/datasenders/",
        params:{project_id:project_id},
        onSubmit:function () {
            $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
        },
        onComplete:function (id, fileName, responseJSON) {
            $.unblockUI();
            $('#message').remove();
            $('#error_tbody').html('');
            $("#error_table").hide();
            if (project_id != 0) {
                $("#imported_table").html('');
                $.each(responseJSON.all_data, function (index, element) {
                    if (element.short_code in responseJSON.imported_entities) {
                        var datas = element.cols.join("</td><td>");
                        $("#imported_table").append("<tr><td>" + datas + "</td></tr>");
                    }
                });
            }
            else {
                $("#subject_table tbody").html('');
                $.each(responseJSON.all_data, function (index, element) {
                    var html = "<td><input type='checkbox' id='" + element.short_code + "' value='" + element.short_code + "'/></td>";
                    html += "<td>" + element.cols.join("</td><td>") + "</td><td>" + element.projects + "</td><td>" + element.email + "</td>";
                    $("#subject_table tbody").append("<tr>" + html + "</tr>");
                });
            }
            if (responseJSON.success == true) {
                $('<div id="message" class="success_message success-message-box">' + responseJSON.message + '</div>').insertAfter($('#file-uploader'));
            }
            else {
                $('#error_tbody').html('');
                if (responseJSON.error_message) {
                    $('<div id="message" class="error_message message-box clear-left">' + responseJSON.error_message + '</div>').insertAfter($('#file-uploader'));
                }
                else {
                    $('<div id="message" class="error_message message-box clear-left">' + responseJSON.message + '</div>').insertAfter($('#file-uploader'));
                }
                if (responseJSON.failure_imports.length > 0) {
                    $("#error_table").removeClass('none');
                }
                $.each(responseJSON.failure_imports, function (index, element) {
                    $("#error_table table tbody").append("<tr><td>" + element.row_num + "</td><td>" + JSON.stringify(element.row) + "</td><td>"
                            + element.error + "</td></tr>");
                });
                $("#error_table").show();
            }
        }
    });
});
