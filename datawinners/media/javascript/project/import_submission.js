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
                    self.success_message.hide();
                    self.error_section.hide();
                    self.error_message.hide();
                },
                width: 750,
                zIndex: 200,
                dialogClass: "no-close",
                buttons: [
                    {
                      text: gettext("Close"),
                      click: function() {
                        $( this ).dialog( "close" );
                       _reload_parent_page();
                      }
                    }
                ]
            }
        );
        self.download_link = $("#template-download-link");
        self.secondary_download_link = $("#secondary-template-download-link");
        self.upload_link = "";
        self.import_help_section = $("#import_help_section");
        self.show_help_link = $("#show_help");
        self.hide_help_link = $("#hide_help");
        self.success_section = $('#success_import_section');
        self.error_section = $('#error_import_section');
        self.error_message = $('#error_message');
        self.success_message = $('#success_message');
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

    self.updateTemplateFileName = function(target){
          var selected_link_element = $(target);
          var file_name = selected_link_element.attr("data-filename") + ".xls";
          self.download_link.text(file_name);
          self.secondary_download_link.text(file_name);
    };

    self.open = function(){
        self.import_dialog.dialog("open");
        return self;
    };

    function _reload_parent_page() {
        DW.loading();
        window.location.reload();
    }

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
    var error_table = $('#error_table');

    self.onComplete = function(id, fileName, responseJSON){
        $.unblockUI();
         _clearTables();
        if(responseJSON.success_submissions.length > 0){
             _populateSuccessTable(responseJSON.question_map, responseJSON.success_submissions);
             $('#success_import_section').show();
        }

        if (responseJSON.errored_submission_details.length > 0) {
            _populateErrorTable(responseJSON.errored_submission_details);
            $('#error_import_section').show();
        }
        _updateMessages(responseJSON);
        _disable_upload_button(responseJSON.quota_over);

    };

    function _disable_upload_button(quota_over) {
        if (quota_over) {
            $('.file-uploader').html('<span disabled="disabled" class="disabled_yellow_submit_button file_upload_disabled">' + gettext("Upload a file") + '</span>');
        }
    }

    function _createHeader(questionMap) {
        var header = '<thead><tr>'
        _.each(questionMap, function (question) {
            header += '<th>' + question + '</th>';
        });
        header += '</tr></thead>';
        return header;
    };

    function _createTableBody(submissions, questionMap) {
        var body = '<tbody>';
        _.each(submissions, function (submission) {
            body += '<tr>';
            _.each(questionMap, function (questionText, questionCode) {
                body += '<td>' + submission[questionCode] + '</td>';
            });
            body += '</tr>';
        });
        body += '</tbody>'
        return body;
    };

    var _populateErrorTable = function(error_details){
        var header = _createErrorHeader();
        error_table.append(header);
        var body = _createErrorBody(error_details);
        error_table.append(body);
    };

    var _createErrorHeader = function() {
        return '<thead><tr><th>Row Number</th><th>Details</th></tr></thead>';
    }

    function _updateMessages(responseJSON) {
        if (responseJSON.success) {
            _update_success_table_message(responseJSON);
            var successCount = responseJSON.success_submissions.length;
            $("#success_message").html(interpolate(gettext("All %(successCount)s records have been successfully imported."), {successCount:successCount}, true));
            $("#success_message").show();
        } else {
            var errorCount = responseJSON.errored_submission_details.length;
            $("#error_table_message").html(interpolate(gettext("%(errorCount)s Submission(s) Failed to Import"), {errorCount:errorCount}, true));

            $("#error_message").html(responseJSON.message);
            $('#error_message').show();
            _update_success_table_message(responseJSON)
        }
    };

    function _update_success_table_message(responseJSON) {
        if(responseJSON.success_submissions.length > 0) {
            var successCount = responseJSON.success_submissions.length;
            $("#success_table_message").html(interpolate(gettext("%(successCount)s Submission(s) Successfully Imported"),{successCount:successCount}, true));
        }
    };

    var _createErrorBody = function(error_details) {
        var body = '<tbody>';
            _.each(error_details, function (error_detail) {
                body += '<tr><td>' + error_detail.row_count + '</td><td>';
                body += '<ul class="bulleted error_list">'
                _.each(error_detail.errors, function (error) {
                    body += '<li>' + error + '</li>';
                });
                body += '</ul></td></tr>';
            });
        body += '</tbody>'
        return body;
    }

    var _populateSuccessTable = function(questionMap, submissions){
        var header = _createHeader(questionMap);
        success_table.append(header);
        var successBody = _createTableBody(submissions, questionMap);
        success_table.append(successBody);
    };

    var _clearTables = function(){
        success_table.html("");
        error_table.html("");
    };

    new qq.FileUploader({
            // pass the dom node (ex. $(selector)[0] for jQuery users)
            element: document.getElementById('file_uploader'),
            // path to server-side upload script
            action: options.upload_link,
            params: {},
            onSubmit: function () {
                $('#success_import_section').hide();
                $('#success_message').hide();
                $('#error_import_section').hide();
                $('#error_message').hide();

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
        var target = event.currentTarget;
        submissionPopup.updateUrls(target);
        submissionPopup.updateTemplateFileName(target);
        submissionPopup.initializeFileUploader();
        submissionPopup.open();
    });
});

