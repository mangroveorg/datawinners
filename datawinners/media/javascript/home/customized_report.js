$(document).ready(function(){
    var nb = 0;
    var num = 0;

    function anim(){
        $(document).everyTime(5000, 'anim', function(){
            var num = $(".pagin ul li a").index($(" .pagin ul li a.on"));
            var before = num;
            if (num < nb-1) {
                num ++;
            }
            else
                num = 0;
            jump_to(num);
        });
    }

    function jump_to(num){
        var width = "450";
        var nb = 5;
        var before = $(".pagin ul li a").index($(".pagin ul li a.on"));
        if (before == -1)
            return false;
            $('.pagin ul li a').removeClass('on');
            
            var distance = Math.abs(num - before);
            if (distance == 4){
                distance = 1;
            }
            if (((before - num == 4) || (before < num )) && (num - before != 4)){
                var direction = "+";
                var animation_params = {left:"-=" + (distance * width)};
            } else{
                var direction = "-";
                var animation_params = {left:"+=" + (distance * width)};
            }

            $("#anim_title").html($(".anim ul li").eq(num).html());
            var i = 1;
            var index = before;
            while(i <= distance) {
                if (direction == "+"){
                    index =  (before + i) % nb;
                } else {
                    index =  (before - i + nb) % nb;
                }
                $('.anim img').eq(index).css("display", "inline").css("left", direction + ( width * i) + "px").addClass("animate");
                i++;
            }

            $('.anim img').eq(before).addClass("animate");

            $("#anim1 a").unbind();
        
            $('.animate').delay(100).animate(animation_params, 2000, 'linear', function() {
                $('.anim img').eq(num).css("left", "0px");
                $('.anim img').eq(before).css("display", "none");
                $('.anim img').eq(before).css("left", "0px");
                $(".animate").removeClass("animate");
                $('.pagin ul li a').eq(num).addClass('on');
                $(document).delay(100);
                bind_navigation();
            });

    }
    
    $(".right_content .block_1").bind("click", function(){
        var num = $(".pagin ul li a").index($(" .pagin ul li a.on"));
            var before = num;
            if (num < nb-1) {
                num ++;
            }
            else
                num = 0;
            jump_to(num);
    });

    if($("#anim1").length){

        $('.anim img').eq(0).show();
        while($('.anim img').eq(nb).attr('alt')=='photo') {
            $('.pagin ul').append('<li><a href="javascript:void(0);" rel="'+nb+'" ><img src="/media/images/puceanim.png" alt="" width="16" height="32" /><br /></a></li');
            nb++;
        }

        $('.pagin ul li a').eq(0).addClass('on');


        $('.pagin ul li a, #anim1 .navigation, #anim1 .anim > div > img').live('mouseover', function(){
            $(document).stopTime('anim');
        });

        $('#anim1').bind('mouseenter', function(){
            //$("span.prev").animate({left:'+=26px'}, 500, 'linear');
            //$("span.next").animate({right:'+=26px'}, 500, 'linear');

        });

        $('#anim1').live('mouseleave', function(){
            //$("span.prev").animate({left:'-=26px'}, 500, 'linear');
            //$("span.next").animate({right:'-=26px'}, 500, 'linear');
        });

        $('.anim img').live('click', function(){
            $(document).stopTime('anim');
            var num = $(".pagin ul li a").index($(" .pagin ul li a.on"));
            var src = $(".anim img").eq(num).attr("src").replace("-title.png",".jpg");
            $("#popbox img").attr("src", src);
            $("#popbox").dialog("open");
        });


        $('.pagin ul li a, #anim1 .navigation, #anim1 .anim > div > img').live('mouseout', function(){
            anim();
        });

        function bind_navigation(){
            $('.pagin ul li a').live('click', function(){
                var num = $(this).attr('rel');
                jump_to(num);
            });

            $('#anim1 .navigation').bind('click', function(){
                var num = $(".pagin ul li a").index($(" .pagin ul li a.on"));
                num += ($(this).attr('id') == "slide_prev") ? -1: 1;
                num = (num + nb) % nb;
                jump_to(num);
            });
        }
        anim();
        bind_navigation();
    }

    $('#popbox').dialog({
        autoOpen: false,
        modal: true,
        width: 1045,
        height: "auto",
        position: ["center", "top"],
        close: function(){
            anim();
        },
        open: function(){
            var num = $(".pagin ul li a").index($(" .pagin ul li a.on"));
            var title = $(".anim ul li").eq(num).html();
            $("#popbox").dialog("option", "title", title);
        }
    });
   
});