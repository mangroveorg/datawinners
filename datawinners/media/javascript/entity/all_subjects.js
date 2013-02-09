$(document).ready(function() {
    $('#all_subjects .subject-container').hide();

    $('#all_subjects .list_header').click(function(){
        $(this).addClass('highlight').siblings('.list_header').removeClass('highlight')
        $('#all_subjects .subject-container:visible').not($(this).next()).hide();
        $(this).next().slideToggle('fast').scrollTop(0);
    })
    var entity_type = "waterpoint";
});