function displaySuccessMessage(data) {
    $('.success-message-box').text(data["message"]);
    $('.success-message-box').show();
    $('.success-message-box')[0].scrollIntoView();
}
function LanguageViewModel() {
    var self = this;
    self.availableLanguages = ko.observableArray(languages);
    self.language = ko.observable();
    self.language_display = ko.computed(function() {
        return self.language();
    });
    self.customizedMessages = ko.observableArray();
    self.customizedMessagesInitialState = ko.observable();
    self.isCustomizedMessageModified = ko.computed(function () {
        return self.customizedMessagesInitialState() != ko.toJSON(self.customizedMessages());
    }, self);

    self.resetChanges = function(){
        var initialState = $.parseJSON(self.customizedMessagesInitialState());
        $.each(self.customizedMessages(),function(index,element){
            element.message.clearError();
            var msg = initialState[index].message;
            element.message(msg);
        });
        $(".TextTags").each(function(i, tag){
            var message = self.customizedMessages()[i].message();
            $(tag).TextNTags("create", message);
        });
    };

    self.saveButtonText = ko.observable(gettext("Save"));
    self.addLanguageText = ko.observable(gettext("Add Language"));

    self.newLanguageName = DW.ko.createValidatableObservable({value: ""});
    var languageNameEmptyMessage = gettext("Please enter a name for your language.");
    self.newLanguageName.subscribe(function () {
            DW.ko.mandatoryValidator(self.newLanguageName, languageNameEmptyMessage);
        }
    );
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
    }, self);

    self.sortLanguages = function () {
        self.availableLanguages.sort(function (left, right) {
            return left.name.toLowerCase() == right.name.toLowerCase() ? 0 : (left.name.toLowerCase() < right.name.toLowerCase() ? -1 : 1)
        });
    };

    self.save = function (callback) {
        if (!self.isValid()) return;
        DW.loading();
        languageViewModel.saveButtonText(gettext("Saving..."));
        $.post(post_url, {
                'data': JSON.stringify(ko.toJS(languageViewModel)),
                'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
            },
            function (data) {
                data = JSON.parse(data);
                languageViewModel.saveButtonText(gettext("Save"));
                displaySuccessMessage(data);
                self.customizedMessagesInitialState(ko.toJSON(self.customizedMessages()));
                if (typeof callback == "function") callback();
            }
        );

    };
    self.addLanguage = function () {
        if (self.newLanguageName() && self.newLanguageName.valid()) {
            self.addLanguageText(gettext("Adding..."));
            DW.loading();
            $('#add_new_language_pop .yes_button').addClass('ui-state-disabled');
            $.post('/languages/create', {"language_name": self.newLanguageName()})
                .done(function (responseString) {
                    var response = $.parseJSON(responseString);
                    if (response.language_code) {
                        self.addLanguageText(gettext("Add Language"));
                        $('#add_new_language_pop .yes_button').removeClass('ui-state-disabled');
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
                        self.addLanguageText(gettext("Add Language"));
                        $('#add_new_language_pop .yes_button').removeClass('ui-state-disabled');
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
