$(document).on("postFormLoadAction", function (evt) {
    $(".ajax-loader").hide();
    if (isQuotaReached != "True") {
        $("#validate-form").removeClass("disabled-state").removeClass("disabled");
    }
});
