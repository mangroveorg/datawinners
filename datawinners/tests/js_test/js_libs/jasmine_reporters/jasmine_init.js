(function() {
  var jasmineEnv = jasmine.getEnv();
  jasmineEnv.updateInterval = 1000;

  var trivialReporter = new jasmine.TrivialReporter();

  jasmineEnv.addReporter(trivialReporter);
  jasmineEnv.addReporter(new jasmine.TerminalReporter({
    verbosity: 3,
    color: true
  }));

  jasmineEnv.specFilter = function(spec) {
    return trivialReporter.specFilter(spec);
  };

  window.onload = function() {
    jasmineEnv.execute();
  };
})();