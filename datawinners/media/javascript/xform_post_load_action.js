$(document).on('initializePostFormLoadAction', 'form', function(){

    var isEditSubmission = dataStrToEdit !== "";

    if(isEditSubmission){
        $("#validate-form").wrap("<div id='submission-action-section'></div>");
        $("<a id='cancel-link' href=" + submissionLogURL + " class='cancel-link'>"+ gettext("Cancel Editing") +"</a>").insertBefore("#validate-form");
    }
});

$(document).on("postFormLoadAction", function(){
    $(".ajax-loader").hide();
    if (isQuotaReached != "True") {
        $("#validate-form").removeClass("disabled-state").removeClass("disabled");
    }

    $("form").change(function (){
        if (typeof(cancelWarningPopUp) == "undefined")
            _initializeWarningDialog();
    });
});


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
        ignore_links: "#cancel_changes , .map-canvas-wrapper a"
    };
    cancelWarningPopUp = new DW.CancelWarningDialog(options).init();
    cancelWarningPopUp.initializeLinkBindings();

}