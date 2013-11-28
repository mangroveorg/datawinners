$(document).ready(function(){
    var import_dialog = $("#submission_import").dialog({
            title: gettext("Import Submission"),
            modal: true,
            autoOpen: false,
            width: 500,
            closeText: 'hide'
        }
    );

    $('.import_link').click(function(){
        var project_name = $(this).attr("data-projectname");
        var form_code = $(this).attr("data-formcode");
        var template_download_url = import_template_url.replace("<project_name>", project_name).replace("form_code", form_code);
        $("#template-download-link").attr("href", template_download_url);
        import_dialog.dialog("open");
    });
});
