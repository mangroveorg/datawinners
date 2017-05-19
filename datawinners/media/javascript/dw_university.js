function resize_iframe(event) {
    if ($("#container_content").height() < event.data + 150) {
        $("#container_content").height(event.data + 150);
    }
    $("#help_iframe").height(event.data);
}

$(document).ready(function(){
    $("#need_help_button").one( "click",function() {
        $.ajax({
            url: DW.help_url,
            data: {},
            global: false,
            error: function(r){
                $('#help_iframe').addClass("none");
                $("#help_unavailable").removeClass("none");
            },
            complete: function(xhr, statusText){
                if (xhr.status == 200) {
                    $('.spinner_help').hide();
                    $("#help_iframe").attr("src", DW.help_url);
                    $('#help_iframe').removeClass("none");
                    $("#help_iframe").addClass("block");
                    $("#need_help_button").addClass("none");
                    $('#need_help_active_button').removeClass("none");
                } else {
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
