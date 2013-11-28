DW.SubmissionImportPopup = function(){
    var self = this;

    self.init = function(download_url_template){
        self.import_dialog = $("#submission_import").dialog({
                title: gettext("Import Submission(s)"),
                modal: true,
                autoOpen: false,
                width: 500,
                closeText: 'hide'
            }
        );
        self.download_link = $("#template-download-link");
        self.download_url_template = download_url_template;
        return self;
    };

    self.updateTemplateDownloadLink = function(target){
        var selected_link_element = $(target);
        var project_name = selected_link_element.attr("data-projectname");
        var form_code = selected_link_element.attr("data-formcode");
        var template_download_url = self.download_url_template.replace("<project_name>", project_name).replace("form_code", form_code);
        self.download_link.attr("href", template_download_url);
        return self;
    };

    self.open = function(){
        self.import_dialog.dialog("open");
        return self;
    };
};

$(function(){
    var submissionPopup = new DW.SubmissionImportPopup().init(import_template_url);
    $(document).on("click", '.import_link', function(event){
        submissionPopup.updateTemplateDownloadLink(event.currentTarget);
        submissionPopup.open();
    });
});