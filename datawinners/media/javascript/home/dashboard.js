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
    },
    toggleAjaxLoader:function(htmlElement, should_show){
        if(should_show){
            htmlElement.removeClass("none");
        }else{
            htmlElement.addClass("none");
        }
    }

};

$(document).ready(function() {
    var project=new DW.dashboard_project();
    project.create_submission_template('submissionTemplate');
    $('.project_id').each(function(){
        project.showSubmissionBreakup($(this).html());
    });

});
