$(document).ready(function () {
    window.languageViewModel = new LanguageViewModel();
    ko.applyBindings(languageViewModel);
    languageViewModel.language(current_language);
    appendAddNewLanguageOption();

    initializeWarningDialogs();

    $("#language").change(function (e) {
        if (languageViewModel.isModified()) {
            e.preventDefault();

            language_change_warning_dialog.show();
            return false;
        } ;

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


});

function initializeWarningDialogs() {
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

    $("#add_new_language_pop").dialog({
        autoOpen: false,
        width: 450,
        modal: true,
        title: gettext('Add Language'),
        resizable: false
    });
}

function resetPreviousLanguage() {
    $("#language option[value=" + languageViewModel.language() + "]").attr("selected", "selected");
}

function appendAddNewLanguageOption() {
    var add_language_option = {code: "add_new", name: gettext("Add Language")};
    languageViewModel.availableLanguages.push(add_language_option);
}

//This method is being used for restricting number of characters to 160 in message box
var first160chars = function (str) {
    var val = str();
    if (val.length > 160)
        str(val.substring(0, 160));
    return str;
};
