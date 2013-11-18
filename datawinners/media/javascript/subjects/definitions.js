DW = DW || {};

DW.SubjectSMSPreviewPage = function () {
    var sms_preview_form = $("#preview_form");
    sms_preview_form.html($("#subject_registration_form").clone().html());
    sms_preview_form.find('input[type="submit"]').remove();
    var sms_form_heading = $("#sms_form_heading");
    sms_preview_form.find('.generate_id_check').remove();
    sms_preview_form.find('input,select').each(function (index, element) {
        var query_element_object = $(element);
        query_element_object.attr("disabled", true);
    });
    sms_preview_form.find("input").val('');
    var input_elements = $("#preview_form select, #preview_form input[type=checkbox]").not("#generate_id");
    input_elements.parents(".answer").before('<input type="text" disabled="disabled">');
    input_elements.each(function (index, element) {
        var query_element_object = $(element);
        var options;
        if (query_element_object.is('select')) {
            query_element_object.attr("hidden", "hidden");
            query_element_object.hide();
            var options_html = "<ul class='multiple_select' style='clear:both'>";
            options = query_element_object.find("option");
            for (var i = 0; i < options.length; i++) {
                var option = $(options[i]);
                if (option.val() != "") {
                    options_html += "<li><span class='bullet'>" + option.val() + ".</span><span>" + option.text() + "</span></li>"
                }
            }
            options_html += "</ul>";

        } else {
            query_element_object.replaceWith("<li><span class='bullet'>" + query_element_object.val() + ". &nbsp;&nbsp; </span></li>");
        }
        query_element_object.after(options_html);
    });

    this.enable = function () {
        $("#message_box").remove();
        $(".errorlist").remove();
        $("#sms_preview").show();
        sms_form_heading.show();
    };

    this.disable = function () {
        $("#sms_preview").hide();
        sms_form_heading.hide();
    };
};

DW.SubjectViewStyleButtons = function (sms_view_page, registration_form) {
    var sms_preview_button = $("#sms_preview_btn");
    var web_preview_button = $("#web_preview_btn");

    sms_preview_button.bind('click', function (eventObject) {
        web_preview_button.removeClass("active");
        sms_preview_button.addClass("active");
        registration_form.disable();
        sms_view_page.enable();
    });

    web_preview_button.bind('click', function (eventObject) {
        web_preview_button.addClass("active");
        sms_preview_button.removeClass("active");
        registration_form.enable();
        sms_view_page.disable();
    });

    if (web_view == "True") {
        web_preview_button.click();
    } else {
        sms_preview_button.click();
    }
};


DW.SubjectPrintModalPage = function () {
    var dialog_html = $($("#sms_preview").clone()).attr("id", "dialog_sms_preview");
    dialog_html.find(".printBtn").show();
    dialog_html.find(".errorlist").hide();
    dialog_html.find("input").val('');
    dialog_html.dialog({
        title: gettext("Subject Registration Preview"),
        modal: true,
        autoOpen: false,
        height: 700,
        width: 800,
        closeText: 'hide',
        open: function () {
            $("body > div").addClass("none_for_print");
        },
        close: function () {
            $("body > div").removeClass("none_for_print");
        }
    });

    this.display = function () {
        dialog_html.dialog("open");
    };

    dialog_html.find(".printBtn").on("click", function (eventObject) {
        window.print();
        eventObject.preventDefault();
    });
};


DW.SubjectRegistrationForm = function (form_selector) {
    var registration_form = $("#subject_registration_form");
    var subject_unique_id = new DW.UniqueIdField(form_selector);

    var web_form_heading = $("#web_form_heading");
    this.enable = function () {
        registration_form.show();
        subject_unique_id.enable();
        web_form_heading.show();
    };

    this.disable = function () {
        var visible_elements = $('input:visible:not([type="submit"]), select:visible', form_selector);
        visible_elements.attr("value", "");
        //This is explicitly called here as otherwise the watermark api does not kick in, that api should have
        //listened to the change event but currently its attached to blur
        visible_elements.blur();
        subject_unique_id.disable();
        //This has to be called last as the above statements will fail if we hide the form first.
        registration_form.hide();
        web_form_heading.hide();
    };
};


