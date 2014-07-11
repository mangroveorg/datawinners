$(function(){
    $(document).on("postFormLoadAction","form",function(){
        $(".ajax-loader").hide();
        $("#validate-form").removeClass("disabled-state").removeClass("disabled");
    });
});
