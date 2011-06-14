$(document).ready(function() {
     $('.dataTables_scrollHead select').customStyle();
    $("#dateRangePicker").daterangepicker( { presetRanges: [
    {text: 'Past 7 days', dateStart: 'last week', dateEnd: 'Today' },
    {text: 'Past 30 days', dateStart: 'last month', dateEnd: 'Today' },
    {text: 'Past year', dateStart: 'last year', dateEnd: 'Today'}],
    earliestDate:'1/1/2011', latestDate:'12/21/2012'
  }
);
    function dataBinding(data, destroy, retrive){
         $('#data_analysis').dataTable( {
             "bDestroy":destroy,
            "bRetrieve": retrive,
            "sPaginationType": "full_numbers",
            "sScrollX": "100%",
            "sScrollXInner": "110%",
            "bScrollCollapse": true,
            "aaData": data
        });
    }
    dataBinding(initial_data, false, true);
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
                       dataBinding(response_data, true, false);

         }});
    });

} );