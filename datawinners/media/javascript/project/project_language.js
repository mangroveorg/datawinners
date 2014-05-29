function ProjectLanguageViewModel(){
  var self = this;

  self.available_languages = [];
  self.enable_sms_replies = ko.observable(true);
  self.selected_language = ko.observable();
  self.is_modified = false;

  var _is_add_new_language_option_selected = function(language_option){
      return language_option == self.available_languages[self.available_languages.length-1].code;
  };

  self.selected_language.subscribe(function(language_option){
      if(_is_add_new_language_option_selected(language_option)){
          window.location.href = language_page_link;
      }
      self.is_modified = true;
  });

  self.enable_sms_replies.subscribe(function(){
      self.is_modified = true;
  });

  self.save = function(){
      var data = {
        'enable_sms_replies': self.enable_sms_replies(),
        'selected_language': self.selected_language(),
        'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
      };
      $.ajax({
          type: "POST",
          url: post_url,
          data: data,
          success: function(response){
              if(response.success){
                self.is_modified = false;
                flash_message("#flash-message-section", "Changes saved successfully", true);
              }
              else{
                flash_message("#flash-message-section", "Save Failed!", false);
              }
          },
          dataType: 'json'
      });
  };

}

$(function(){
    var viewModel = new ProjectLanguageViewModel();
    viewModel.available_languages = languages_list;
    viewModel.available_languages.push({name: gettext('Add a new language on the Languages page'), code: 'new_lang'});
    viewModel.selected_language(current_project_language);
    viewModel.is_modified = false;

    var options = {
        successCallBack:function(callback){
            viewModel.save();
            callback();
        },
        isQuestionnaireModified : function(){return viewModel.is_modified;},
        cancelDialogDiv : "#cancel_language_changes_warning",
        validate: function(){
            return true;
        }
    };
    new DW.CancelWarningDialog(options).init().initializeLinkBindings();
    ko.applyBindings(viewModel, $("#project_language_section")[0]);

    var add_language_option = $("#project_language option:last-child");
    add_language_option.attr('id', 'language_page_link');
});