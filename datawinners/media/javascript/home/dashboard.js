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

function _trackConversion(){
    if(is_first_time_activation == 'True'){
        DW.trackEvent('account', 'activated', account_type, parseInt(account_cost));
    }
}

$(document).ready(function() {
    var project=new DW.dashboard_project();
    project.create_submission_template('submissionTemplate');
    $('.project_id').each(function(){
        project.showSubmissionBreakup($(this).html());
    });
    _trackConversion();

    $( ".close_help_element" ).click(function() {
        $("#welcome_area, #help_element").addClass("none");
        $("#help_message").removeClass("none");
        $("#container_content .container_24").addClass("position_relative");

        var data = {
        'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
        };

        $.ajax({
            type: "POST",
            url: '/dashboard/hide_help_element/',
            data: data
        });
    });

    $(".close_help_element").tooltip({
        position: "top right",
        relative: true,
        opacity: 0.8,
        events: {
            def: "mouseover,mouseout",
            input: "focus,blur",
            widget: "focus mouseover,blur mouseout",
            tooltip: "click,click"
        }

    }).dynamic({ bottom: { direction: 'down', bounce: true } });

    
    $( "#help_message_dialog_close" ).click(function() {
        $("#help_message").addClass("none");
        $("#container_content .container_24").removeClass("position_relative");
    });

    $("#video-lightbox").dialog({
        modal: true,
        autoOpen: false,
        height: 'auto',
        width: 'auto',
        closeText: 'hide',
        close: function(){
            $("#video-lightbox iframe").attr("src", "");
        }
    });

    $("a.open_video").bind("click", function(){
        $("#video-lightbox iframe").attr("src", $(this).attr("href"));
        $("#video-lightbox").dialog("option", "title", $(this).text());
        $("#video-lightbox").dialog("open");
        return false;
    });
});
