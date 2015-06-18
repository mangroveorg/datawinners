$(document).ready(function(){
    var title;
    if (is_poll){
        title = gettext("Delete this Poll?");
    }
    else{
        title = gettext("Delete this Questionnaire?");
    }
   $("#delete_project_block").dialog({
        title: title,
        modal: true,
        autoOpen: false,
        height: 150,
        width: 'auto',
        closeText: 'hide'
      }
   );

   $("#delete_project_block .cancel_link").bind("click", function() {
       $("#delete_project_block").dialog("close");
       return false;
   });
});
