$(document).ready(function() {

    function showDialog(src, title) {
        $('#popbox img').attr('src', src);
        $('#popbox').dialog({
            autoOpen: true,
            modal: true,
            width: 780,
            height: "auto",
            title: title,
            position: ["center", "top"],
            open: function(){
                $(".ui-dialog").css("top", $(window).scrollTop());
            },
            close: function(){
                $("#popbox").dialog("destroy");
            }
        });
    }

    $('.popbox').click(function(){
        showDialog($(this).attr("href"), $(this).attr('title'));
        return false;
    });
});
