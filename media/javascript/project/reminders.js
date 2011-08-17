$(document).ready(function(){
    $('.choice').change(function(){
        var is_reminder = $("input[@name='rdio']:checked").val();
        var project_id = $('#project_id').html();
        var url = '/project/reminderstatus/' + project_id+"/";
        $.post(url, {'is_reminder': is_reminder}, function(data){
//            console.log(data);
        });
    });
});