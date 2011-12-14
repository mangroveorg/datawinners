DW.dashboard_project=function(project_id){
    this.project_id=project_id;


};

DW.dashboard_project.prototype={
    getSubmissionDetails:function(){
        $.get('/submission/details/'+ this.project_id +'/', this._get_submission_data);
    },
    create_submission_template:function(submission_template_id){
        var markup = "<tr><td>${created}</td><td>${reporter}</td><td>${message}</td></tr>";
        $.template( submission_template_id, markup );

    },

    _parse_submission_data:function(data){
            var submissions = $.parseJSON(data);
            if (submissions.length<=0){
                return gettext("No submissions present for this project");
            }
            return $.tmpl("submissionTemplate", submissions);
    }


};

$(document).ready(function() {
    $( "#how_to" ).accordion({
        collapsible: true,
        active: 0
    });

    var project=new DW.dashboard_project();
    project.create_submission_template('submissionTemplate')
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

    var project_ids = [];
    $('.project_id').each(function(){

        var id = $(this).html();
        $.get('/submission/breakup/'+id+'/', function(data){
            var success_breakup = $.parseJSON(data);
            $('#submission_success_breakup_'+id).html(success_breakup[0]+gettext(" successful | ")+success_breakup[1]+gettext(" errors"));
        });
    });

});
