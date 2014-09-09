$(function(){

     isSmartPhoneUpgradeInfoFlagPresent === 'True' && new DW.Dialog({
            title: gettext("Use the New Version of Our Android App"),
            dialogDiv: "#smartphone_upgrade_section",
            autoOpen: true,
            width: 600
        }).init().initializeLinkBindings();

});