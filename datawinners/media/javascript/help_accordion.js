$(document).ready(function() {
    $("#help_accordion #show_link").click(function() {
        $("#help_details").show("slow");
        $(this).hide();
    });

    $("#help_accordion #hide_link").click(function() {
        $("#help_details").hide("slow");
        $("#show_link").show();
    });
})