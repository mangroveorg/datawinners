function resize_iframe(event) {
    if ($("#container_content").height() < event.data + 150) {
        $("#container_content").height(event.data + 150);
    }
    $("#help_iframe").height(event.data);
}

$(document).ready(function(){
    $("#need_help_button").one( "click",function() {
        DW.help_url = DW.help_url.replace('/en/', '/');
        var url_language = DW.help_url.match("www.datawinners.com/(.*)/find-answers-app");
        if (url_language) {
            url_slug = DW.help_url.match("find-answers-app/(.*)/\\?template=help");
            if (url_slug) {
                DW.help_url = DW.help_url.replace(url_slug[1], url_slug[1] + '-' + url_language[1]);
            }
        }

        $.ajax({
            async: false,
            url: DW.help_url,
            data: {},
            global: false,
            error: function(r){
                $('.spinner_help').remove();
                $('#help_iframe').remove();
                $("#help_unavailable").removeClass("none");
            },
            complete: function(xhr, statusText){
                if (xhr.status != 200){
                    $('#help_iframe').addClass("none");
                    $("#help_unavailable").removeClass("none");
                }
            },
            beforeSend: function() {
                $("#help_iframe").attr("src", "");
                $('#help_iframe').addClass("none");
                $('#help_iframe').hide();
                $('.spinner_help').show();
                $("#div_iframe").css("visibility", "visible");
            },
            success: function(){
                $("#help_iframe").attr("src", DW.help_url);
                $("#help_iframe").on("load",function(){
                    $('.spinner_help').hide();
                    $(this).removeClass("none");
                    $(this).addClass("block");
                    $("#need_help_button").addClass("none");
                    $('#need_help_active_button').removeClass("none");
                });
            }
        });

        return false;
    });
    $("#need_help_button").on( "click",function() {
                    $("#div_iframe").css("visibility", "visible");
                    $('#help_iframe').removeClass("none");
                    $("#help_iframe").addClass("block");
                    $("#need_help_button").addClass("none");
                    $('#need_help_active_button').removeClass("none");
        return false;
    });

    $("#help_iframe").load(function(){
        if (window.addEventListener) {
            window.addEventListener("message", resize_iframe, false);
        }else if (window.attachEvent) {
            window.attachEvent("onmessage", resize_iframe);
        }
    });

    $(".close_help_button, #need_help_active_button").click(function() {
        $("#div_iframe").css("visibility", "hidden");
        $("#need_help_active_button").addClass("none");
        $('#need_help_button').removeClass("none");
        return false;
    });


});
