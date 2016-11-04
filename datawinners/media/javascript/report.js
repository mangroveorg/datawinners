$(function(){
    $("#report_navigation a").click(function(){
        $("#report_navigation li.active").addClass("inactive");
        $("#report_navigation li.active").removeClass("active");
        $(this).parent().addClass("active");
        $("#report_container").load($(this).attr("id"));
    })
})