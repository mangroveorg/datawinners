function set_current_tab(){
      var current_element = $("#tab_items .current");
      var current_tab = $("#tab_items li").index(current_element)+1;
      var wizard_slider = $("#step_wizard").slider({
               range: "max",
               min: 1,
               max: 6,
               value: current_tab,
               disabled:true
      });

}

