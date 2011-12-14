DW.dashboard_project=function(){
};

DW.dashboard_project.prototype={
    getSubmissionDetails:function(submission_response){
        var submissions = $.parseJSON(submission_response);
        if (submissions.length<=0){
            return gettext("No submissions present for this project");
        }
        return $.tmpl("submissionTemplate", submissions);
    },
    create_submission_template:function(submission_template_id){
        var markup = "<tr><td>${created}</td><td>${reporter}</td><td>${message}</td></tr>";
        $.template( submission_template_id, markup );

    },
    showSubmissionBreakup:function(project_id){
        $.get('/submission/breakup/'+project_id+'/', function(data){
            var success_breakup = $.parseJSON(data);
            $('#submission_success_breakup_'+project_id).html(success_breakup[0]+gettext(" successful | ")+success_breakup[1]+gettext(" errors"));
        });

    }

};

$(document).ready(function() {
    $( "#how_to" ).accordion({
        collapsible: true,
        active: 0
    });

    var project=new DW.dashboard_project();
    project.create_submission_template('submissionTemplate')

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
                $(ui.newContent).find('.submission_list').html(project.getSubmissionDetails(data));
            });
        }
    });

    $('.project_id').each(function(){
        project.showSubmissionBreakup($(this).html());
    });

});
