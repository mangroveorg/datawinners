$(document).ready(function() {
    $(".help_accordion .show_link").click(function() {
        $(this).parent().find(".details").show();
        $(this).hide();
    });

    $(".help_accordion .hide_link").click(function() {
        $(this).parent().hide();
        $(this).parent().parent().find(".show_link").show();
    });

    $("#edit-disclaimer").dialog({
        title: gettext("Shared Registration Form"),
        modal: true,
        autoOpen: true,
        width: 600,
        height: 150,
        position: ['center', 120]
    });

    $("#close-disclaimer").click(function() {
        $("#edit-disclaimer").dialog("close");
    });
})