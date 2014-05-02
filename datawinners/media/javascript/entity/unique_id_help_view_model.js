
$(document).ready(function () {
   $(".learn_more_accordion > li > div").click(function(){
    if(false == $(this).next().is(':visible')) {
        $('.learn_more_accordion #learn_more_image').slideUp(300);
    }
    $(this).next().slideToggle(300);
});

$('.learn_more_accordion #learn_more_image').hide();
$('#ok').click(function(){
    $('.unique_id_learn_more_form').dialog('close');
});
});