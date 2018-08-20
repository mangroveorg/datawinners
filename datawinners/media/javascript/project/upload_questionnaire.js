DW.UploadQuestionnaire = function(options){
    this._init(options);
};
DW.showError = function(errors,message_prefix,message_suffix){
    var error_message_prefix = '';
    var error_message_suffix = '';
    var apply_class = '';

    if(message_prefix){
        error_message_prefix = message_prefix;
        apply_class = 'xls_errors';
    }
    if(message_suffix){
        error_message_suffix = message_suffix;
        apply_class = 'xls_errors';
    }

    var error_messages = "<ul>";

    $.each(errors, function(index, error){
       error_messages += "<li class='"+ apply_class +"'>" + error + "</li>";
    });
    error_messages += "</ul>";
    var flash_message = $("#xlx-message");
    flash_message.removeClass("none").removeClass("success-message-box").addClass("message-box").
        html("<span>" + error_message_prefix + "</span>"+ error_messages +"<span>" + error_message_suffix + "</span>").show();
};
DW.showInfo = function(infos){
    var info_messages = '';

    $.each(infos, function(index, info){
       info_messages += "<div class='information_box'>" + info + "</div>";
    });
//    info_messages += "</ul>";
    var flash_message = $("#xlx-info");
    flash_message.removeClass("none").removeClass("success-message-box").
        html(info_messages).show();
    //flash_message.delay(5000).fadeOut();
};
DW.updateFilename = function(file_name){
    $("div.download_xls span.heading_block a").text(file_name);
};

DW.showSuccess = function(message){
    var flash_message = $("#xlx-message");
    flash_message.removeClass("none").removeClass("message-box").addClass("success-message-box").
    html("<label class='success'>" + gettext("Your changes have been saved.") + "</label").show();
    flash_message.delay(5000).fadeOut(); //verify this
};

DW.UploadQuestionnaire.prototype._init = function(options){
    var self = this;
    var uploadButton = $("#uploadXLS");
    if (!!uploadButton) {
        var spinner = $(".upload_spinner");
        var initialUploadButtonText = uploadButton.text();
        var cancelUploadLink = $("#cancel-xlx-upload");
    }
    var warningMessageBox = $(".warning-message-box");
    var flash_message = $("#xlx-message");
    self.file_uploader = new qq.FileUploader({
        element: document.getElementById('file_uploader'),
        action: options.postUrl(),
        buttonText: options.buttonText,
        onSubmit: function () {
            $('.information_box').remove();

            if (!!uploadButton) {
                cancelUploadLink.removeClass("none");
                spinner.removeClass("none");
                uploadButton.text(gettext("Uploading..."));
                uploadButton.attr("disabled","disabled");
                uploadButton.addClass("disabled_yellow_submit_button");
            }

            // Create the event
            var event = new CustomEvent("uploadFile", { "detail": "File is currently uploaded" });

            // Dispatch/Trigger/Fire the event
            document.dispatchEvent(event);

            flash_message.addClass("none");
            this.params = options.params || {};
            options.onSubmit && options.onSubmit();
        },
        onComplete: function (id, fileName, responseJSON) {
            warningMessageBox.addClass("none");
            if (!!uploadButton) {
                cancelUploadLink.addClass("none");
                spinner.addClass("none");
                uploadButton.text(initialUploadButtonText);
                uploadButton.removeClass("disabled_yellow_submit_button");
                uploadButton.removeAttr("disabled");
            }

            if (!responseJSON['success']) {
                if (responseJSON['unsupported']) {
                    options.promptOverwrite(responseJSON, self.file_uploader, self.file_input);
                } else {
                    options.postErrorHandler(responseJSON);
                }
            }
            else {
                (options.onSuccess && options.onSuccess());
                options.postSuccessSave && options.postSuccessSave(responseJSON);
                if (responseJSON['information']) {
                    options.postInfoHandler(responseJSON)
                }
            }
        }
    });

    self.file_input = $("input[name=file]");
    if (!!uploadButton) {
        uploadButton.on("click", function() {
            if(!options.preUploadValidation()){
                return false;
            }
            $("input[name=file]").click();
            return false;
        });

        cancelUploadLink.on("click", function(){
            $(".qq-upload-cancel")[0].click();
            cancelUploadLink.addClass("none");
            spinner.addClass("none");
            uploadButton.text(initialUploadButtonText);
            uploadButton.removeAttr("disabled");
            uploadButton.removeClass("disabled_yellow_submit_button")
            warningMessageBox.removeClass("none");
            flash_message.addClass("none");
            DW.trackEvent('advanced-questionnaire', 'cancel-upload');
            options.postCancelCallBack && options.postCancelCallBack();
            return false;
        });
    }

};

DW.XLSHelpSection = function(){
    var options = {
        dialogElementSelector: "#xls_learn_more_form",
        title: "Create Questionnaires with Advanced Features",
        width:955
    };
    var dialogSection = $("#xls_learn_more_form");
    DW.AccordionDialog(options);
    $(".xls_learn_more").on('click', function() {
        DW.trackEvent('advanced-questionnaire', 'learn-more-clicked');
        dialogSection.removeClass("none");
        dialogSection.dialog("open");
        $(document).scrollTop(0);
    });

    $("#xls_learn_more_form #learn-xls-forms-pdf-link").on('click', function(){
        DW.trackEvent('advanced-questionnaire', 'xlsforms-pdf-downloaded');
        return true;
    });
};

DW.XLSSampleSectionTracker = function(){

    new DW.Dialog({
        title: gettext("Download Sample Forms"),
        dialogDiv: "#sample_xls_forms_section",
        link_selector: "#sample_forms_link",
        width: 800
    }).init().initializeLinkBindings();

    $("#sample_xls_forms_section_dialog_section #sample_xls_section").on('click', "a", function(){
        var excel_file_name = $(this).text();
        DW.trackEvent('advanced-questionnaire', 'sample-xls-downloaded', excel_file_name);
        return true;
    });
}