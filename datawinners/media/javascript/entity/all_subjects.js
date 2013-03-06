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
});