$(document).ready(function(){
    $(".export-entity-link").bind("click", function(){
        var entity_type = $(this).attr("id").substr(7);
        $("#type_to_export").val(entity_type);
        $("#checked_subjects").html('');
        var checkboxes = $("#"+entity_type+"-table :checkbox:checked");

        checkboxes.each(function(){
            var element = document.createElement("input");
            element.name = $(this).attr("name");
            element.value = $(this).val();
            element.type = 'hidden';
            $("#checked_subjects").append(element);
        });

        $('#subject-export-form').trigger('submit');
    });

    $(".file-uploader").each(function(){
        var form_code = $(this).attr("id").substr(7);

        var uploader = new qq.FileUploader({
            // pass the dom node (ex. $(selector)[0] for jQuery users)
            element: $(this)[0],
            // path to server-side upload script
            action: upload_url,
            params: {form_code: form_code},
            onComplete: function(id, fileName, responseJSON) {
                $('.message').remove();
                $('.error_tbody').html('');
                $(".error_table").hide();
                $("#"+form_code+"_table").html('');
                $.each(responseJSON.all_data, function(index, entity_data) {
                    if (entity_data.code == form_code){
                        $.each(entity_data.data, function(key, element){
                            if ($.inArray(element.short_code, responseJSON.imported) != -1){
                                var datas = element.cols.join("</td><td>");

                                $("#"+form_code+"_table").append("<tr><td>"+datas+"</td></tr>");
                            }
                        });
                    }
                });

                if (responseJSON.success == true) {
                    $('<div id="message" class="success_message success-message-box">' + responseJSON.message + '</div>').insertAfter($('#import-'+form_code));

                }
                else {
                    $("#"+form_code+"_error_table table tbody").html('');
                    if (responseJSON.error_message) {
                        $('<div id="message" class="error_message message-box">' + responseJSON.error_message + '</div>').insertAfter($('#import-'+form_code));
                    }
                    else {
                        $('<div id="message" class="error_message message-box">' + responseJSON.message + '</div>').insertAfter($('#import-'+form_code));
                    }
                    if (responseJSON.failure_imports > 0) {
                        $("#"+form_code+"_error_table").show();
                    }
                    $.each(responseJSON.failure_imports, function(index, element) {
                        $("#"+form_code+"_error_table table tbody").append("<tr><td>" + element.row_num + "</td><td>" + JSON.stringify(element.row) + "</td><td>"
                                + element.error + "</td></tr>");
                    });
                    $("#"+form_code+"_error_table").show();
                }
            }
        });
    })



    $(".popup-import").dialog({
        autoOpen: false,
        modal: true,
        title: function(){
            var entity_type = $(this).attr("id").substr(22);
            return interpolate(gettext('Import a list of %(entity)s'), {entity:entity_type}, true);
        },
        zIndex:200,
        width: 1000
    });

    $(".import-subject").unbind().bind("click", function(){
        var entity_type = $(this).attr("id").substr(7);
        $("#popup-"+entity_type).dialog("open");
    });

    $(".close_import_dialog").bind("click", function(){
        var entity_type = $(this).attr("id").substr(13);
        $("#popup-"+entity_type).dialog("close");
    })

    $(".edit-form-code-link").bind("click", function(){
        var entity_type = $(this).attr("id").substr(8);
        location.href = $("#link-to-edit-form-"+entity_type).attr("href");
    })
})
