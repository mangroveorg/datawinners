function ReplyMessageViewModel(){
    var self = this;

    self.saveButtonText = ko.observable(gettext("Save"));

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

    self.messages = ko.observableArray();

    self.messagesInitialState = ko.observable();

    self.isMessageModified = ko.computed(function() {
        return self.messagesInitialState() != ko.toJSON(self.messages());
    }, self);

    self.isMessageItemChanged = function (messageCode, messageText) {
        if (self.messagesInitialState()) {
            var initialMessages = JSON.parse(self.messagesInitialState());
            for (var i = 0; i < initialMessages.length; i++) {
                if (initialMessages[i].code == messageCode) {
                    return initialMessages[i].message != messageText;
                }
            }
        }
        return false;
    };

    self.resetChanges = function(){
        if(!self.isMessageModified())return;
        var initialState = $.parseJSON(self.messagesInitialState());
        $.each(self.messages(),function(index,element){
            element.message.clearError();
            element.message(initialState[index].message);
        });
        $(".TextTags").each(function(i, tag){
            $(tag).TextNTags("create", self.messages()[i].message());
        });
    };

    self.isValid = ko.computed(function () {
        var valid_fields = $.map(self.messages(), function (e) {
            return e.message.valid()
        });
        return valid_fields.indexOf(false) == -1;
    }, self);

    self.isSaveDisabled = ko.computed(function(){
        return !self.isMessageModified();
    })
}

function createObservableMessageItemsFor(data, messageObservable, initialStateObservable, msgChangeWarning) {
    var messages = [];
    for (var i = 0; i < data.length; i++) {
        var messageItem = DW.ko.createValidatableObservable({value: data[i].message});
        var count = ko.observable(0);
        var customized_message_item = { "code": data[i].code, "title": gettext(data[i].title), "message": messageItem, "count": count };

        messageItem.sys_variable_modified = ko.observable(false);
        messageItem.clearError = function () {
            this.sys_variable_modified(false);
            this.valid(true);
            this.error("");
        };

        messageItem.is_errored = ko.computed(function () {
            return !this.valid() || this.sys_variable_modified()
        }, messageItem);

        messageItem.setSysVariableError = function (error_message) {
            this.sys_variable_modified(true);
            this.error(error_message);
        };

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
