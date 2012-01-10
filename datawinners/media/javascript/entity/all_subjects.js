$(document).ready(function() {
    $("#all_subjects" ).accordion({
        header: '.list_header',
        autoHeight: false,
        collapsible: true,
        active:100
    });
    var entity_type = "waterpoint";
    $(".export-entity-link").bind("click", function(){
        var entity_type = $(this).attr("id").substr(7);
        $("#type_to_export").val(entity_type);
        $("#checked_subjects").html('');
        var checkboxes = $("#"+entity_type+"-table :checkbox:checked");

        checkboxes.each(function(){
            var element = document.createElement("input");
            element.name = $(this).attr("name");
            element.value = $(this).val();
            element.type = 'hidden';
            $("#checked_subjects").append(element);
        });
        $('#subject-export-form').trigger('submit');
    });
});