$(document).ready(function(){
   $("#delete_project_block").dialog({
        title: gettext("Delete this Project?"),
        modal: true,
        autoOpen: false,
        height: 150,
        width: 370,
        closeText: 'hide'
      }
   );
   $(".delete_project").bind("click", function(){
       $("#delete_project_block").dialog("open");
       var project_id = $(this).attr('href').split('/')[3];
       $('#confirm_delete').attr('href',$(this).attr('href'));
       $('#undo_delete_project').attr('href', '/project/undelete/'+project_id+"/");
       $('#undelete_project_section').show().hide(50000);
       return false;
   });
    $("#delete_project_block .cancel_link").bind("click", function() {
        $("#delete_project_block").dialog("close");
        return false;
    });
});
