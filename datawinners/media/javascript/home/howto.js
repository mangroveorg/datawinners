$(document).ready(function() {
    var menu_number = $("#how_menu .title [rel]").length;
    
    var active = null;

    function moveActive(n) {
        $('#how_active').animate({left: (180 * (parseInt(n, 10) - 1)) + 'px'}, 500, 'swing');
    }

    function hideContent(n) {
        var myDiv = $('#step' + n);
        myDiv.hide();
        myDiv.removeClass('active');
    }

    function showContent(n) {
        var myDiv = $('#step' + n);
        myDiv.fadeIn();
        myDiv.addClass('active');
        if(n == menu_number) {
            $('#how_next').hide();
        } else {
            $('#how_next').show();
        }
        if(n == 1) {
            $('#how_prev').hide();
        } else {
            $('#how_prev').show();
        }
    }

    function swapContent(n) {
        hideContent(active);
        moveActive(n);
        showContent(n);
        active = parseInt(n, 10);
        updateNavLinks(n);
    }

    function updateNavLinks(n){
        $("#how_next a").html(gettext("Next:") +" "+ $("#how_menu a[rel=" + (active + 1) + "] strong").html() + " &gt;&gt;");
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
        var n = (active < menu_number) ? active + 1 : menu_number;
        swapContent(n);
    });

    $('#backToSummaryReport').click(function(){
       swapContent(1);
    });
    
    swapContent(1);
});
