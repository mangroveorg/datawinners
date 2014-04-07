$(document).ready(function () {
    $('.chosen_entity_type').click(function () {
        var chosen_entity_type = $(this).text();
        var url = default_url+'entity/'+chosen_entity_type;
        window.location = url;
    });
});