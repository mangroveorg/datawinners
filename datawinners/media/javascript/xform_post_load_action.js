$(document).on('initializePostFormLoadAction', 'form', function(){
    $(document).on("postFormLoadAction", function(){
        $(".ajax-loader").hide();
        if (isQuotaReached != "True") {
            $("#validate-form").removeClass("disabled-state").removeClass("disabled");
        }

        $("form").change(function (){
            if (typeof(cancelWarningPopUp) == "undefined")
                _initializeWarningDialog();
        });
})});


function _initializeWarningDialog() {
    var options = {
        successCallBack: function (callback) {
            saveXformSubmission(callback);
        },
        isQuestionnaireModified: function () {
            return true;
        },
        validate: function () {
            return true;
        },

        cancelDialogDiv: "#cancel_submission_warning_message",
        ignore_links: "#cancel_changes"
    };
    cancelWarningPopUp = new DW.CancelWarningDialog(options).init();
    cancelWarningPopUp.initializeLinkBindings();

}