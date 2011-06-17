$(document).ready(function() {
  $('.dataTables_scrollHead select').customStyle();
  $("#dateRangePicker").daterangepicker( {
    presetRanges: [
    {text: 'Current month', dateStart: function(){ return Date.parse('today').moveToFirstDayOfMonth();  }, dateEnd: 'today' },
    {text: 'Last Month', dateStart: 'last month', dateEnd: 'today' },
    {text: 'Year to date', dateStart: function(){ var x= Date.parse('today'); x.setMonth(0); x.setDate(1); return x; }, dateEnd: 'today' }
    ],
    presets: {dateRange: 'Date Range'},
    earliestDate:'1/1/2011', latestDate:'21/12/2012', dateFormat:'dd-mm-yy', rangeSplitter:'/',
    onClose:function(){submit_data()}
  });
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
   function submit_data(){
       var aggregation_selectBox_Array = $(".aggregation_type"), aggregationArray = new Array();
         aggregation_selectBox_Array.each(function(){
         aggregationArray.push($(this).val())
        });
        var time_range = $("#dateRangePicker").val().split("/");
        if (time_range[0]!="Click to select a date range" && Date.parse(time_range[0]) == null){
            $("#dateErrorDiv").html('<label class=error>'+"Enter a correct date. No filtering applied"+'</label>')
            hide_message();
            time_range[0]="";
            time_range[1]="";
        }
        var start_time = time_range[0] || "";
        var end_time = time_range[1] || start_time;
        $.ajax({
          type: 'POST',
          url: window.location.pathname,
          data: {'aggregation-types':JSON.stringify(aggregationArray), 'start_time':start_time, 'end_time': end_time},
          success:function(response) {
                       var response_data = JSON.parse(response);
                       dataBinding(response_data, true, false);

         }});
   }
    $(".aggregation_type").live("change", function(){
        submit_data();

  });
    function hide_message() {
        $('#dateErrorDiv label').delay(5000).fadeOut();
    }

} );