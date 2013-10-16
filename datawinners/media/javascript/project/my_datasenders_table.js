$(function(){
    var checkbox_column_index = 0;
    new DW.DataSenderTable({
                                url: datasender_ajax_url,
                                non_sortable_columns: [checkbox_column_index, $('#datasender_table th.devices').index('#datasender_table th')]
                            });

});