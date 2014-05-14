$(document).ready(function(){
    function LanguageViewModel(){
        var self = this;
        self.availableLanguages = languages;
        self.language = ko.observable();
    }
    window.languageViewModel = new LanguageViewModel();
    ko.applyBindings(languageViewModel);
    languageViewModel.language(current_language)
});