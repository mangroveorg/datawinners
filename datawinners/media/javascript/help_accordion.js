$(document).ready(function() {
    $("#container_content").delegate('.show_link', 'click', function() {
        $(this).parent().find(".details").show().end().end().hide();
    });

    $("#container_content").delegate('.hide_link', 'click', function() {
        $(this).parent().hide().parents('.help_accordion').find(".show_link").show();
    });
})