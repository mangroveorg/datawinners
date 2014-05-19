$(document).ready(function () {
    function LanguageViewModel() {
        var self = this;
        self.availableLanguages = languages;
        self.language = ko.observable();
        self.customizedMessages = ko.observableArray();
        self.saveButtonText = ko.observable(gettext("Save"));
        self.initialState = ko.observable();
        self.isModified = ko.computed(function(){
            return self.initialState() != ko.toJSON(self.customizedMessages());
        },self);

        self.language.subscribe(function () {
            if(self.initialState() && self.isModified()){

            }
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
                languageViewModel.initialState(ko.toJSON(languageViewModel.customizedMessages()))

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
    var options = {
        successCallBack:function(callback){
            languageViewModel.save();
            callback();
        },
        isQuestionnaireModified : function(){return languageViewModel.isModified();},
        cancelDialogDiv : "#cancel_language_changes_warning",
        validate: function(){
            return languageViewModel.isValid();
        },
        triggerLinks:"#language"
    };
    new DW.CancelWarningDialog(options).init();
});

