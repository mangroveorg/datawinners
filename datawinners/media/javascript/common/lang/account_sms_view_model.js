function displaySuccessMessage(data) {
    $('.success-message-box').text(data["message"]);
    $('.success-message-box').show();
    $('.success-message-box')[0].scrollIntoView();
}

function AccountWideSmsViewModel() {
    var self = this;

    self.checkWarningMsgDisplay = function (messageItem) {
        messageItem.displayWarning(self.isMessageItemChanged(messageItem.code, messageItem.message()));
    };


    self.save = function (callback) {
        if (!self.isValid()) return;
        DW.loading();
        self.saveButtonText(gettext("Saving..."));
        $.post(post_url, {
                'data': JSON.stringify(ko.toJS(self)),
                'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
            },
            function (data) {
                data = JSON.parse(data);
                self.saveButtonText(gettext("Save"));
                displaySuccessMessage(data);
                resetAccountMsgWarningDisplay();
                self.messagesInitialState(ko.toJSON(self.messages()));
                if (typeof callback == "function") callback();
            }
        );

    };
}


function resetAccountMsgWarningDisplay(){
    var messages = accountWideSmsViewModel.messages();
    for(var i=0;i<messages.length;i++){
        messages[i].displayWarning(false);
    }
}

$(function(){
    window.accountWideSmsViewModel= new AccountWideSmsViewModel();
    ko.applyBindings(accountWideSmsViewModel);
    createObservableMessageItemsFor(account_messages, accountWideSmsViewModel.messages, accountWideSmsViewModel.messagesInitialState, true);
    initializeWarningDialog();
});


function initializeWarningDialog() {
    var options = {
        successCallBack: function (callback) {
            accountWideSmsViewModel.save(callback);
        },
        isQuestionnaireModified: function () {
            return accountWideSmsViewModel.isMessageModified();
        },
        cancelDialogDiv: "#cancel_language_changes_warning",
        validate: function () {
            return accountWideSmsViewModel.isValid();
        },
        ignore_links: "#cancel_changes"
    };
    new DW.CancelWarningDialog(options).init().initializeLinkBindings();
}

AccountWideSmsViewModel.prototype = new ReplyMessageViewModel();
AccountWideSmsViewModel.prototype.constructor = AccountWideSmsViewModel;