function open_add_language_popup(e){
    $("#language option[value=" + languageViewModel.language() + "]").attr("selected", "selected");
    $('#add_new_language_pop').dialog('open');
    languageViewModel.newLanguageName("");
    languageViewModel.newLanguageName.clearError();
    return false;
}

var add_lang_called = false;

$(document).ready(function () {
    window.languageViewModel = new QuestionnaireReplyViewModel();
    languageViewModel.language(current_language);
    ko.applyBindings(languageViewModel);
    initializeWarningDialogs();

    $("#language").change(function (e) {
        if (languageViewModel.isMessageModified()) {
            e.preventDefault();

            language_change_warning_dialog.show();
            return false;
        }
        DW.loading();
        languageViewModel.language($("#language option:selected").val());
    });

    $("#add_language_link").click(function(e){
        if (languageViewModel.isMessageModified()) {
            e.preventDefault();
            add_lang_called = true;
            language_change_warning_dialog.show();
            return false;
        }else
            open_add_language_popup(e);
    });

    $("#language_customized_messages").on('click', ".reset-link", function(event){
        languageViewModel.resetMessage(event, ko.dataFor(this));
    });

    _initializeLearnMoreDialog();

});

function _initializeLearnMoreDialog(){
    var learnMoreOptions = {
        link_selector: "#learn_more_link",
        title: "Learn How to Add and Edit Languages",
        dialogDiv: "#questionnaire_reply_sms_learn_more",
        width:900
    };
    new DW.Dialog(learnMoreOptions).init().initializeLinkBindings();
}

function initializeWarningDialogs() {
    var options = {
        successCallBack: function (callback) {
            languageViewModel.save(callback);
        },
        ignoreCallback: function(){
            languageViewModel.resetModifiedFlagForAllMessages();
        },
        isQuestionnaireModified: function () {
            return languageViewModel.isMessageModified();
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
            languageViewModel.language(selected_language);
            languageViewModel.resetModifiedFlagForAllMessages();
            if(add_lang_called){
                add_lang_called = false;
                open_add_language_popup(e);
            }
        }
    });
    language_change_warning_dialog = new DW.CancelWarningDialog(language_change_warning_dialog_options);
    language_change_warning_dialog.init();

    var cancelPopupOptions = {
        ignoreCallback: function (callback) {
            languageViewModel.resetChanges();
        },
        title: "Cancel Changes",
        link_selector: "#cancel_changes",
        dialogDiv: "#revert_changes_warning",
        cancelLinkSelector :"#keep_changes",
        width: 580,
        openPredicate: function(){return languageViewModel.isMessageModified();}
    };
    new DW.Dialog(cancelPopupOptions).init().initializeLinkBindings();

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
