$(document).ready(function () {
    var hideEntityTypes = function(){
        $('.entity_types').toggle(entity_types.length != 1);
    };
    hideEntityTypes();
    $('.chosen_entity_type li').each(function(index, elem){
        $(elem).removeClass('inactive');
        $(elem).removeClass('active');
        if(elem.textContent.toLowerCase() == subject_type.toLowerCase())
            $(elem).addClass('active');
        else
            $(elem).addClass('inactive');
    });

    $('.chosen_entity_type li').click(function () {
        var chosen_entity_type = $(this).text().toLowerCase();
        var url = default_url+'entity/'+chosen_entity_type;
        window.location = url;
    });

});