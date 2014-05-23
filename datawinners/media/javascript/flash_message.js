function flash_message(flash_msg_section_selector, msg, status) {
    $('.flash-message').remove();

    $(flash_msg_section_selector).prepend('<div class="clear-left flash-message">' + gettext(msg) + (msg.match("[.]$") ? '' : '.') + '</div>')
    $('.flash-message').addClass((status === false) ? "message-box" : "success-message-box");

    $('#success_message').delay(4000).fadeOut(1000, function () {
        $('.flash-message').remove();
    });
}

