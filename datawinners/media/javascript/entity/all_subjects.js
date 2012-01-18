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
    
    $(".import-subject").each(function(){
        var form_code = $(this).attr("id").substr(7);
        
        var uploader = new qq.FileUploader({
            // pass the dom node (ex. $(selector)[0] for jQuery users)
            element: $(this)[0],
            // path to server-side upload script
            action: "/entity/subjects/",
            params: {form_code: form_code},
            template:'<div  style="display:none;" class="qq-upload-drop-area"><span>' + gettext("Drop files here to upload") + '</span></div>' +
                '<a href="javascript:void(0);" class="qq-upload-button" style="width: 50px;display: inline-block;background: none;padding: 0;border: none; orverflow: none;">' + gettext("Import") + '<br/></a>' +
                '<ul class="qq-upload-list" style="display: none;"></ul>' ,
            onComplete: function(id, fileName, responseJSON) {
                $('#message').remove();
                $('#error_tbody').html('');
                $("#error_table").hide();
                $("#"+form_code+"_table").html('');
                $.each(responseJSON.all_data, function(index, entity_data) {
                    if (entity_data.code == form_code){
                        $.each(entity_data.data, function(key, element){
                            var datas = element.cols.join("</td><td>");
                            datas = '<input type="checkbox" value="'+element.short_code+'" name="checked"/></td><td>'+datas;
                            $("#"+form_code+"_table").append("<tr><td>"+datas+"</td></tr>");
                        });
                    }
                });
            }
        });
    })


    /* leave commented for next change
    $(".popup-import").dialog({
        autoOpen: false,
        modal: true,
        title: function(){
            var entity_type = $(this).attr("id").substr(22);
            return interpolate(gettext('Import a list of %(entity)s'), {entity:entity_type}, true);
        },
        zIndex:200,
        width: 1000
    });

    $(".import-subject").unbind().bind("click", function(){
        var entity_type = $(this).attr("id").substr(7);
        $("#popup-"+entity_type).dialog("open");
    });
    */
});