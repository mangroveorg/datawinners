$(document).ready(function () {
    $('#all_subjects .subject-container').hide();

    $('#all_subjects .list_header').click(function () {
        $(this).toggleClass('highlight').siblings('.list_header').removeClass('highlight');
        $('#all_subjects .subject-container:visible').not($(this).next()).hide();
        $(this).next().slideToggle('fast').scrollTop(0);
    });

    $(".checkall-subjects").bind("click", function(){
        var type = $(this).attr("id").substr(9);

        var checked = $(this).attr("checked") == "checked";

        $($.sprintf("#%s-table tr td:first-child input:checkbox", type)).attr("checked", checked);
    });

    $(".subject-container table tbody tr td:first-child input:checkbox").bind("click", function(){
        if ($(this).attr("checked") != "checked") {
            var table = $(this).parent().parent().parent().parent();
            $("thead tr th input.checkall-subjects", table).attr("checked", false);
        }
    })
});