$(document).ready(function() {
    var active = null;

    function moveActive(n) {
        $('#how_active').animate({left: (180 * (parseInt(n) - 1)) + 'px'}, 500, 'swing');
    }

    function hideContent(n) {
        var myDiv = $('#step' + n);
        myDiv.hide();
        myDiv.removeClass('active');
        active = null;
    }

    function showContent(n) {
        var myDiv = $('#step' + n);
        myDiv.fadeIn();
        myDiv.addClass('active');
        if(n == 4) {
            $('#how_next').hide();
        } else {
            $('#how_next').show();
        }
        if(n == 1) {
            $('#how_prev').hide();
        } else {
            $('#how_prev').show();
        }
        active = n;
    }

    function swapContent(n) {
        hideContent(active);
        moveActive(n);
        showContent(n);
    }

    $('#how_menu a').click(function(){
        var n = $(this).attr('rel');
        swapContent(n);
    });

    $('#how_prev').click(function(){
        var n = (active > 1) ? active - 1 : 1;
        swapContent(n);
    });

    $('#how_next').click(function(){
        var n = (active < 4) ? active + 1 : 4;
        swapContent(n);
    });

    swapContent(1);
});
