function initializeDialogWithAccordion(dialogSection, options){
        dialogSection.dialog({
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
        dialogSection.off('click', '#close_unique_id_learn_more_section', _closeDialogHandler);
        dialogSection.on('click', '#close_unique_id_learn_more_section', _closeDialogHandler);
}
function _closeDialogHandler(){
        $("#xls_learn_more_form").dialog('close');
}