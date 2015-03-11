$(function () {

    new DW.XLSHelpSection();

    DW.XLSSampleSectionTracker();

    new DW.UploadQuestionnaire({
        buttonText: "Upload New XLSForm",
        postUrl: function(){
           return '/xlsform/upload/update/'+ project_id +'/';
        },
        postErrorHandler: function(responseJSON) {
            DW.trackEvent('advanced-questionnaire-edited', 'edit-questionnaire-errored');

            DW.showError(responseJSON['error_msg'],responseJSON.message_prefix, responseJSON.message_suffix);
        },
        postInfoHandler: function(responseJSON) {
            DW.showInfo(responseJSON['information']);
        },
        postSuccessSave: function(responseJSON) {
            DW.updateFilename(responseJSON.file_name);
        },
        preUploadValidation:function(){
            var editQuestionnaireWarningOptions = {
                successCallBack: function (callback) {
                    callback();
                    $("input[name=file]").click();
                    return false;
                },
                title: gettext("Warning: Changes to your Questionnaire will delete previously collected data"),
                link_selector: "#cancel_changes",
                dialogDiv: "#cancel_questionnaire_edit",
                cancelLinkSelector: "#cancel_dialog",
                width: 780
            };
            var warningDialog = new DW.Dialog(editQuestionnaireWarningOptions).init();
            warningDialog.show();
            return false;
        },
        onSuccess:function(){
            DW.trackEvent('advanced-questionnaire-edited', 'edit-questionnaire-success');

            var kwargs = {dialogDiv: "#inform_datasender_about_changes",
                title: gettext('Inform Your Data Senders about the Changes'),
                width:650,
                successCallBack: function(callback) {
                    callback();
                    DW.showSuccess();
                }
            };
            var informAboutChanges = new DW.Dialog(kwargs).init();
            informAboutChanges.show();
            return true;
        }
    });

    $('.download_link').click(function () {
        $('#download_form').attr('action', '/xlsform/download/').submit();
    });


});


