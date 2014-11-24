DW.UploadQuestionnaire = function(options){
    var self = this;
    self._init(options);
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

DW.showSuccess = function(message){
    var flash_message = $("#xlx-message");
    flash_message.removeClass("none").removeClass("message-box").addClass("success-message-box").
    html("<label class='success'>" + gettext("Your changes have been saved.") + "</label").show();
    flash_message.delay(5000).fadeOut(); //verify this
};

DW.UploadQuestionnaire.prototype._init = function(options){
    var self = this;
    var preUploadValidation =  options.preUploadValidation || function(){ return true;};

    var uploadButton = $("#uploadXLS");
    var spinner = $(".upload_spinner");
    var initialUploadButtonText = uploadButton.text();
    var cancelUploadLink = $("#cancel-xlx-upload");
    var warningMessageBox = $(".warning-message-box");
    var flash_message = $("#xlx-message");
    new qq.FileUploader({
        element: document.getElementById('file_uploader'),
        action: options.postUrl(),
        params: {},
        buttonText: options.buttonText,
        onSubmit: function () {
            cancelUploadLink.removeClass("none");
            spinner.removeClass("none");
            flash_message.addClass("none");
            uploadButton.text(gettext("Uploading..."));
            uploadButton.attr("disabled","disabled");
            uploadButton.addClass("disabled_yellow_submit_button");
            this.params = (options.params && options.params()) || {};
            options.onSubmit && options.onSubmit();
        },
        onComplete: function (id, fileName, responseJSON) {
            warningMessageBox.addClass("none");
            cancelUploadLink.addClass("none");
            spinner.addClass("none");
            uploadButton.text(initialUploadButtonText);
            uploadButton.removeClass("disabled_yellow_submit_button");
            uploadButton.removeAttr("disabled");
            if (!responseJSON['success']) {
                options.postErrorHandler(responseJSON);
            }
            else {
                (options.onSuccess && options.onSuccess());
                options.postSuccessSave && options.postSuccessSave(responseJSON);
            }
        }
    });

    uploadButton.on("click", function() {
        if(!preUploadValidation()){
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