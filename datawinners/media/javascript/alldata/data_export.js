$(document).ready(function(){

    buildDateRangePicker($("#dateRangePicker"));
    buildDateRangePicker($("#dateRangePickerForEntity"));
    buildDateRangePicker($("#dateRangePickerForRegisterSubject"));

    setSubjectSelectionOptions();
    bindEntityTypeChange();

    $('#exportProjectBtn').click(function() {
        var questionnaire_code = $("#project_select").val();
        var time_range = getDateRange($("#dateRangePicker"));
        var download_link = '/api/get_for_form/'+questionnaire_code +
            (time_range[0] == null ? '': '/'+time_range[0]) +
            (time_range[1] == null ? '': '/'+time_range[1]);

        window.location.href = download_link;
    });

    $('#exportEntityBtn').click(function() {
        var subject_type = $("#subject_type_select").val();
        var subject_id = $("#subject_select").val();
        var time_range = getDateRange($("#dateRangePickerForEntity"));

        var download_link = '/api/get_for_subject/'+subject_type + '/' + subject_id +
            (time_range[0] == null ? '': '/'+time_range[0]) +
            (time_range[1] == null ? '': '/'+time_range[1]);

        window.location.href = download_link;
    });

    $('#exportRegisterSubjectBtn').click(function() {
        var subject_type = $("#register_subject_select").val();
        var time_range = getDateRange($("#dateRangePickerForRegisterSubject"));

        var download_link = '/alldata/registereddata/'+subject_type +
            (time_range[0] == null ? '': '/'+time_range[0]) +
            (time_range[1] == null ? '': '/'+time_range[1]);

        window.location.href = download_link;
    });

    function getDateRange(dateRangePicker) {

        var results=[null, null]
        var time_range = dateRangePicker.val().split("to");
        if(time_range.length == 2){
         var start_date = Date.parse(time_range[0]);
         var end_date = Date.parse(time_range[1]);

            if(start_date == null) return results;
            results[0] =time_range[0].trim();
            if(end_date == null) return results;
            results[1] =time_range[1].trim();
            return results;
        }
        return results;
    };

    function buildDateRangePicker(elem) {
        elem.daterangepicker({
            presetRanges:[],
            presets:{dateRange:gettext('Date Range')},
            dateFormat:'dd-mm-yy',
            rangeSplitter:gettext("to")
        });
    };

    function appendSubjectSelectionOptions(){
        var subject_type = $("#subject_type_select").val();

        $.ajax({
            type: 'GET',
            url: "/alldata/entities/" + subject_type,
            async:false,
            success:function(response) {
                var subject_type_list = $("#subject_select");
                subject_type_list.children().remove();
                for( index in response){
                    var subject_short_code = response[index];
                    subject_type_list.append("<option value='"+subject_short_code+"'>"+subject_short_code+"</option>")
                }
            }
        });
    }

    function bindEntityTypeChange() {
        $('#subject_type_select').change(setSubjectSelectionOptions);
    }

    function setSubjectSelectionOptions() {
        appendSubjectSelectionOptions();
        toggleOnSelectionChange();
    }

    function toggleOnSelectionChange() {
        var should_grey_out = $("#subject_select").children().length == 0;
        if(should_grey_out){
            $("#exportEntityBtn").attr('disabled', true);
            $("#subject_select").attr('disabled', true);
            $("#dateRangePickerForEntity").attr('disabled', true);
        }else{
            $("#exportEntityBtn").removeAttr("disabled");
            $("#subject_select").removeAttr("disabled");
            $("#dateRangePickerForEntity").removeAttr("disabled");
        }
    }

});