$(document).ready(function () {
    $(".export-entity-link").bind("click", function () {
        var entity_type = $(this).attr("id").substr(7);
        $("#type_to_export").val(entity_type);
        $("#checked_subjects").html('');
        var checkboxes = $("#" + entity_type + "-table :checkbox:checked");

        checkboxes.each(function () {
            var element = document.createElement("input");
            element.name = $(this).attr("name");
            element.value = $(this).val();
            element.type = 'hidden';
            $("#checked_subjects").append(element);
        });

        $('#subject-export-form').trigger('submit');
    });

    $(".file-uploader").each(function () {
        var form_code = $(this).attr("id").substr(7);

        var uploader = new qq.FileUploader({
            // pass the dom node (ex. $(selector)[0] for jQuery users)
            element: $(this)[0],
            // path to server-side upload script
            action: upload_url,
            onSubmit: function () {
                $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}})
            },
            onComplete: function (id, fileName, responseJSON) {
                $.unblockUI();
                $(".blockUI").fadeOut("slow");
                $('#message').remove();
                $('.error_tbody').html('');
                $(".error_table").hide();
                $("#" + form_code + "_table").html('');
                if ($.isEmptyObject(responseJSON)) {
                    $('<div id="message" class="error_message message-box clear-left">' + gettext("Sorry, an error occured - the reason could be connectivity issues or the import taking too long to process.  Please try again.  Limit the number of subjects you import to 200 or less.") + '</div>').insertAfter($('#file-uploader'));
                }
                else {
                    $.each(responseJSON.all_data, function (index, entity_data) {
                        if (entity_data.code == form_code) {
                            $.each(entity_data.data, function (key, element) {
                                if ($.inArray(element.short_code, responseJSON.imported) != -1) {
                                    var datas = element.cols.join("</td><td>");

                                    $("#" + form_code + "_table").append("<tr><td>" + datas + "</td></tr>");
                                }
                            });
                        }
                    });

                    if (responseJSON.success == true) {
                        $('<div id="message" class="success_message success-message-box">' + responseJSON.message + '</div>').insertAfter($('#import-' + form_code));

                    }
                    else {
                        $("#" + form_code + "_error_table table tbody").html('');
                        if (responseJSON.error_message) {
                            $('<div id="message" class="error_message message-box">' + responseJSON.error_message + '</div>').insertAfter($('#import-' + form_code));
                        }
                        else {
                            $('<div id="message" class="error_message message-box">' + responseJSON.message + '</div>').insertAfter($('#import-' + form_code));
                        }
                        if (responseJSON.failure_imports.length > 0) {
                            $("#" + form_code + "_error_table").removeClass('none');
                        }
                        $.each(responseJSON.failure_imports, function (index, element) {
                            $("#" + form_code + "_error_table table tbody").append("<tr><td>" + element.row_num + "</td><td>" + JSON.stringify(element.row) + "</td><td>"
                                + element.error + "</td></tr>");
                        });
                        $("#" + form_code + "_error_table").show();
                    }
                }
            }
        });
    })


    $(".popup-import").dialog({
        autoOpen: false,
        modal: true,
        title: interpolate(gettext('Import a list of %(entity)s'), {entity: subject_type}, true),
        zIndex: 200,
        width: 1000,
        close: function () {
            if ($('#message').length) {
                window.location.replace(document.location.href);
            }
        }
    });

    $(document).on("click", ".import-subject", function () {
        if ($(this).parent().hasClass("subjects_links")) {
            var index = $(".subjects_links .import-subject").index($(this));
        } else {
            var subject_container = $(this).parent().parent().parent().parent();
            var index = $(".subject-container").index(subject_container);
        }

        if (index == -1)
            index = 0;

        $(".popup-import").eq(index).dialog("open");
    });

    $(".close_import_dialog").bind("click", function () {
        $(this).parent().parent().dialog("close");
    })

    $(".edit-form-code-link").bind("click", function () {
        var index = $(".edit-form-code-link").index($(this));
        location.href = $(".edit-form-link").eq(index).attr("href");
    })
})
