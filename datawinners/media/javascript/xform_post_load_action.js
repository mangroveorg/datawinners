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

    if (Object.prototype.toString.call(window.HTMLElement).indexOf('Constructor') > 0){
        $(document).find('input[type=file]').each(function(){
            if ($(this).attr('accept') == "video/*"){
                $(this).removeAttr('accept');
                $(this).attr('data','video/*');
            }
        });
    }

    $(document).data('maxSubmissionSize', 50 * 1024 * 1024); // Increase media file size from default 5mb to 50mb
});


function _initializeWarningDialog() {
    var calledAfterEdit = function() {
        $('#success-message-box').show();
        $(window).scrollTop($('#success-message-box').offset().top);
    };

    var options = {
        successCallBack: function (callback) {
            saveXformSubmission(calledAfterEdit);
        },
        isQuestionnaireModified: function () {
            if ($('#success-message-box').is(':visible')) {
                return false;
            }
            return true;
        },
        validate: function () {
            return true;
        },

        cancelDialogDiv: "#cancel_submission_warning_message",
        ignore_links: "#cancel_changes , .map-canvas-wrapper a, .get_image_link"
    };
    cancelWarningPopUp = new DW.CancelWarningDialog(options).init();
    cancelWarningPopUp.initializeLinkBindings();

}