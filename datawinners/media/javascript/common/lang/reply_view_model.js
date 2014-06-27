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

    self.isMessageModified = ko.observable(false);

    self.resetModifiedFlag = function(){
        $.each(self.messages(),function(i,messageItem){
            messageItem.isModified(false);
        });
    };

    self.resetModifiedFlagForAllMessages = function(){
        self.resetModifiedFlag();
        self.isMessageModified(false);
    }

    self.resetChanges = function(){
        if(!self.isMessageModified()){
            return;
        }

        var initialState = $.parseJSON(self.messagesInitialState());
        $.each(self.messages(),function(index,element){
            element.message.clearError();
            element.message(initialState[index].message);
        });
        $(".TextTags").each(function(i, tag){
            $(tag).TextNTags("create", self.messages()[i].message());
        });

        self.resetModifiedFlagForAllMessages();
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

function createObservableMessageItemsFor(data, viewModel, msgChangeWarning) {
    var messageObservable = viewModel.messages;
    var initialStateObservable = viewModel.messagesInitialState;
    var messages = [];
    for (var i = 0; i < data.length; i++) {
        var messageItem = DW.ko.createValidatableObservable({value: data[i].message});
        var count = ko.observable(0);
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

        var isModified = ko.observable(false);
        var customized_message_item = { "code": data[i].code, "title": gettext(data[i].title), "message": messageItem, "count": count ,"isModified":isModified};
        messageItem.subscribe(function () {
            DW.ko.mandatoryValidator(this.message, gettext("Enter reply SMS text."));
            this.isModified(true);
        }, customized_message_item);

        isModified.subscribe(function(){
            viewModel.isMessageModified(true);
        });

        if (msgChangeWarning) {
            customized_message_item.displayWarning = ko.observable(false);
        }
        messages.push(customized_message_item);
    }
    messageObservable(messages);
    initialStateObservable(ko.toJSON(messageObservable()))
}
