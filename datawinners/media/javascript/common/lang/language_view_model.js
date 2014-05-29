function LanguageViewModel() {
    var self = this;
    self.availableLanguages = ko.observableArray(languages);
    self.language = ko.observable();
    self.language_display = ko.computed(function () {
        return self.language();
    });
    self.customizedMessages = ko.observableArray();
    self.customizedMessagesInitialState = ko.observable();
    self.isCustomizedMessageModified = ko.computed(function () {
        return self.customizedMessagesInitialState() != ko.toJSON(self.customizedMessages());
    }, self);


    self.accountMessages = ko.observableArray();
    self.accountMessagesInitialState = ko.observable();
    self.isAccountMessageModified = ko.computed(function () {
        return self.accountMessagesInitialState() != ko.toJSON(self.accountMessages());
    }, self);

    self.saveButtonText = ko.observable(gettext("Save"));

    self.newLanguageName = DW.ko.createValidatableObservable({value: ""});
    var languageNameEmptyMessage = gettext("Please enter a name for your language.");
    self.newLanguageName.subscribe(function () {
            DW.ko.mandatoryValidator(self.newLanguageName, languageNameEmptyMessage);
        }
    );


    self.language.subscribe(function () {
        $.getJSON("/languages/custom_messages", {'language': languageViewModel.language()}).success(function (data) {
            createObservableMessageItemsFor(data, languageViewModel.customizedMessages,
                languageViewModel.customizedMessagesInitialState);
        });
    }, self, 'change');
    self.isValid = ko.computed(function () {
        var valid_fields = $.map(self.customizedMessages(), function (e) {
            return e.message.valid()
        });
        return valid_fields.indexOf(false) == -1;
    }, self.customizedMessages);

    self.sortLanguages = function () {
        self.availableLanguages.sort(function (left, right) {
            return left.name.toLowerCase() == right.name.toLowerCase() ? 0 : (left.name.toLowerCase() < right.name.toLowerCase() ? -1 : 1)
        });
    };

    self.save = function (callback) {
        if (!self.isValid()) return;
        DW.loading();
        languageViewModel.saveButtonText(gettext("Saving..."));
        $.post('/languages/custom_messages', {
                'data': JSON.stringify(ko.toJS(languageViewModel))},
            function (data) {
                data = JSON.parse(data);
                languageViewModel.saveButtonText(gettext("Save"));
                $('.success-message-box').text(data["message"]);
                $('.success-message-box').show();
                self.customizedMessagesInitialState(ko.toJSON(self.customizedMessages()));
                self.accountMessagesInitialState(ko.toJSON(self.accountMessages()));
                if (typeof callback == "function") callback();
            }
        );

    };
    self.addLanguage = function () {
        if (self.newLanguageName() && self.newLanguageName.valid()) {
            $.post('/languages/create', {"language_name": self.newLanguageName()})
                .done(function (responseString) {
                    var response = $.parseJSON(responseString);
                    if (response.language_code) {
                        $('#add_new_language_pop').dialog('close');
                        self.availableLanguages.pop();
                        self.availableLanguages.push({code: response.language_code, name: response.language_name});
                        self.sortLanguages();
                        appendAddNewLanguageOption();
                        self.language(response.language_code);
                        $('.success-message-box').text(gettext("Language Added successfully"));
                        $('.success-message-box').show();

                    } else {
                        self.newLanguageName.setError(response.message);
                    }
                })
        } else {
            if (!self.newLanguageName())
                self.newLanguageName.setError(languageNameEmptyMessage);
        }
    };

    self.cancelAddLanguage = function () {
        $('#add_new_language_pop').dialog('close');
    }
}

function createObservableMessageItemsFor(data, messageObservable, initialStateObservable) {
    var messages = [];
    for (var i = 0; i < data.length; i++) {
        var messageItem = DW.ko.createValidatableObservable({value: data[i].message});
        var count = ko.computed(function () {
            return this().length;
        }, messageItem);
        var customized_message_item = { "code": data[i].code, "title": data[i].title, "message": messageItem, "count": count };
        messageItem.subscribe(function () {
            DW.ko.mandatoryValidator(this.message, gettext("Enter reply SMS text."));
        }, customized_message_item);
        messages.push(customized_message_item);
    }
    messageObservable(messages);
    initialStateObservable(ko.toJSON(messageObservable()))
}


