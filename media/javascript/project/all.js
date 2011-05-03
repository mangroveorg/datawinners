$(document).ready(function(){

    $('.project-id-class').click(function(){
        var pid = $(this).id;
        $.get("/project/overview",pid);
    });
})

