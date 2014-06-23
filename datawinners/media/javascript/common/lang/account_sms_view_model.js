function displaySuccessMessage(data) {
    $('.success-message-box').text(data["message"]);
    $('.success-message-box').show();
    $('.success-message-box')[0].scrollIntoView();
}
function AccountWideSmsViewModel() {
    var self = this;
    self.accountMessages = ko.observableArray();
    self.accountMessagesInitialState = ko.observable();
    self.isAccountMessageModified = ko.computed(function () {
        return self.accountMessagesInitialState() != ko.toJSON(self.accountMessages());
    }, self);

    self.saveButtonText = ko.observable(gettext("Save"));
    self.isAccountMessageItemChanged = function (messageCode, messageText) {
        if (self.accountMessagesInitialState()) {
            var initialAccountMessages = JSON.parse(self.accountMessagesInitialState());
            for (var i = 0; i < initialAccountMessages.length; i++) {
                if (initialAccountMessages[i].code == messageCode) {
                    return initialAccountMessages[i].message != messageText;
                }
            }
        }
        return false;
    };

    self.resetChanges = function(){
        var initialState = $.parseJSON(self.accountMessagesInitialState());
        $.each(self.accountMessages(),function(index,element){
            element.message.clearError();
            element.message(initialState[index].message);
        });
        $(".TextTags").each(function(i, tag){
            $(tag).TextNTags("create", self.accountMessages()[i].message());
        });
    };

    self.checkWarningMsgDisplay = function (messageItem) {
        messageItem.displayWarning(self.isAccountMessageItemChanged(messageItem.code, messageItem.message()));
    };
    self.helptextscenario = function (text) {
        return gettext('scenario ' + text);
    };
    self.helptextexample = function (text) {
        return gettext('example ' + text);
    };
    self.displayExample = function (text) {
        var example_text = gettext('example ' + text);
        return ( example_text != " ")
    };
    self.isValid = ko.computed(function () {
        var valid_fields = $.map(self.accountMessages(), function (e) {
            return e.message.valid()
        });
        return valid_fields.indexOf(false) == -1;
    }, self);

    self.save = function (callback) {
        if (!self.isValid()) return;
        DW.loading();
        accountWideSmsViewModel.saveButtonText(gettext("Saving..."));
        $.post(post_url, {
                'data': JSON.stringify(ko.toJS(accountWideSmsViewModel)),
                'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
            },
            function (data) {
                data = JSON.parse(data);
                accountWideSmsViewModel.saveButtonText(gettext("Save"));
                displaySuccessMessage(data);
                resetAccountMsgWarningDisplay();
                self.accountMessagesInitialState(ko.toJSON(self.accountMessages()));
                if (typeof callback == "function") callback();
            }
        );

    };
}

function createObservableMessageItemsFor(data, messageObservable, initialStateObservable, msgChangeWarning) {
    var messages = [];
    for (var i = 0; i < data.length; i++) {
        var messageItem = DW.ko.createValidatableObservable({value: data[i].message});
        var count = ko.observable(0);
        var customized_message_item = { "code": data[i].code, "title": data[i].title, "message": messageItem, "count": count };
        messageItem.subscribe(function () {
            DW.ko.mandatoryValidator(this.message, gettext("Enter reply SMS text."));
        }, customized_message_item);
        if (msgChangeWarning) {
            customized_message_item.displayWarning = ko.observable(false);
        }
        messages.push(customized_message_item);
    }
    messageObservable(messages);
    initialStateObservable(ko.toJSON(messageObservable()))
}

function resetAccountMsgWarningDisplay(){
    var messages = accountWideSmsViewModel.accountMessages();
    for(var i=0;i<messages.length;i++){
        messages[i].displayWarning(false);
    }
}

$(function(){
    window.accountWideSmsViewModel= new AccountWideSmsViewModel();
    ko.applyBindings(accountWideSmsViewModel);

    createObservableMessageItemsFor(account_messages, accountWideSmsViewModel.accountMessages, accountWideSmsViewModel.accountMessagesInitialState,true);
    initializeWarningDialog();
});


function initializeWarningDialog() {
    var options = {
        successCallBack: function (callback) {
            accountWideSmsViewModel.save(callback);
        },
        isQuestionnaireModified: function () {
            return accountWideSmsViewModel.isAccountMessageModified();
        },
        cancelDialogDiv: "#cancel_language_changes_warning",
        validate: function () {
            return accountWideSmsViewModel.isValid();
        },
        ignore_links: "#cancel_changes"
    };
    new DW.CancelWarningDialog(options).init().initializeLinkBindings();
}