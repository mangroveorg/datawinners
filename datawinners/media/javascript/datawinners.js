DW.loading = function() {
    $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px', zIndex:1000000}});
}
$(document).ajaxStop($.unblockUI);



DW.formatToLongDate = function(date_as_str){
    date_as_str.substring(1, 4);
    var month_name_map = {0:gettext('January') ,
                      1: gettext('February') ,
                      2: gettext('March') ,
                      3: gettext('April') ,
                      4: gettext('May') ,
                      5: gettext('June') ,
                      6: gettext('July') ,
                      7: gettext('August') ,
                      8: gettext('September'),
                      9: gettext('October') ,
                      10:gettext('November') ,
                      11:gettext('December') };
    return date_as_str.substring(8, 10) + ' ' + month_name_map[parseInt(date_as_str.substring(5, 7))-1] + ' ' + date_as_str.substring(0, 4);
}