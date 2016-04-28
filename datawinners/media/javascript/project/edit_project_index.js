$(function () {

    new DW.XLSHelpSection();

    DW.XLSSampleSectionTracker();

    new DW.UploadQuestionnaire({
        buttonText: "Upload New XLSForm",
        params: {"edit": true},
        postUrl: function(){
           return '/xlsform/upload/update/'+ project_id +'/';
        },
        preUploadValidation: function() {
            if (typeof(xlsform_edit_enabled) == 'undefined') {
                this.promptOverwrite();
                return false;
            }
            this.params.edit = true;
            return true;
        },
        postErrorHandler: function(responseJSON) {
            DW.trackEvent('advanced-questionnaire-edited', 'edit-questionnaire-errored');
            if (typeof(questionnaire_builder_enabled) != 'undefined') {
                raiseUploadFileCompletedEvent(responseJSON);
            }
            DW.showError(responseJSON['error_msg'],responseJSON.message_prefix, responseJSON.message_suffix);
        },
        promptOverwrite: function(responseJSON, file_uploader, file_input) {
            var self = this;
            DW.trackEvent('advanced-questionnaire-edited', 'edit-questionnaire-errored');
            var editQuestionnaireWarningOptions = {
                successCallBack: function (callback) {
                    callback();
                    self.params.edit = false;
                    if (file_input) {
                        file_uploader._onInputChange(file_input[0]);
                    } else {
                        $("input[name=file]").click();
                    }
                    return false;
                },
                title: gettext("Warning: Changes to your Questionnaire will delete previously collected data"),
                link_selector: "#cancel_changes",
                dialogDiv: "#cancel_questionnaire_edit",
                cancelLinkSelector: "#cancel_dialog",
                width: 780
            };
            if (typeof(questionnaire_builder_enabled) != 'undefined') {
                raiseUploadFileCompletedEvent();
            }
            var warningDialog = new DW.Dialog(editQuestionnaireWarningOptions).init();
            warningDialog.show();
        },
        postInfoHandler: function(responseJSON) {
            DW.showInfo(responseJSON['information']);
        },
        postSuccessSave: function(responseJSON) {
            DW.updateFilename(responseJSON.file_name);
        },
        onSuccess:function(){
            DW.trackEvent('advanced-questionnaire-edited', 'edit-questionnaire-success');

            if (typeof(questionnaire_builder_enabled) != 'undefined') {
                raiseUploadFileCompletedEvent();
            }
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


