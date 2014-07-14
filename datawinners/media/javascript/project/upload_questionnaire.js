DW.UploadQuestionnaire = function(options){
    var self = this;
    self._init(options);
};
DW.showError = function(errorMessage){
    var flash_message = $("#xlx-message");
    flash_message.removeClass("none").removeClass("success-message-box").addClass("message-box").
        html("<label class='error_message'>" + errorMessage + "</label>").show();
};

DW.UploadQuestionnaire.prototype._showSuccess = function(message){
    var flash_message = $("#xlx-message");
    flash_message.removeClass("none").removeClass("message-box").addClass("success-message-box").
    html("<label class='success'>" + gettext("Your changes have been saved.") + "</label").show();
    flash_message.delay(5000).fadeOut(); //verify this
};

DW.UploadQuestionnaire.prototype._init = function(options){
    var self = this;
    var preUploadValidation =  options.preUploadValidation || function(){ return true;};

    var uploadButton = $("#uploadXLS");
    var initialUploadButtonText = uploadButton.text();
    var cancelUploadLink = $("#cancel-xlx-upload");

    uploadButton.on("click", function() {

        if(!preUploadValidation()){
            return false;
        }

        new qq.FileUploader({
            element: document.getElementById('file_uploader'),
            action: options.postUrl(),
            params: {},
            buttonText: options.buttonText,
            onSubmit: function(){
                cancelUploadLink.removeClass("none");
                uploadButton.text(gettext("Uploading..."));
                options.onSubmit && options.onSubmit();
            },
            onComplete: function (id, fileName, responseJSON){
                cancelUploadLink.addClass("none");
                uploadButton.text(initialUploadButtonText);
                if(responseJSON['error_msg']){
                    options.postErrorHandler(responseJSON);
                }
                else{
                    self._showSuccess();
                    options.postSuccessSave && options.postSuccessSave(responseJSON);
                }
            }
        });

        $("input[name=file]").click();
        return false;
    });

    cancelUploadLink.on("click", function(){
        $(".qq-upload-cancel")[0].click();
        cancelUploadLink.addClass("none");
        uploadButton.text(initialUploadButtonText);
        options.postCancelCallBack && options.postCancelCallBack();
        return false;
    });
};