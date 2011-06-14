$(document).ready(function() {
     $('.dataTables_scrollHead select').customStyle();
    
    $('#data_analysis').dataTable( {
        "bRetrieve" : true,
        "sPaginationType": "full_numbers",
        "sScrollX": "100%",
        "sScrollXInner": "110%",
        "bScrollCollapse": true,
		"aaData": initial_data



	} );
    var newDataTable;
    function dataBinding(data){
            newDataTable = {
            "bDestroy":true,
            "sPaginationType": "full_numbers",
            "sScrollX": "100%",
            "sScrollXInner": "110%",
            "bScrollCollapse": true,
            "aaData": data
        };
    }
    $(".aggregation_type").live("change", function(){
        var aggregation_selectBox_Array = $(".aggregation_type"), aggregationArray = new Array();
         aggregation_selectBox_Array.each(function(){
         aggregationArray.push($(this).val())
        });
        $.ajax({
          type: 'POST',
          url: window.location.pathname,
          data: {'aggregation-types':JSON.stringify(aggregationArray)},
          success:function(response) {
                       console.log("response data"+response)
                       var response_data = JSON.parse(response);
                       dataBinding(response_data);
                       $('#data_analysis').dataTable( newDataTable );

         }});
    });

} );