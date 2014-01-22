describe("analysis chart test", function () {
    beforeEach(function () {
        $("#data_sender_filter").autocomplete();
        spyOn(jQuery, "ajax").andCallFake(function (params) {
            return params.success(
                {"total": 1, "result": {"mcq1": {"field_type": "select1", "data": [
                    {"count": 1, "term": "q"},
                    {"count": 0, "term": "a"}
                ], 'count': 1}, "Question 3": {"field_type": "select", "data": [
                    {"count": 1, "term": "a"},
                    {"count": 0, "term": "b"}
                ], 'count': 1}}}
            );
        });
        var generator = new DW.SubmissionAnalysisChartGenerator();
        generator.generateCharts();
    });
    it('should show one bar chart and one pie chart', function () {
        expect($(".pieDiv").filter(":visible").length).toEqual(1);
        expect($(".barDiv").filter(":visible").length).toEqual(1);
    });
    it('test selecting bar chart option', function () {
        $("#bar-li-0 a").trigger("click");
        expect($(".pieDiv").filter(":visible").length).toEqual(0);
        expect($(".barDiv").filter(":visible").length).toEqual(2);
    });
});