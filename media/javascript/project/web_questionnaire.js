//this file is added to overlap tooltip on textbox in ie7
$(document).ready(function() {

    $(".help_icon").mouseover(function(){
        $(".answer span label").hide();
        $(".answer span").removeAttr("style");
    });

    $(".help_icon").mouseout(function(){
        $(".answer span label").show();
        $(".answer span").css({
            'position':'relative',
            'float':'left',
            'top':3
        });
    });

});