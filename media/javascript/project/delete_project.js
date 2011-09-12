$(document).ready(function(){
   $("#delete_project_block").dialog({
        title: gettext("Delete this Project?"),
        modal: true,
        autoOpen: false,
        height: 200,
        width: 300,
        closeText: 'hide'
      }
   );
   $(".delete_project").bind("click", function(){
       $("#delete_project_block").dialog("open");
       $('#confirm_delete').attr('href',$(this).attr('href'));
       return false;
   });
   $("#delete_project_block .cancel_link").bind("click", function(){
         $("#delete_project_block").dialog("close");
   });
});
