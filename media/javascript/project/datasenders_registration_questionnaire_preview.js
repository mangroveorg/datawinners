$(document).ready(function() {
    $(".sender_registration_preview").dialog({
        title: "Data Sender Registration Preview",
        modal: true,
        autoOpen: false,
        height: 700,
        width: 800,
        closeText: 'hide',
        open: function() {
            // Here I load the content. This is the content of your link.
            $(".sender_registration_preview").load(sender_registration_form_preview_link, function() {
            });
        }
    }
    );

    $(".preview_sender_registration_form").bind("click", function() {
        $(".sender_registration_preview").dialog("open");
    });

});