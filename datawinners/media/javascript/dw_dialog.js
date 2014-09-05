DW.Dialog = function (options) {
    var self = this;
    var _successCallBack = options["successCallBack"] || function(){};
    var _cancelCallback = options["cancelCallback"]|| function(){};
    var _ignoreCallback = options["ignoreCallback"]|| function(){};

    this.init = function () {
        var dialogDiv = options.dialogDiv;
        var dialogId = dialogDiv.substring(1) + "_dialog_section";
        self.cancelDialog = $('<div id='+ dialogId +'>').html($(dialogDiv).html());
        self.ignoreButton = self.cancelDialog.find(".no_button");
        self.saveButton = self.cancelDialog.find(".yes_button");
        var cancelLinkSelector = options.cancelLinkSelector || "#cancel_dialog";
        self.cancelButton = self.cancelDialog.find(cancelLinkSelector);
        self.openPredicate = options.openPredicate || function(){return true;};
        _initializeDialog();
        _initializeIgnoreButtonHandler();
        _initializeCancelButtonHandler();
        _initializeSaveButtonHandler();
        return this;
    };

    this.show = function(){
        self.cancelDialog.dialog("open");
    };

    var _initializeDialog = function () {
        self.cancelDialog.dialog({
            title: gettext(options.title),
            modal: true,
            autoOpen: false,
            width: options.width || 550,
            closeText: 'hide',
            closeOnEscape: false,
            open: options.open || function(){}
        });
    };

    var _initializeIgnoreButtonHandler = function () {
        self.ignoreButton.bind('click', function (event) {
            _ignoreCallback();
            self.cancelDialog.dialog("close");
            return false;
        });
    };

    var _initializeCancelButtonHandler = function () {
        self.cancelButton.bind('click', function () {
            _cancelCallback();
            self.cancelDialog.dialog("close");
            return false;
        });
    };

    var _initializeSaveButtonHandler = function () {
        self.saveButton.bind('click', function (event) {
            _successCallBack(function () {
                self.cancelDialog.dialog("close");
                return false;
            });
            self.cancelDialog.dialog("close");
        });
    };

    this.initializeLinkBindings = function () {
        var ignore_links = options.ignore_link_selector || "";
        $(options.link_selector).not(ignore_links).bind('click', {self: this}, function (event) {
            if (self.openPredicate()) {
                self.cancelDialog.dialog("open");
                return false;
            }
        });
    };
};