$(document).ready(function () {
    function LanguageViewModel() {
        var self = this;
        self.availableLanguages = languages;
        self.language = ko.observable();
        self.customizedMessages = ko.observableArray();
        self.language.subscribe(function () {
            $.getJSON("/languages/custom_messages", {'language': languageViewModel.language()}).success(function (data) {
                for (var i in data) {
                    var messageItem = DW.ko.createValidatableObservable({value:data[i].message});
                    var customized_message_item = { "code": data[i].code, "title": data[i].title, "message": messageItem };
                    messageItem.subscribe(function () {
                        DW.ko.mandatoryValidator(this.message,gettext("Enter reply SMS text."));
                    }, customized_message_item);
                    languageViewModel.customizedMessages.push(customized_message_item);
                }
            });
        }, self, 'change');
    }

    window.languageViewModel = new LanguageViewModel();
    ko.applyBindings(languageViewModel);
    languageViewModel.language(current_language);
});

