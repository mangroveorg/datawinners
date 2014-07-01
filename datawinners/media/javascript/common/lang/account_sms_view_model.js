function displaySuccessMessage(data) {
    $('.success-message-box').text(data["message"]);
    $('.success-message-box').show();
    $('.success-message-box')[0].scrollIntoView();
}

function AccountWideSmsViewModel() {
    var self = this;

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
                    $.each(self.messages(), function (index, element) {
                        element.message.clearError();
                    });

                    resetAccountMsgWarningDisplay();
                    self.resetModifiedFlag();
                    self.messagesInitialState(ko.toJSON(self.messages()));
                    self.isMessageModified(false);
                    if (typeof callback == "function") callback();
                }
                else {
                    var initialState = data.messages;
                    $.each(self.messages(), function (index, element) {
                        element.message(initialState[index].message);
                        resetAccountMsgWarningDisplay();
                        initialState[index].valid == false ? element.message.setSysVariableError(initialState[index].error) : element.message.clearError();
                    });
                    $(".TextTags").each(function (i, tag) {
                        $(tag).TextNTags("create", self.messages()[i].message());
                    });
                }
            }
        );

    };

    self.resetMessage = function(event, messageItem){
        $.post("/defaultmessages/",{'message_code':messageItem.code}).done(function(response){
            messageItem.message.clearError();
            var messageBox = $(event.target).parents("li").next().children(".TextTags");
            $(messageBox).TextNTags("create", response);
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
    createObservableMessageItemsFor(account_messages, accountWideSmsViewModel, true);
    _initializeLearnMoreDialog();
    initializeWarningDialog();

    $("#account_wide_sms").on('click', ".reset-link", function(event){
        accountWideSmsViewModel.resetMessage(event, ko.dataFor(this));
    });
});

function _initializeLearnMoreDialog(){
    var learnMoreOptions = {
        link_selector: "#learn_more_link",
        title: "Learn How to Edit Languages",
        dialogDiv: "#account_wide_sms_learn_more",
        width:900
    };
    new DW.Dialog(learnMoreOptions).init().initializeLinkBindings();
}

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

    var cancelPopupOptions = {
        ignoreCallback: function (callback) {
            accountWideSmsViewModel.resetChanges();
        },
        title: "Cancel Changes",
        link_selector: "#cancel_changes",
        dialogDiv: "#revert_changes_warning",
        cancelLinkSelector :"#keep_changes",
        openPredicate: function(){return accountWideSmsViewModel.isMessageModified();}
    };
    new DW.Dialog(cancelPopupOptions).init().initializeLinkBindings();
}

AccountWideSmsViewModel.prototype = new ReplyMessageViewModel();
AccountWideSmsViewModel.prototype.constructor = AccountWideSmsViewModel;