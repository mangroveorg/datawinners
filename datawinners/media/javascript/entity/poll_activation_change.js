function PollDateTime() {
    var self = this;
    self.number_of_days = ko.observable();
    var active_poll_days = [1,2,3,4,5];
    var current_date = new Date();
    var month_name_map = {0:gettext('January') ,
                      1: gettext('February') ,
                      2: gettext('March') ,
                      3: gettext('April') ,
                      4: gettext('May') ,
                      5: gettext('June') ,
                      6: gettext('July') ,
                      7: gettext('August') ,
                      8: gettext('September'),
                      9: gettext('October') ,
                      10:gettext('November') ,
                      11:gettext('December') };

    var item_map_week = {
            1: gettext('Monday'),
            2: gettext('Tuesday'),
            3: gettext('Wednesday'),
            4: gettext('Thursday'),
            5: gettext('Friday'),
            6: gettext('Saturday'),
            0: gettext('Sunday')
    };
    self.to_date_poll = ko.observable();
    var end_date;
    self.days_active = ko.computed(function(){
        var dat = new Date();
        dat.setDate(dat.getDate() + self.number_of_days());
        end_date = dat;
        self.to_date_poll(item_map_week[dat.getDay()]+", "+ dat.getDate()+ " "+ month_name_map[dat.getMonth()] +" "+ dat.getFullYear());
        return active_poll_days
    });

    function get_current_time() {
        return item_map_week[current_date.getDay()] + ", " +
                            current_date.getDate() + " " +
                            month_name_map[current_date.getMonth()] + " " +
                            current_date.getFullYear() + " " +
                            current_date.getHours() + ":" +
                            current_date.getMinutes() + ":" +
                            current_date.getSeconds();
    }
    self.from_date_poll = ko.observable(get_current_time());
}
