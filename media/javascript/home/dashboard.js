$(document).ready(function() {
    $( "#how_to" ).accordion({ collapsible: true, active: 0 });
    $( "#projects" ).accordion({ header: '.project_header', autoHeight: false, collapsible: true,active:100 });

    project_ids = [];
    $('.project_id').each(function(){
        
        var id = $(this).html();
        $.get('/submission/breakup/'+id+'/', function(data){
            var success_breakup = $.parseJSON(data);
            $('#submission_success_breakup_'+id).html(success_breakup[0]+gettext(" successful | ")+success_breakup[1]+gettext(" errors"));
        });
    });

});
