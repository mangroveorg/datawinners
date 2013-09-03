DW = DW || {};

DW.SubjectSMSPreviewPage = function () {
    var sms_preview_form = $("#preview_form");
    sms_preview_form.html($("#subject_registration_form").clone().html());
    sms_preview_form.find('input[type="submit"]').remove();
    sms_preview_form.find('input').attr("value", '');
    var sms_form_heading = $("#sms_form_heading");

    sms_preview_form.find('input,select').each(function (index, element) {
        var query_element_object = $(element);
        query_element_object.attr("disabled", true);
        var options_html = "<ol class='multiple_select'>";
        var options = query_element_object.find("option");
        for (var i = 0; i < options.length; i++) {
            var option = $(options[i]);
            if (option.val() != "") {
                options_html += "<li><span class='bullet'>" + option.val() + ".</span><span>" + option.text() + "</span></li>"
            }
        }
        options_html += "</ol>";
        query_element_object.after(options_html);
    });

    this.enable = function () {
        $(".errorlist").remove();
        $("#sms_preview").attr("hidden", false);
        sms_form_heading.show();
    };
    this.disable = function () {
        $("#sms_preview").attr("hidden", true);
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
    dialog_html.find(".printBtn").attr("hidden", false);

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
    var generate_id = $("#generate_id", form_selector);
    var registration_form = $("#subject_registration_form");
    var web_form_heading = $("#web_form_heading");

    this.enable = function () {
        registration_form.attr("hidden", false);
        generate_id.attr("checked", "checked");
        web_form_heading.show();
    };

    this.disable = function () {
        var visible_elements = $('input:visible:not([type="submit"]), select:visible', form_selector);
        visible_elements.attr("value", "");
        //This is explicitly called here as otherwise the watermark api does not kick in, that api should have
        //listened to the change event but currently its attached to blur
        visible_elements.blur();
        generate_id.attr("checked", "checked");
        //This has to be called last as the above statements will fail if we hide the form first.
        registration_form.attr("hidden", true);
        web_form_heading.hide();
    };

    var subject_unique_id = $(".subject_field", form_selector);

    generate_id.on('click', function () {
        subject_unique_id.attr("disabled", $(this).is(":checked"));
        if ($(this).is(":checked")) {
            subject_unique_id.val('');
        }
    });

    subject_unique_id.attr("disabled", true);
};

