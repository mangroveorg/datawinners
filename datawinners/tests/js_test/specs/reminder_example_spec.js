describe("Calculation for next deadline for reminders", function() {

    it("should update example for next deadline in reminder settings month", function () {
        sinon.useFakeTimers(new Date(2014,11,11).getTime());
        var monthly_reminder = new MonthlyReminder();
        expected_date = new Date(2015, 0, 11);
        monthly_reminder.calculate_deadline(11);
        expect(monthly_reminder.reminder_date).toEqual(expected_date);

    });

    it("should update example for next deadline(february) in reminder settings", function () {
        sinon.useFakeTimers(new Date(2014,1,12).getTime());
        var monthly_reminder = new MonthlyReminder();
        expected_date = new Date(2014,1,28);
        monthly_reminder.calculate_deadline(30);
        expect(monthly_reminder.reminder_date).toEqual(expected_date);
    });

    it("should update example for next deadline(lastday) in reminder settings month", function () {
        sinon.useFakeTimers(new Date(2014,0,12).getTime());
        var monthly_reminder = new MonthlyReminder();
        expected_date = new Date(2014,0,31);
        monthly_reminder.calculate_deadline(0);
        expect(monthly_reminder.reminder_date).toEqual(expected_date);
    });

    it("should update example for next deadline(lastday + january) in reminder settings month", function () {
        sinon.useFakeTimers(new Date(2014,0,31).getTime());
        var monthly_reminder = new MonthlyReminder();
        expected_date = new Date(2014,1,28);
        monthly_reminder.calculate_deadline(0);
        expect(monthly_reminder.reminder_date).toEqual(expected_date);
    });

    it("should update example for next deadline(lastday + february) in reminder settings month", function () {
        sinon.useFakeTimers(new Date(2014,1,14).getTime());
        var monthly_reminder = new MonthlyReminder();
        expected_date = new Date(2014,1,28);
        monthly_reminder.calculate_deadline(0);
        expect(monthly_reminder.reminder_date).toEqual(expected_date);
    });

    it("should update example for next deadline in reminder settings week", function () {
        sinon.useFakeTimers(new Date(2015,0,12).getTime());
        var weekly_reminder = new WeeklyReminder();
        expected_date = new Date(2015,0,15);
        weekly_reminder.calculate_deadline(4);
        expect(weekly_reminder.reminder_date).toEqual(expected_date);
    });

    it("should update example for next deadline in reminder settings week", function () {
        var monthly_reminder = new WeeklyReminder();
        sinon.useFakeTimers(new Date(2015,0,1).getTime());
        expected_date = new Date(2015,0,8);
        monthly_reminder.calculate_deadline(4);
        expect(monthly_reminder.reminder_date).toEqual(expected_date);
    });

    it("should throw an error when reminder message is empty ", function () {
        var reminder = new ReminderInstance();
        reminder.text("");
        reminder.enable(true);

        expect(reminder.is_valid()).toEqual(false);
    });
});

