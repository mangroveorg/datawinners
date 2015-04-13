DW.flashMessage = function(msg, status){
    $('.flash-message').remove();

    $(".dataTables_wrapper").prepend('<div class="clear-left flash-message margin-left-right-null">' + gettext(msg) + (msg.match("[.]$") ? '' : '.') + '</div>');
    $('.flash-message').addClass((status === false) ? "message-box" : "success-message-box");
    window.scrollTo(0,0);
};

