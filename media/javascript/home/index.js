$(document).ready(function() {
    $('.container_carousel a').click(function() {
        var popup = $('#'+$(this).attr('rel'));
        if(popup != undefined) {
            popup.fadeIn();
        }
    });

    $('.close a').click(function(){
        $(this).parent().parent().fadeOut();
    });
});
