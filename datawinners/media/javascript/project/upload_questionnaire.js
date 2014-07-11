DW.UploadQuestionnaire = function(options){
    var self = this;
    self._init(options);
};
DW.UploadQuestionnaire.prototype._showError = function(errorMessage){
    var flash_message = $("#xlx-error-message");
    flash_message.removeClass("none").removeClass("success-message-box").addClass("message-box").
        html("<label class='error_message'>" + errorMessage + "</label>").show();
};

DW.UploadQuestionnaire.prototype._showSuccess = function(message){
    var flash_message = $("#xlx-error-message");
    flash_message.removeClass("none").removeClass("message-box").addClass("success-message-box").
    html("<label class='success'>" + gettext("Your changes have been saved.") + "</label").show();
    $('#message-label').delay(5000).fadeOut();
}

DW.UploadQuestionnaire.prototype._init = function(options){
        var self = this;
        var preUploadValidation =  options.preUploadValidation || function(){ return true;};

        $("#uploadXLS").on("click", function() {

            if(!preUploadValidation()){
                return false;
            }

            new qq.FileUploader({
                element: document.getElementById('file_uploader'),
                action: options.postUrl(),
                params: {},
                buttonText: options.buttonText,
                onSubmit: options.onSubmit || function () {
                },
                onComplete: function (id, fileName, responseJSON) {
                    if (responseJSON['error_msg']) {
                        self._showError(responseJSON['error_msg']);
                    } else {
                        options.postSuccessSave && options.postSuccessSave(responseJSON);
                    }
                }
            });

            $("input[name=file]").click();
            return false;
        });
};