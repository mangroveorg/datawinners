function ProjectLanguageViewModel(){
  var self = this;

  self.available_languages = [];
  self.enable_sms_replies = ko.observable(true);

  self.is_outgoing_sms_disabled = ko.computed(function(){
      return !self.enable_sms_replies();
  }, self);

  self.selected_language = ko.observable();
  self.is_modified = false;
  self.save_text = ko.observable(gettext('Save'));

  self.selected_language.subscribe(function(language_option){
      self.is_modified = true;
  });

  self.enable_sms_replies.subscribe(function(){
      self.is_modified = true;
  });

//  introducing to prevent default event handler coming in place of callback
  self.save_and_reload = function(){
      self.save();
  };

  self.save = function(callback){
      var params = _.isUndefined(callback) ? "?resp_message=1" : "";
      var data = {
        'enable_sms_replies': self.enable_sms_replies(),
        'selected_language': self.selected_language(),
        'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
      };
      self.save_text(gettext('Saving...'));
      DW.loading();
      $.ajax({
          type: "POST",
          url: post_url + params,
          data: data,
          success: function(response){
              self.save_text(gettext('Save'));
              if(response.success){
                  self.is_modified = false;
                  if(callback)
                    callback();
                  else
                    window.location.reload();
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
    viewModel.selected_language(current_project_language);
    viewModel.enable_sms_replies(is_outgoing_reply_messages_enabled == 'True');
    viewModel.is_modified = false;

    var options = {
        successCallBack:function(callback){
            viewModel.save(callback);
        },
        isQuestionnaireModified : function(){return viewModel.is_modified;},
        cancelDialogDiv : "#cancel_language_changes_warning",
        validate: function(){
            return true;
        }
    };
    new DW.CancelWarningDialog(options).init().initializeLinkBindings();
    ko.applyBindings(viewModel, $("#project_language_section")[0]);
});