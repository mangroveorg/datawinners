DW.viewModel = {};

$(document).ready(function() {
     $('#autogen').unbind('change').change(function(event) {
        if ($('#autogen').attr('checked') != true) {
            $('#short_name').attr('disabled', '');

        }
        else {
            $('#short_name').removeClass('error');
            $("#short_name").parent().find('label.error').hide();
            $('#short_name').val("");
            DW.viewModel.message.s('');
            $('#short_name').attr('disabled', 'disabled');
        }
    });
    $('#register_entity').unbind('click').click(function() {
        if ($('#question_form').valid()) {
            if (DW.viewModel.message.s())
                DW.viewModel.message.s(DW.viewModel.message.s().toLowerCase());
            $.post($('#post_url').val(), {'format': 'json', 'data': JSON.stringify(ko.toJS(DW.viewModel), null, 1)},
                    function(response) {
                        var d = $.parseJSON(response);
                        $('#message').remove();
                        if (d.success) {
                            $('<span id="message" class="success-message-box">' + d.message + '</span>').insertBefore($('#question_form'));
                            $("#entity_name").val('');
                            $("#location").val('');
                            $("#geo_code").val('');
                            $("#description").val('');
                            $("#mobile_number").val('');
                            $("#short_name").val('');
                            $('#id_entity_type').val(0);

                            $('#message').delay(10000).fadeOut();
                        }
                        else {
                            $('<span id="message" class="error_message">' + d.message + '</span>').insertBefore($('#question_form'));
                        }
                    }
            );
        }
    }
    );
    $.widget("custom.catcomplete", $.ui.autocomplete, {
        _renderMenu: function(ul, items) {
            var self = this,
                    currentCategory = "";
            $.each(items, function(index, item) {
                if (item.category != currentCategory) {
                    ul.append("<li class='ui-autocomplete-category'>" + item.category + "</li>");
                    currentCategory = item.category;
                }
                self._renderItem(ul, item);
            });
        }
    });

    $("#id_location").catcomplete({
        source: "/places"
    });

    DW.viewModel = {
        'message': {
            'n': ko.observable(),
            's': ko.observable(),
            't': ko.observable(),
            'l': ko.observable(),
            'd': ko.observable(),
            'm': ko.observable(),
            'g': ko.observable(),
            'form_code': 'reg'
        },
        'transport': 'web',
        'source': 'web',
        'destination': 'mangrove'
    };
    ko.applyBindings(DW.viewModel);

});

