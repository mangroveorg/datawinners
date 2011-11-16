DW.set_deadline_example = function() {
    var deadline_example = "";
    var frequency = $('#id_frequency_period').val();
    var deadline_type_value = $('#id_deadline_type:not(:disabled)').val();

    if (frequency == 'week') {
        // Monday of the following week
        // Monday of the week
        var selected_weekday_text = $('#id_deadline_week option:selected').text();
        if (deadline_type_value == 'Following') {
            deadline_example = interpolate(gettext("%(day)s of the week following the reporting week"), { day : selected_weekday_text}, true);
        } else {
            deadline_example = interpolate(gettext("%(day)s of the reporting week"), { day : selected_weekday_text }, true);
        }
    } else if (frequency == 'month') {
        // 5th day of October for September report
        // 5th day of October for October report
        var selected_month_day_text = $('#id_deadline_month option:selected').text();
        if (deadline_type_value == 'Following') {
            deadline_example = interpolate(gettext("%(day)s of October for September report"), { day : selected_month_day_text }, true);
        } else {
            deadline_example = interpolate(gettext("%(day)s of October for October report"), { day : selected_month_day_text }, true);
        }
    }
    $('#deadline_example').text(deadline_example);
};

function show_element(element, should_show) {
    if (should_show == 'True') {
        $(element).show();
    } else {
        $(element).hide();
    }
}

function enable_timeperiod() {
    if ($('#id_frequency_period').val() == "week") {
        show_element($('#week_block'), "True");
        show_element($('#month_block'), "False");
        $('#week_block :input').attr('disabled', false);
        $('#month_block :input').attr('disabled', true);
    } else if ($('#id_frequency_period').val() == "month") {
        $('#week_block :input').attr('disabled', true);
        $('#month_block :input').attr('disabled', false);
        show_element($('#week_block'), "False");
        show_element($('#month_block'), "True");
    }
}

function toggle_has_deadline() {
    if ($('input[name="has_deadline"]:checked').val() == "True") {
        show_element($('#time_period'), "True");
        show_element($('#deadline_example_block'), "True");
        $('#time_period :input').attr('disabled', false);
        enable_timeperiod();
        DW.set_deadline_example();
    } else {
        $('#time_period :input').attr('disabled', true);
        show_element($('#time_period'), "False");
        show_element($('#deadline_example_block'), "False");
    }
}

function toggle_frequency_period() {
    if ($('input[name="frequency_enabled"]:checked').val() == "True") {
        $('#id_frequency_period').attr('disabled', false);
    } else {
        $('#id_frequency_period').attr('disabled', true);
        $('input[name="has_deadline"]').attr('disabled', true);
    }
    toggle_has_deadline();
}

function deadline_init() {
    show_element($('#deadline_block'), $('input[name="frequency_enabled"]:checked').val());
    toggle_frequency_period();
}

function toggle_deadline_block() {
    show_element($('#deadline_block'), $('input[name="frequency_enabled"]:checked').val());
    if ($('input[name="frequency_enabled"]:checked').val() == "True") {
        $('input[name="has_deadline"]').attr('disabled', false);
    } else {
        $('input[name="has_deadline"]').attr('disabled', true);
    }
}

$(document).ready(function() {
    deadline_init();
    $($('input[name="frequency_enabled"]')).change(function() {
        toggle_deadline_block();
        toggle_frequency_period();
    });

    $($('input[name="has_deadline"]')).change(function() {
        toggle_has_deadline();
    });

    $('#id_frequency_period').change(function() {
        enable_timeperiod();
    });

    $('#id_deadline_week,#id_deadline_month,#id_deadline_type,#id_frequency_period').change(function() {
        DW.set_deadline_example();
    });

});

