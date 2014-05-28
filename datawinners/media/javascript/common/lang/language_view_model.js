var first160chars = function(str){
    var val = str();
    if (val.length>160)
        str(val.substring(0,160));
    return str;
}

$(document).ready(function () {
    function LanguageViewModel() {
        var self = this;
        self.availableLanguages = ko.observableArray(languages);
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
                DW.ko.mandatoryValidator(self.newLanguageName, gettext("Please enter a name for your language."));
            }
        );


        self.language.subscribe(function () {
            $.getJSON("/languages/custom_messages", {'language': languageViewModel.language()}).success(function (data) {
                var customized_messages = [];
                for (var i = 0; i < data.length; i++) {
                    var messageItem = DW.ko.createValidatableObservable({value: data[i].message});
                    var count = ko.computed(function(){
                        return this().length;
                    }, messageItem)
                    var customized_message_item = { "code": data[i].code, "title": data[i].title, "message": messageItem, "count":count };
                    messageItem.subscribe(function () {
                        DW.ko.mandatoryValidator(this.message, gettext("Enter reply SMS text.")) &&
                        DW.ko.customValidator(this.message, "Text should be less than 160 chars", function(val){return (val+"").length<160;})

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

        self.sortLanguages = function () {
            self.availableLanguages.sort(function(left, right) {
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
                    self.initialState(ko.toJSON(self.customizedMessages()));
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
                        self.availableLanguages.pop();
                        self.availableLanguages.push({code: response.language_code, name: response.language_name});
                        self.sortLanguages();
                        appendAddNewLanguageOption();
                        self.language(response.language_code);
                        $('.success-message-box').text(gettext("Language Added succesfully"));
                        $('.success-message-box').show();

                    }else{
                      self.newLanguageName.setError(response.message);
                    }
                })
        };

        self.cancelAddLanguage = function () {
            $('#add_new_language_pop').dialog('close');
        }
    }


    window.languageViewModel = new LanguageViewModel();
    ko.applyBindings(languageViewModel);
    languageViewModel.language(current_language);
    languageViewModel.sortLanguages();
    appendAddNewLanguageOption();

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
            resetPreviousLanguage();
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
            $("#language option[value=" + languageViewModel.language() + "]").attr("selected", "selected");
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
        width: 450,
        modal: true,
        title: gettext('Add Language'),
        resizable:false
    });

}

function resetPreviousLanguage(){
    $("#language option[value=" + languageViewModel.language() + "]").attr("selected", "selected");
}

function appendAddNewLanguageOption(){
        var add_language_option = {code: "add_new", name: gettext("Add Language")};
        languageViewModel.availableLanguages.push(add_language_option);
}


