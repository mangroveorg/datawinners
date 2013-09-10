DW = DW || {};

DW.UniqueIdField = function (form_selector) {
    var generate_id = $("#generate_id", form_selector);
    var subject_unique_id = $(".subject_field", form_selector);

    this.enable = function () {
        if (subject_unique_id.val() == "") {
            this.disable();
        } else {
            generate_id.removeAttr('checked');
            subject_unique_id.attr("disabled", false);
        }
    };

    this.disable = function () {
        generate_id.attr("checked", "checked");
        subject_unique_id.val("");
        subject_unique_id.attr("disabled", true);
    };

    generate_id.on('click', function () {
        subject_unique_id.attr("disabled", $(this).is(":checked"));
        if ($(this).is(":checked")) {
            subject_unique_id.val('');
        }
    });
};
