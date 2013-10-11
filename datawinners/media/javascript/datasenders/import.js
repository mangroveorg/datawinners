$(document).ready(function () {
    $("#popup-import").dialog({
        autoOpen:false,
        modal:true,
        title:gettext("Import a Data Senders list"),
        zIndex:200,
        width:940,
        close:function () {
            if ($('#message').length) {
                window.location.replace(document.location.href);
            }
        }
    });


    $("#import-datasenders").bind("click", function () {
        $("#popup-import").dialog("open");
        $('#message').remove();
        $('#error_tbody').html('');
        $("#error_table").hide();
        $('#imported_table').html("");
    });

    $(".close_import_dialog").bind("click", function () {
        $("#popup-import").dialog("close");
    });

    $("#error_table").hide();
    var uploader = new qq.FileUploader({
        // pass the dom node (ex. $(selector)[0] for jQuery users)
        element:document.getElementById('file_uploader'),
        // path to server-side upload script
        action:window.location.href,
        params:{},
        onSubmit:function () {
            $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
        },
        onComplete:function (id, fileName, responseJSON) {
            $.unblockUI();
            $('#message').remove();
            $('#error_tbody').html('');
            $("#error_table").hide();
            if ($.isEmptyObject(responseJSON)) {
                $('<div id="message" class="error_message message-box clear-left">' + gettext("Sorry, an error occured - the reason could be connectivity issues or the import taking too long to process.  Please try again.  Limit the number of subjects you import to 200 or less.") + '</div>').insertAfter($('#file-uploader'));
            }
            else {
                reload_tables(responseJSON);
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
        }
    });
});
