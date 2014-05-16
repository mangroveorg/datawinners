$(document).ready(function () {
    function LanguageViewModel() {
        var self = this;
        self.availableLanguages = languages;
        self.language = ko.observable();
        self.customizedMessages = ko.observableArray();
        self.saveButtonText = ko.observable(gettext("Save"));
        self.language.subscribe(function () {
            $.getJSON("/languages/custom_messages", {'language': languageViewModel.language()}).success(function (data) {
                var customized_messages = [];
                for (var i in data) {
                    var messageItem = DW.ko.createValidatableObservable({value: data[i].message});
                    var customized_message_item = { "code": data[i].code, "title": data[i].title, "message": messageItem };
                    messageItem.subscribe(function () {
                        DW.ko.mandatoryValidator(this.message, gettext("Enter reply SMS text."));
                    }, customized_message_item);
                    customized_messages.push(customized_message_item);
                }
                languageViewModel.customizedMessages(customized_messages);
            });
        }, self, 'change');
        self.isValid=ko.computed(function(){
            var valid_fields = $.map(self.customizedMessages(), function(e){return e.message.valid()});
            return valid_fields.indexOf(false) == -1;
        }, self.customizedMessages);
        self.save = function () {
            if (!self.isValid()) return;
            DW.loading();
            languageViewModel.saveButtonText(gettext("Saving..."));
            $.post('/languages/custom_messages', {
                    'data': JSON.stringify(ko.toJS(languageViewModel))},
                function (data) {
                    data = JSON.parse(data);
                    $(".save").text(gettext('Save'));
                    $('.success-message-box').text(data["message"]);
                    $('.success-message-box').show();
                }
            );

        };
    }

    window.languageViewModel = new LanguageViewModel();
    ko.applyBindings(languageViewModel);
    languageViewModel.language(current_language);

});

