$(function() {
    var sms_preview = new DW.sms_instruction_and_preview();
    sms_preview.bind_preview_navigation_item();
    var web_preview = new DW.web_instruction_and_preview();
    web_preview.bind_preview_navigation_item();
    var web_preview = new DW.smart_phone_instruction_and_preview();
    web_preview.bind_preview_navigation_item();
});