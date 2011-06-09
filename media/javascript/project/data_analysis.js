$(document).ready(function() {
	var oTable = $('#data_analysis').dataTable({
		"sPaginationType": "full_numbers",
        "sScrollX": "100%",
        "sScrollXInner": "110%",
        "bScrollCollapse": true

	});
    $(".aggregation_type").live("change", function(){
        var aggregation_selectBox_Array = $(".aggregation_type"), aggregationArray = new Array();
         aggregation_selectBox_Array.each(function(index){
         aggregationArray.push($(this).val())
        });
        $.ajax({
          type: 'POST',
          url: window.location.pathname,
          data: {'aggregation-types':JSON.stringify(aggregationArray)},
          success:function(response) {
                    $('#data_body').replaceWith(response);
        }});

    })
} );