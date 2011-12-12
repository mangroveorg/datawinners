$(document).ready(function() {
    $( "#how_to" ).accordion({
        collapsible: true,
        active: 0
    });

    var markup = "<tr><td>${created}</td><td>${reporter}</td><td>${message}</td></tr>";
    $.template( "submissionTemplate", markup );

    var no_submission_message = "No submissions present for this project";

    $( "#projects" ).accordion({
        header: '.project_header',
        autoHeight: false,
        collapsible: true,
        active:100,
        change: function(event, ui){
            var id = $(ui.newContent).find('.project_id').html();
            if(id == null){
                return false;
            }
            $.get('/submission/details/'+ id +'/', function(data) {
                var submissions = $.parseJSON(data);
                var submission_content = gettext("No submissions present for this project");
                if (submissions.length > 0) {
                    submission_content = $.tmpl("submissionTemplate", submissions);
                }
                $(ui.newContent).find('.submission_list').html(submission_content);
            });
        }
    });

    project_ids = [];
    $('.project_id').each(function(){
        
        var id = $(this).html();
        $.get('/submission/breakup/'+id+'/', function(data){
            var success_breakup = $.parseJSON(data);
            $('#submission_success_breakup_'+id).html(success_breakup[0]+gettext(" successful | ")+success_breakup[1]+gettext(" errors"));
        });
    });

});
