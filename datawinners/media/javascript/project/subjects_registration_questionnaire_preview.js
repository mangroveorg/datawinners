$(document).ready(function() {
                $(".subject_registration_preview").clone().dialog({
                title: gettext("Subject Registration Preview"),
                modal: true,
                autoOpen: false,
                height: 700,
                width: 800,
                closeText: 'hide',
                open: function() {
                  $("body > div").addClass("none_for_print");
                  $(".subject_registration_preview").load();
                },
                close: function(){
                    $("body > div").removeClass("none_for_print");
                }
              }
          );

        $(".preview_subject_registration_form").bind("click", function(){
           $(".subject_registration_preview").dialog("open");
            return false;
        });

});
