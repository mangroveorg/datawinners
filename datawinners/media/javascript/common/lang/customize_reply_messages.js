function open_add_language_popup(e) {
    $("#language option[value=" + languageViewModel.language() + "]").attr("selected", "selected");
    e.preventDefault();
    $('#add_new_language_pop').dialog('open');
    languageViewModel.newLanguageName("");
    languageViewModel.newLanguageName.clearError();
    return false;
}
$(document).ready(function () {
    window.languageViewModel = new LanguageViewModel();
    ko.applyBindings(languageViewModel);
    languageViewModel.language(current_language);
    appendAddNewLanguageOption();

    initializeWarningDialogs();

    $("#language").change(function (e) {
        if (languageViewModel.isCustomizedMessageModified()) {
            e.preventDefault();

            language_change_warning_dialog.show();
            return false;
        }

        if ($("#language").val() === "add_new") {
            return open_add_language_popup(e);
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
            return languageViewModel.isCustomizedMessageModified();
        },
        cancelDialogDiv: "#cancel_language_changes_warning",
        validate: function () {
            return languageViewModel.isValid();
        },
        ignore_links: "#cancel_changes"
    };
    new DW.CancelWarningDialog(options).init().initializeLinkBindings();
    var language_change_warning_dialog_options = $.extend(options, {
        cancelCallback: function () {
            resetPreviousLanguage();
        },
        actionCallback: function (e) {
            var selected_language = $("#language option:selected").val();
            if(selected_language=="add_new"){
                open_add_language_popup(e);
            }else{
            languageViewModel.language(selected_language);}
        }
    });
    language_change_warning_dialog = new DW.CancelWarningDialog(language_change_warning_dialog_options);
    language_change_warning_dialog.init();

    $("#add_new_language_pop").dialog({
        autoOpen: false,
        zIndex: 200,
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
