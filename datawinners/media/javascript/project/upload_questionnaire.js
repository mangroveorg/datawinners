DW.UploadQuestionnaire = function(options){
    var self = this;
    self._init(options);
};
DW.showError = function(errors){
    var error_message_prefix = gettext("<br/>");
    var error_messages = "<ul>";
    $.each(errors, function(index, error){
       error_messages += "<li class='xls_errors'>" + error + "</li>";
    });
    error_messages += "</ul>";
    var flash_message = $("#xlx-message");
    flash_message.removeClass("none").removeClass("success-message-box").addClass("message-box").
        html("<span>" + gettext('Sorry! Current version of DataWinners does not support') + "</span>"+ error_messages +"<span>" + gettext('Update your XLSForm and upload again.') + "</span>").show();
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
        options.postCancelCallBack && options.postCancelCallBack();
        return false;
    });
};
DW.XLSHelpSection = function(){
    this.init = function () {
        var options = {
            title:"Learn More About How To Create Questionnaires With Advanced Features"
        };
        var dialogSection = $("#xls_learn_more_form");
        initializeDialogWithAccordion(dialogSection, options);
        $("#xls_learn_more").on('click', function () {
            dialogSection.removeClass("none");
            dialogSection.dialog("open");
//                dialogSection.parent(".ui-dialog")[0].scrollIntoView();
        });
    }
};