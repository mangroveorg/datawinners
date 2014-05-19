DW.CancelWarningDialog = function (options) {
    var self = this;
    var successCallBack = options.successCallBack;
    var isQuestionnaireModified = options.isQuestionnaireModified;

    this.init = function () {
        var canceDialogDiv = options.cancelDialogDiv || "#cancel_questionnaire_warning_message";
        self.cancelDialog = $(canceDialogDiv);
        self.ignoreButton = self.cancelDialog.find(".no_button");
        self.saveButton = self.cancelDialog.find(".yes_button");
        self.cancelButton = self.cancelDialog.find("#cancel_dialog");
        _initializeDialog();
        _initializeIgnoreButtonHandler();
        _initializeCancelButtonHandler();
        _initializeSaveButtonHandler();
        _initializeLinkBindings();
    };

    var _initializeDialog = function () {
        self.cancelDialog.dialog({
            title: gettext("You Have Unsaved Changes"),
            modal: true,
            autoOpen: false,
            width: 550,
            closeText: 'hide'
        });
    };

    var _initializeIgnoreButtonHandler = function () {
        self.ignoreButton.bind('click', function () {
            self.cancelDialog.dialog("close");
            return _redirect();
        });
    };

    var _initializeCancelButtonHandler = function () {
        self.cancelButton.bind('click', function () {
            self.cancelDialog.dialog("close");
            return false;
        });
    };

    var _initializeSaveButtonHandler = function () {
        self.saveButton.bind('click', function () {
            if(options.validate()) {
                successCallBack(function () {
                    return _redirect();
                });
            }
            self.cancelDialog.dialog("close");
        });
    };

    var _redirect = function () {
        window.location.href = redirect_url;
        return true;
    };

    var _initializeLinkBindings = function () {
        $("a[href]:visible, a#back_to_create_options, a#cancel_questionnaire").not(".add_link, .preview-navigation a, .sms_tester, .delete_project, #dw_help_link").bind('click', {self: this}, function (event) {
            var that = event.data.self;
            redirect_url = $(this).attr("href");
            if (isQuestionnaireModified()) {
                self.cancelDialog.dialog("open");
                return false;
            }
            else
                return _redirect();
        });
    };

};