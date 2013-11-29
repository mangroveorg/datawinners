DW.SubmissionImportPopup = function(){
    var self = this;

    self.init = function(download_url_template){
        self.import_dialog = $("#submission_import").dialog({
                title: gettext("Import a Submission List"),
                modal: true,
                autoOpen: false,
                open: function(){
                    _hide_help_section();
                },
                width: 500,
                closeText: 'hide'
            }
        );
        self.download_link = $("#template-download-link");
        self.import_help_section = $("#import_help_section");
        self.show_help_link = $("#show_help");
        self.hide_help_link = $("#hide_help");
        self.download_url_template = download_url_template;
         __initialize_event_handlers();
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

    var _hide_help_section = function() {
        self.import_help_section.hide();
    };

    var __initialize_event_handlers = function () {
        _hide_help_section();

        self.show_help_link.on("click", function(){
            self.import_help_section.show();
        });

        self.hide_help_link.on("click", function(){
            self.import_help_section.hide();
        });
    };

};

$(function(){
    var submissionPopup = new DW.SubmissionImportPopup().init(import_template_url);
    $(document).on("click", '.import_link', function(event){
        submissionPopup.updateTemplateDownloadLink(event.currentTarget);
        submissionPopup.open();
    });
});