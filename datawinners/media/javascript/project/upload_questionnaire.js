DW.UploadQuestionnaire = function(options){
    var self = this;
    self._init(options);
};
DW.showError = function(errorMessage){
    var flash_message = $("#xlx-message");
    flash_message.removeClass("none").removeClass("success-message-box").addClass("message-box").
        html("<label class='error'>" + errorMessage + "</label>").show();
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
            uploadButton.text(gettext("Uploading..."));
            uploadButton.attr("disabled","disabled");
            this.params = (options.params && options.params()) || {};
            options.onSubmit && options.onSubmit();
        },
        onComplete: function (id, fileName, responseJSON) {
            warningMessageBox.addClass("none");
            cancelUploadLink.addClass("none");
            spinner.addClass("none");
            uploadButton.text(initialUploadButtonText);
            uploadButton.removeAttr("disabled");
            if (responseJSON['error_msg']) {
                options.postErrorHandler(responseJSON);
            }
            else {
                (options.onSuccess && options.onSuccess()) || DW.showSuccess();
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
        warningMessageBox.removeClass("none");
        flash_message.addClass("none");
        options.postCancelCallBack && options.postCancelCallBack();
        return false;
    });
};