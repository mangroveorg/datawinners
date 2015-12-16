$(document).ready(function(){
    var progressbar = $( "#progressbar" ),
    progressLabel = $( ".progress-label" );
	var reindex_table = $("#reindex_table").DataTable({
		
        "ajax": {
            url: dataUrl,
            type: "GET",
            data:{
            	"reload": reload,
            	"full_reindex":full_reindex
            },
            dataSrc:function(d){
            	console.log(d);
                progressbar.progressbar( "value", Math.ceil(d.completed_submissions*100/d.total_submissions) );
                $('#start_time').html(d.reindex_start_time);
                $('#end_time').html(d.reindex_end_time);
                $('#total_submissions').html(d.total_submissions);
                $('#completed_submissions').html(d.completed_submissions);

            	if(d.in_progress){
                	setTimeout(refresh_data,3000);
            	}
            	return d.data;
            }
            
        },
        "columns":[
                   {"data":"db_name", "title":"Index name"},
                   {"data":"questionnaire_id","title":"Questionnaire Id"},
                   {"data":"name","title":"Questionnaire Name"},
                   {"data":"no_of_submissions", "title":"No of Submissions"},
                   {"data":"status","title":"Status","defaultContent":""},
                   {"data":"result","title":"Details","defaultContent":""},
                   {"data":"end_time","title":"End time","defaultContent":""},
                   {"data":"time_taken","title":"Time taken","defaultContent":""}
                   
                   ],
       "order": [[ 6, "desc" ]] 
	});
	
	var refresh_data = function(){
		console.log('refreshing...');
		reindex_table.ajax.reload();
	};


  progressbar.progressbar({
    value: false,
    change: function() {
      progressLabel.text( progressbar.progressbar( "value" ) + "%" );
    },
    complete: function() {
      progressLabel.text( "Complete!" );
    }
  });


})