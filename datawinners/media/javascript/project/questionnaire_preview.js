$(document).ready(function () {
    DW.questionnaire_preview = {
        init:function () {
            DW.questionnaire_preview.init_sms_questionnaire_preview();
            DW.questionnaire_preview.init_questionnaire_preview();
            DW.trackEvent('questionnaire', 'accessed-overview');
        },
        init_sms_questionnaire_preview:function () {
            DW.questionnaire_preview.init_dialog(".sms-questionnaire-preview", sms_questionnaire_preview_link);
            DW.questionnaire_preview.bind(".sms-questionnaire-preview", ".sms-preview");
        },
        init_questionnaire_preview:function () {
            DW.questionnaire_preview.init_dialog(".questionnaire_preview", questionnaire_preview_link);
            DW.questionnaire_preview.bind(".questionnaire_preview", ".preview");
        },
        init_dialog:function (dialog_element, questionnaire_preview_link) {
            var questionnaire_preview = $(dialog_element);
            questionnaire_preview.dialog({
                    title:questionnaire_preview.attr("src_data") || gettext("Questionnaire Preview"),
                    modal:true,
                    autoOpen:false,
                    height:700,
                    width:800,
                    closeText:'hide',
                    zIndex:1300,
                    open:function () {
                        // Here I load the content. This is the content of your link.
                        $("body > div").addClass("none_for_print");
                        questionnaire_preview.load(questionnaire_preview_link, function () {
                        });
                    },
                    close:function () {
                        $("body > div").removeClass("none_for_print");
                    }
                }
            );
        },
        bind:function (dialog_element, preview_link) {
            $("#container_content").delegate(preview_link, "click", function () {
                $(dialog_element).dialog("open");
                return false;
            });
        }
    };

    DW.questionnaire_preview.init();
});
