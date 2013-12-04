DW.SubmissionImportPopup = function(){
    var self = this;

    self.init = function(options){
        self.import_dialog = $("#submission_import").dialog({
                title: gettext("Import a Submission List"),
                modal: true,
                autoOpen: false,
                open: function(){
                    self.import_help_section.hide();
                   self.success_section.hide();
                },
                width: 500,
                closeText: 'hide'
            }
        );
        self.download_link = $("#template-download-link");
        self.secondary_download_link = $("#secondary-template-download-link");
        self.upload_link = "";
        self.import_help_section = $("#import_help_section");
        self.show_help_link = $("#show_help");
        self.hide_help_link = $("#hide_help");
        self.success_section = $('#success_import_section');
        self.import_template_url_template = options.import_template_url_template;
        self.import_submission_url_template = options.import_submission_url_template;
        _initialize_event_handlers();
        return self;
    };

    self.updateUrls = function(target){
        var selected_link_element = $(target);
        var project_name = selected_link_element.attr("data-projectname");
        var form_code = selected_link_element.attr("data-formcode");
        _updateTemplateDownloadLink(project_name, form_code);
        _updateSubmissionUploadLink(form_code, selected_link_element);
        return self;
    };

    self.open = function(){
        self.import_dialog.dialog("open");
        return self;
    };

    function _updateTemplateDownloadLink(project_name, form_code) {
        var template_download_url = self.import_template_url_template.replace("<project_name>", project_name).replace("form_code", form_code);
        self.download_link.attr("href", template_download_url);
        self.secondary_download_link.attr("href", template_download_url);
    };

    function _updateSubmissionUploadLink(form_code, selected_link_element) {
        self.upload_link = self.import_submission_url_template.replace("form_code", form_code);
        self.upload_link += '?project_id=' + selected_link_element.attr("data-projectid");
    };

    var _initialize_event_handlers = function () {

        self.show_help_link.on("click", function(){
            self.import_help_section.show();
        });

        self.hide_help_link.on("click", function(){
            self.import_help_section.hide();
        });
    };

    self.initializeFileUploader = function() {
        var options = {
            "upload_link": self.upload_link
        };
        DW.SubmissionFileUploader(options);
    };

};

DW.SubmissionFileUploader = function(options){
    var self = this;
    var success_table = $('#success_table');

    self.onComplete = function(id, fileName, responseJSON){
        $.unblockUI();
        if(responseJSON.success_submissions.length > 0){
             _clearSuccessSection();
             _populateSuccessTable(responseJSON.question_map, responseJSON.success_submissions);
             _updateSuccessSectionHeader(responseJSON);
             $('#success_import_section').show();
        }
    };

    function _createHeader(questionMap) {
        var header = '<thead><tr>'
        _.each(questionMap, function (question) {
            header += '<th>' + question + '</th>';
        });
        header += '</tr></thead>';
        return header;
    };

    function _createSuccessTableBody(submissions, questionMap) {
        var successBody = '<tbody>';
        _.each(submissions, function (submission) {
            successBody += '<tr>';
            _.each(questionMap, function (questionText, questionCode) {
                successBody += '<td>' + submission[questionCode] + '</td>';
            });
            successBody += '</tr>';
        });
        successBody += '</tbody>'
        return successBody;
    };

    function _updateSuccessSectionHeader(responseJSON) {
        $("#success_table_message").html(responseJSON.success_submissions.length + gettext(" Record(s) Successfully Imported"));
    };

    var _populateSuccessTable = function(questionMap, submissions){
        var header = _createHeader(questionMap);
        success_table.append(header);
        var successBody = _createSuccessTableBody(submissions, questionMap);
        success_table.append(successBody);
    };

    var _clearSuccessSection = function(){
        success_table.html("");
    };

    new qq.FileUploader({
            // pass the dom node (ex. $(selector)[0] for jQuery users)
            element: document.getElementById('file_uploader'),
            // path to server-side upload script
            action: options.upload_link,
            params: {},
            onSubmit: function () {
                $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
            },
            onComplete: self.onComplete
    });
};

$(function(){
    var options = {
        "import_template_url_template": import_template_url,
        "import_submission_url_template": import_submission_url
    };
    var submissionPopup = new DW.SubmissionImportPopup().init(options);
    $(document).on("click", '.import_link', function(event){
        submissionPopup.updateUrls(event.currentTarget);
        submissionPopup.initializeFileUploader();
        submissionPopup.open();
    });
});

