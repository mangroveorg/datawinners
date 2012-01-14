DW.get_trial_number_info = function(){
    $('#mapping tbody').html('');
    $.post(window.location.href,{country:$('#id_country').val()},
            function(response){
                $('#trial_number_info').removeClass('none');
                var d = $.parseJSON(response);
                for (var key in d) {
                    if (d.hasOwnProperty(key)) {
                        $('#mapping tbody').append("<tr><td>"+ key + "</td><td>" + d[key] + "</td></tr>");
                    }
                }
            }
    );
};

$(document).ready(function(){
   $('#id_country').change(DW.get_trial_number_info)
});