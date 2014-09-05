$(function () {

    new DW.XLSHelpSection().init();
    new DW.UploadQuestionnaire({
        buttonText: "Upload New XLSForm",
        postUrl: function(){
           return '/xlsform/upload/update/'+ project_id +'/';
        },
        postErrorHandler: function(responseJSON) {
            DW.showError(responseJSON['error_msg']);
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


