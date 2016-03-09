Equivalent XML JS [![Build status](https://secure.travis-ci.org/theozaurus/equivalent-xml-js.png)](http://travis-ci.org/theozaurus/equivalent-xml-js)
========

Equivalent XML JS is designed to ease the process of testing XML output. The work is a port of [equivalent-xml](https://github.com/mbklein/equivalent-xml)

 - Comparing text output is brittle due to the vagaries of serialization.
 - Attribute order doesn't matter.
 - Element order matters sometimes, but not always.
 - Text sometimes needs to be normalized, but CDATA doesn't.

Usage
=====

    > var doc1 = EquivalentXml.xml("<root><foo a='1' b='2'>Hello</foo><bar>World</bar></root>");
    > var doc2 = EquivalentXml.xml("<root><bar>World</bar><foo b='2' a='1'> Hello </foo></root>");
    > EquivalentXml.isEquivalent(doc1,doc2);
    true
    > EquivalentXml.isEquivalent(doc1,doc2, {element_order: true});
    false
    > EquivalentXml.isEquivalent(doc1,doc2, {normalize_whitespace: false});
    false
    
Options
=======

    {element_order: true }
    
  Require elements to be in the same relative position in order to be considered equivalent.

    {normalize_whitespace: false }
    
  Don't normalize whitespace within text nodes; require text nodes to match exactly.

Using with Jasmine
==================

  In your `SpecHelper.js` file add:
  
    beforeEach(function() {
      this.addMatchers(EquivalentXml.jasmine);
    });
    
  Then in your tests you can write
  
     expect(node_1).beEquivalentTo(node_2);
     expect(node_1).not.beEquivalentTo(node_2);
     expect(node_1).beEquivalentTo(node_2,{element_order: true});

Install tools
=============

If you want to test or build the source you will first need to install [Ruby](http://ruby-lang.org) and [Bundler](http://gembundler.com/). Once you have this:

    $ bundle install

Building the source with dependencies
=====================================

    $ mkdir build
    $ rake build

Tests
=====

All of the tests are written in [Jasmine](http://pivotal.github.com/jasmine/). [Sprockets](https://github.com/sstephenson/sprockets) is used to describe dependencies between the files. To start jasmine run:

    $ rake jasmine
    
Open your browser to [http://localhost:8888](http://localhost:8888)

If you want to run the tests directly in the console just type:

    $ rake jasmine:ci
    /Users/theo/.rvm/rubies/ruby-1.9.3-p0/bin/ruby -S rspec spec/javascripts/support/jasmine_runner.rb --colour --format progress
    [2012-03-15 15:46:50] INFO  WEBrick 1.3.1
    [2012-03-15 15:46:50] INFO  ruby 1.9.3 (2011-10-30) [x86_64-darwin11.1.0]
    [2012-03-15 15:46:50] INFO  WEBrick::HTTPServer#start: pid=39919 port=63714
    Waiting for jasmine server on 63714...
    jasmine server started.
    Waiting for suite to finish in browser ...
    ..........................................
    
Or you can check the current status of master using [Travis](http://travis-ci.org/#!/theozaurus/equivalent-xml-js)

Supported platforms
===================

It has been tested on:

 - Chrome 18
 - Safari 5
 - Firefox 
