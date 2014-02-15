beforeEach(function(){
    var jsTestPath = window.location.pathname.split('jasmine_runner')[0]
    jasmine.getFixtures().fixturesPath = jsTestPath + '/specs/fixtures';
});