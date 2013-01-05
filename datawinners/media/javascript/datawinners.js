DW.loading = function() {
    $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px', zIndex:1000000}});
}
$(document).ajaxStop($.unblockUI);
