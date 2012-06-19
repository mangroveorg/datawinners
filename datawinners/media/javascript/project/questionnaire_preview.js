$(document).ready(function() {
    $(".questionnaire_preview").dialog({
                title: $(".questionnaire_preview").attr("src_data") || gettext("Questionnaire Preview"),
                modal: true,
                autoOpen: false,
                height: 700,
                width: 800,
                closeText: 'hide',
                zIndex: 1300,
                open: function() {
                    // Here I load the content. This is the content of your link.
                    $(".questionnaire_preview").load(quessionarie_preview_link, function() {});
                }
            }
    );
    $(".preview").bind("click", function() {
        $(".questionnaire_preview").dialog("open");
        return false;
    });
});
