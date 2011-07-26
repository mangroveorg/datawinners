function set_current_tab(){
  var current_element = $("#tab_items .current");
  var current_tab = $("#tab_items li").index(current_element)+1;
  var wizard_slider = $("#step_wizard").slider({
           range: "max",
           min: 1,
           max: 5,
           value: current_tab,
           disabled:true
  });
}
$(document).ready(function(){
   $("#cancel_project_block").dialog({
        title: "Cancel this Project?",
        modal: true,
        autoOpen: false,
        height: 200,
        width: 300,
        closeText: 'hide'
      }
   );
   $(".cancel").bind("click", function(){
       $("#cancel_project_block").dialog("open");
   })
    $(".cancel_link").bind("click", function(){
         $("#cancel_project_block").dialog("close");
    })
})


