$(function () {
    $('.download_link').click(function(){
        $('#download_form').attr('action', '/xlsform/download/').submit();
    });
});
