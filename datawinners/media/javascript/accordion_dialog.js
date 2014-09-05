DW.AccordionDialog = function(options){
        var dialogElement = $(options.dialogElementSelector);
        var dialog = dialogElement.dialog({
                autoOpen: false,
                width: 940,
                modal: true,
                position:"top",
                title: gettext(options.title) || gettext("dialog title"),
                zIndex: 1100,
                open: function(){
                    $(".learn_more_accordion").accordion({collapsible: true,active: false});
                },
                close: function(){
                    $(".learn_more_accordion").accordion( "destroy" );
                }
        });
        dialogElement.on('click', '#close_accordion_link', function(){
            dialog.dialog('close');
        });
};