$(document).ready(function() {
    $('#popbox').dialog({
        autoOpen: false,
        modal: true,
        width: 640
    });

    function showDialog(src, title) {
        $('#popbox img').attr('src', src);
        $('#popbox').dialog({
            title: title
        });
        $('#popbox').dialog('open');
    }

    $('.popbox').click(function(){
        showDialog($(this).attr("href"), $(this).attr('title'));
        return false;
    });
});
