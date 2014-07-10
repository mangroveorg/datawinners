$.Topic("formRenderComplete").subscribe( function(){
    $(".ajax-loader").addClass("none");
    $("#validate-form").removeClass('disabled-state').removeClass("disabled");
});