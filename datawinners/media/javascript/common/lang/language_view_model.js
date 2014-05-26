$(document).ready(function () {
    function LanguageViewModel() {
        var self = this;
        self.availableLanguages = ko.observableArray(languages);
        var add_language_option = {code: "add_new", name: "Add a new language"};
        self.availableLanguages.push(add_language_option);
        self.language = ko.observable();
        self.language_display = ko.computed(function () {
            return self.language();
        });
        self.customizedMessages = ko.observableArray();
        self.saveButtonText = ko.observable(gettext("Save"));
        self.initialState = ko.observable();
        self.isModified = ko.computed(function () {
            return self.initialState() != ko.toJSON(self.customizedMessages());
        }, self);
        self.newLanguageName = DW.ko.createValidatableObservable({value: ""});
        self.newLanguageName.subscribe(function () {
                DW.ko.mandatoryValidator(self.newLanguageName, gettext("Enter valid language name."));
            }
        );
        self.sortLanguages = function () {
                    self.availableLanguages.sort(function(left, right) {
                        return left.name == right.name ? 0 : (left.name < right.name ? -1 : 1)
                    });
                };
        self.language.subscribe(function () {
            $.getJSON("/languages/custom_messages", {'language': languageViewModel.language()}).success(function (data) {
                var customized_messages = [];
                for (var i = 0; i < data.length; i++) {
                    var messageItem = DW.ko.createValidatableObservable({value: data[i].message});
                    var customized_message_item = { "code": data[i].code, "title": data[i].title, "message": messageItem };
                    messageItem.subscribe(function () {
                        DW.ko.mandatoryValidator(this.message, gettext("Enter reply SMS text."));
                    }, customized_message_item);
                    customized_messages.push(customized_message_item);
                }
                languageViewModel.customizedMessages(customized_messages);
                languageViewModel.initialState(ko.toJSON(languageViewModel.customizedMessages()))

            });
        }, self, 'change');
        self.isValid = ko.computed(function () {
            var valid_fields = $.map(self.customizedMessages(), function (e) {
                return e.message.valid()
            });
            return valid_fields.indexOf(false) == -1;
        }, self.customizedMessages);
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
                    self.initialState(ko.toJSON(self.customizedMessages()));
                    self.availableLanguages.remove(add_language_option);
                    self.sortLanguages();
                    self.availableLanguages.push(add_language_option);
                    if (typeof callback == "function") callback();
                }
            );

        };
        self.addLanguage = function () {
            $.post('/languages/create', {"language_name": self.newLanguageName()})
                .done(function (responseString) {
                    var response = $.parseJSON(responseString);
                    if (response.language_code) {
                        $('#add_new_language_pop').dialog('close');
                        self.availableLanguages.push({code: response.language_code, name: response.language_name});
                        self.availableLanguages.remove(add_language_option);
                        self.sortLanguages();
                        self.availableLanguages.push(add_language_option);
                        self.language(response.language_code);
                    }else{
                      self.newLanguageName.setError(response.message);
                    }
                })
        };

        self.cancelAddLanguage = function () {
            $('#add_new_language_pop').dialog('close');
            resetPreviousLanguage();
        }
    }


    window.languageViewModel = new LanguageViewModel();
    ko.applyBindings(languageViewModel);
    languageViewModel.language(current_language);
    var options = {
        successCallBack: function (callback) {
            languageViewModel.save(callback);
        },
        isQuestionnaireModified: function () {
            return languageViewModel.isModified();
        },
        cancelDialogDiv: "#cancel_language_changes_warning",
        validate: function () {
            return languageViewModel.isValid();
        }
    };
    new DW.CancelWarningDialog(options).init().initializeLinkBindings();
    var language_change_warning_dialog_options = $.extend(options, {
        cancelCallback: function () {
            $("#language option[value=" + languageViewModel.language() + "]").attr("selected", "selected");
        },
        actionCallback: function () {
            languageViewModel.language($("#language option:selected").val());
        }
    });
    var language_change_warning_dialog = new DW.CancelWarningDialog(language_change_warning_dialog_options);
    language_change_warning_dialog.init();

    $("#language").change(function (e) {
        if (languageViewModel.isModified()) {
            e.preventDefault();

            language_change_warning_dialog.show();
            return false;
        }
        ;
        if ($("#language").val() === "add_new") {
            e.preventDefault();
            $('#add_new_language_pop').dialog('open');
            languageViewModel.newLanguageName("");
            languageViewModel.newLanguageName.clearError();
            return false;
        }
        DW.loading();
        languageViewModel.language($("#language option:selected").val());
    });

    initializeNewLanguageDialog();
});

function initializeNewLanguageDialog() {
    $("#add_new_language_pop").dialog({
        autoOpen: false,
        width: 600,
        modal: true,
        title: gettext('Add Language')
    });

}

function resetPreviousLanguage(){
    $("#language option[value=" + languageViewModel.language() + "]").attr("selected", "selected");
}

