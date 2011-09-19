$(document).ready(function() {
    $('.plus a').click(function() {
        popup = $('#'+$(this).attr('rel'));
        if(popup != undefined) {
            popup.fadeIn();
        }
    });

    $('.close a').click(function(){
        $(this).parent().parent().fadeOut();
    });
});
