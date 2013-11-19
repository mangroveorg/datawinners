(function() {
  var jasmineEnv = jasmine.getEnv();
  jasmineEnv.updateInterval = 1000;

  var trivialReporter = new jasmine.TrivialReporter();

  jasmineEnv.addReporter(trivialReporter);
  jasmine.getEnv().addReporter(new jasmine.TapReporter());

  jasmineEnv.specFilter = function(spec) {
    return trivialReporter.specFilter(spec);
  };

  window.onload = function() {
    jasmineEnv.execute();
  };
})();