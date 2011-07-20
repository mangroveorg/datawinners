$(document).ready(function() {
                $(".subject_registration_preview").dialog({
                title: "Subject Registration Preview",
                modal: true,
                autoOpen: false,
                height: 700,
                width: 800,
                closeText: 'hide',
                open: function() {
                  // Here I load the content. This is the content of your link.
                  $(".subject_registration_preview").load(subject_registration_form_preview_link, function() {});
                }
              }
          );

        $(".preview_subject_registration_form").bind("click", function(){
           $(".subject_registration_preview").dialog("open");
        });

});