$(document).ready(function() {
    $(".questionnaire_preview").dialog({
                title: gettext("Questionnaire Preview"),
                modal: true,
                autoOpen: false,
                height: 700,
                width: 800,
                closeText: 'hide',
                open: function() {
                    // Here I load the content. This is the content of your link.
                    $(".questionnaire_preview").load(quessionarie_preview_link, function() {});
                }
            }
    );
    $(".preview").bind("click", function() {
        $(".questionnaire_preview").dialog("open");
    });
});
