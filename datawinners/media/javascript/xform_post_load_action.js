$(document).on("postFormLoadAction", function (evt) {
    $(".ajax-loader").hide();
    $("#validate-form").removeClass("disabled-state").removeClass("disabled");
});
