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
        if (!self.isValid() || !self.isMessageModified()) return;
        DW.loading();
        self.saveButtonText(gettext("Saving..."));
        $.post(post_url, {
                'data': JSON.stringify(ko.toJS(self)),
                'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
        }).done(function (data) {
                data = JSON.parse(data);
                self.saveButtonText(gettext("Save"));
                if(data.success) {
                    displaySuccessMessage(data);
                    resetAccountMsgWarningDisplay();
                    self.messagesInitialState(ko.toJSON(self.messages()));
                    if (typeof callback == "function") callback();
                }
                else {
                    var initialState = data.messages;
                    $.each(self.messages(), function (index, element) {
                        element.message(initialState[index].message);
                        resetAccountMsgWarningDisplay();
                        initialState[index].valid == false ? element.message.setError(initialState[index].error) : element.message.clearError();
                    });
                    $(".TextTags").each(function (i, tag) {
                        $(tag).TextNTags("create", self.messages()[i].message());
                    });
                }
            }
        );

    };

    self.resetMessage = function(e,messageItem){
        $.post("/defaultmessages/",{'message_code':messageItem.code}).done(function(response){
            messageItem.message.clearError();
            $($(e.target).parents("li").next().children(".TextTags")).TextNTags("create", response);
        });
    }

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