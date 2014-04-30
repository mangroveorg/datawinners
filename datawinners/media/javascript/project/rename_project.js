$(function(){
    $.inlineEdit({"project_title":"/project/rename/"},
        {
            getId: function($el){ return $el.attr('pid');},
            animate: false,
            colors: { success: 'darkblue', error: 'red' },
            save_label:gettext("Save"),
            beforeSave: function(editFieldSection){
                editFieldSection.find('button').text(gettext("Saving..."));
            },
            afterSave: function(result){
                var editFieldSection = result.editFieldSection;
                editFieldSection.find('button').text(gettext("Save"));
            },
            cancel_label:gettext("Cancel")
        });

   $(".project_rename").click(function(){
       $(".project_title").trigger('click');
   })
});