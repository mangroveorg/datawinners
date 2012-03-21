$(document).ready(function() {
    $('#learn_more').click(function(e){
        e.preventDefault();
        $('html,body').animate({scrollTop: $('a[name="a3"]').offset().top},'slow');
    });
    for(i in country){
        $("#country_select").append('<option value="'+i+'">'+i+'</option>');
    }


    $("#country_select").change(function(){
        var html = '';
        for(i in country[$(this).val()]){
            html += '<li>'+country[$(this).val()][i]+'</li>';
        }
        $("#networks_list").html(html);
    });
});