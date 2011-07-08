    // DW is the global name space on which all the function/methods will be attached through out the site
    // This is to avoid introducing global functions/methods/variables in each page
    // which could pollute the global namespace and make path for conflicting between the variable/function/method names, which would make debugging tough.
    var DW = {};

    $(document).ready(function(){
          $.addwatermarks();
          $(".help_icon").tooltip({
                      position: "top right",
                      opacity:0.6,
                      events: {
                          def:     "click,blur",
                          input:   "focus,blur",
                          widget:  "focus mouseover,blur mouseout",
                          tooltip: "click,click"
                      }

          });

    })


