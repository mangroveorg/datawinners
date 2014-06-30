$(document).ready(function() {
    $('#learn_more').click(function(e){
        e.preventDefault();
        $('html,body').animate({scrollTop: $('a[name="a3"]').offset().top},'slow');
    });
    for(i in country){
        if(country.hasOwnProperty(i)){
            $("#country_select").append('<option value="'+i+'">'+i+'</option>');
        }
    }


    $("#country_select").change(function(){
        var html = '';
        $.each(country[$(this).val()], function(i,val){
            html += '<li>'+val+'</li>';
        });
        $("#networks_list").html(html);
    });
});