$(document).ready(function(){

    $($('input[name="frequency_enabled"]')).change(function(){
        if (this.value == "True") {
           $('#id_frequency_period').attr('disabled', false);
        }
        else{
            $('#id_frequency_period').attr('disabled', true);
        }
    });

    $($('input[name="activity_report"]')).change(function(){
        if (this.value == "no") {
           $('#id_category').attr('disabled', false);
           $('#id_entity_type').attr('disabled', false);
        }
        else{
            $('#id_category').attr('disabled', true);
            $('#id_entity_type').attr('disabled', true);
        }
    });

});
