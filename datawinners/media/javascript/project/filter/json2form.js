$.fn.appendJson = function(json_data) {
    return this.each(function () {
        $this = $(this);
        if (!$this.is('form')) {
            return false;
        }
        for (var name in json_data) {
            $('<input type="hidden"/>').attr('name', name).val(json_data[name]).appendTo($this);
        }
    });
};