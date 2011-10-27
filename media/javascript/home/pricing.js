$(document).ready(function() {
    $('#learn_more').click(function(e){
        e.preventDefault();
        $('html,body').animate({scrollTop: $('a[name="a3"]').offset().top},'slow');
    });
});