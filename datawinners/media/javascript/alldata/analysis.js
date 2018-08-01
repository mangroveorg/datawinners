$(document).ready(function () {

    DW.SubmissionLogExport = function () {
        var self = this;
        var user_email = "";
        var organization_name = "";

        self.init = function () {
            self.exportLink = $('.export_link');
            self.exportForm = $('#export_form');
            _initialize_dialogs();
            _initialize_events();
        };

        self.update_tab = function(currentTabName){
            self.url = '/allfailedsubmissions/export/log' + '?type=' + currentTabName;
           self.count_url = '/allfailedsubmissions/export/log-count' + '?type=' + currentTabName;
        };

        self._show_export_message = function(){
            var messageBox = $("#export-warning");
            messageBox.removeClass("none");
            $("#close-export-msg").on('click', function(){
                messageBox.addClass("none");
            });
        };

        var _updateAndSubmitForm = function(is_export_with_media, is_single_sheet){
            if (is_export_with_media)
            {
                self._show_export_message();
            }
            self.exportForm.attr('action', self.url).submit();
        };

        var _check_limit_and_export = function(is_export_with_media, is_single_sheet){
            $.post(self.count_url, {
                    'data': JSON.stringify({"questionnaire_code": $("#questionnaire_code").val(),
                                            "search_filters": {}
                                            }),
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                }
            ).done(function(data){
                    if(data['count'] <= 20000){
                       _updateAndSubmitForm(is_export_with_media, is_single_sheet);
                    }
                    else{
                        DW.trackEvent('export-submissions', 'export-exceeded-limit', "user_email" + ":" + "organization_name");
                        self.limit_dialog.show();
                    }
            });
        };

        var _initialize_dialogs = function(){

           var limit_info_dialog_options = {
                    successCallBack: function (callback) {
                    },
                    title: gettext("Number of Submissions Exceeds Export Limit"),
                    link_selector: ".export_link",
                    dialogDiv: "#export_submission_limit_dialog",
                    cancelLinkSelector: "#cancel_dialog",
                    width: 580
                };
           self.limit_dialog = new DW.Dialog(limit_info_dialog_options).init();
        };

        var _initialize_events = function () {
            $('.with_media').click(function(){
                   DW.trackEvent('export-submissions-with-images', 'export-submissions-single-sheet', user_email + ":" + organization_name);
                   _check_limit_and_export(true, false);
             });

            self.exportLink.click(function () {
                   DW.trackEvent('export-submissions', 'export-submissions-single-sheet', user_email + ":" + organization_name);
                   _check_limit_and_export(false, false);
            });
        };
    };

    var submissionLogExport = new DW.SubmissionLogExport();
    submissionLogExport.update_tab("allfailedsubmissions");
    submissionLogExport.init();
});


