$(document).ready(function() {
    $(".help_accordion .show_link").click(function() {
        $(this).parent().find(".details").show();
        $(this).hide();
    });

    $(".help_accordion .hide_link").click(function() {
        $(this).parent().hide();
        $(this).parent().parent().find(".show_link").show();
    });
})