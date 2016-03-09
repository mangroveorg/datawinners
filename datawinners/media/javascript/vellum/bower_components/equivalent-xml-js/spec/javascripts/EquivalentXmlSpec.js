/*jshint multistr:true */

describe("EquivalentXml",function(){

  it("should consider a document equivalent to itself", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    expect(doc1).beEquivalentTo(doc1);
  });

  it("should compare non-XML content based on its string representation", function(){
    expect(null).beEquivalentTo(null);
    expect('').beEquivalentTo('');
    expect('').beEquivalentTo(null);
    expect('foo').beEquivalentTo('foo');
    expect('foo').not.beEquivalentTo('bar');

    var doc1 = XML("<doc xmlns='foo:bar'><first order='1'>foo  bar baz</first><second>things</second></doc>");
    expect(doc1).not.beEquivalentTo(null);
  });

  it("should ensure that attributes match", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first order='1'>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'><first order='2'>foo  bar baz</first><second>things</second></doc>");
    expect(doc1).not.beEquivalentTo(doc2);

    doc1 = XML("<doc xmlns='foo:bar'><first order='1'>foo  bar baz</first><second>things</second></doc>");
    doc2 = XML("<doc xmlns='foo:bar'><first order='1'>foo  bar baz</first><second>things</second></doc>");
    expect(doc1).beEquivalentTo(doc2);
  });

  it("shouldn't care about attribute order", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first order='1' value='quux'>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'><first value='quux' order='1'>foo  bar baz</first><second>things</second></doc>");
    expect(doc1).beEquivalentTo(doc2);
  });

  it("shouldn't care about element order by default", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'><second>things</second><first>foo  bar baz</first></doc>");
    expect(doc1).beEquivalentTo(doc2);
  });

  it("should care about element order if :element_order => true is specified", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'><second>things</second><first>foo  bar baz</first></doc>");
    expect(doc1).not.beEquivalentTo(doc2,{element_order: true});
  });

  it("should ensure nodesets have the same number of elements", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'><second>things</second><first>foo  bar baz</first><third/></doc>");
    expect(doc1).not.beEquivalentTo(doc2);
  });

  it("should ensure namespaces match", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc xmlns='foo:baz'><first>foo  bar baz</first><second>things</second></doc>");
    expect(doc1).not.beEquivalentTo(doc2);
  });

  it("should compare namespaces based on URI, not on prefix", function(){
    var doc1 = XML("<doc xmlns:foo='foo:bar'><foo:first>foo  bar baz</foo:first><foo:second>things</foo:second></doc>");
    var doc2 = XML("<doc xmlns:baz='foo:bar'><baz:first>foo  bar baz</baz:first><baz:second>things</baz:second></doc>");
    expect(doc1).beEquivalentTo(doc2);
  });

  it("should not matter where the namespace is defined", function() {
    var doc1 = XML("<doc xmlns:foo='foo:bar'><foo:first/></doc>");
    var doc2 = XML("<doc><first xmlns='foo:bar'/></doc>");
    expect(doc1).beEquivalentTo(doc2);
  });

  it("should ignore declared but unused namespaces", function(){
    var doc1 = XML("<doc xmlns:foo='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc><first>foo  bar baz</first><second>things</second></doc>");
    expect(doc1).beEquivalentTo(doc2);
  });

  it("should normalize simple whitespace by default", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'><first>foo bar  baz</first><second>things</second></doc>");
    expect(doc1).beEquivalentTo(doc2);
  });

  it("shouldn't normalize simple whitespace if :normalize_whitespace => false is specified", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'><first>foo bar  baz</first><second>things</second></doc>");
    expect(doc1).not.beEquivalentTo(doc2,{normalize_whitespace: false});
  });

  it("should normalize complex whitespace by default", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'>\n\
  <second>things</second>\n\
  <first>\n\
    foo\n\
    bar baz\n\
  </first>\n\
</doc>");
    expect(doc1).beEquivalentTo(doc2);
  });

  it("shouldn't normalize complex whitespace if :normalize_whitespace => false is specified", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'>\n\
  <second>things</second>\n\
  <first>\n\
    foo\n\
    bar baz\n\
  </first>\n\
</doc>");
    expect(doc1).not.beEquivalentTo(doc2,{normalize_whitespace: false});
  });

  it("should ignore comment nodes", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'>\n\
  <second>things</second>\n\
  <!-- Comment Node -->\n\
  <first>\n\
    foo\n\
    bar baz\n\
  </first>\n\
</doc>");
    expect(doc1).beEquivalentTo(doc2);
  });

  it("should properly handle a mixture of text and element nodes", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><phrase>This phrase <b>has bold text</b> in it.</phrase></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'><phrase>This phrase in <b>has bold text</b> it.</phrase></doc>");
    expect(doc1).not.beEquivalentTo(doc2);
  });

  it("should properly handle documents passed in as strings", function(){
    var doc1 = "<doc xmlns='foo:bar'><first order='1'>foo  bar baz</first><second>things</second></doc>";
    var doc2 = "<doc xmlns='foo:bar'><first order='1'>foo  bar baz</first><second>things</second></doc>";
    expect(doc1).beEquivalentTo(doc2);

    doc1 = "<doc xmlns='foo:bar'><first order='1'>foo  bar baz</first><second>things</second></doc>";
    doc2 = "<doc xmlns='foo:bar'><first order='1'>foo  bar baz quux</first><second>things</second></doc>";
    expect(doc1).not.beEquivalentTo(doc2);
  });

  it("should compare nodesets", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
    expect(doc1.childNodes[0].childNodes).beEquivalentTo(doc1.childNodes[0].childNodes);
  });

  // it("should compare nodeset with string", function(){
  //   var doc1 = XML("<doc xmlns='foo:bar'><first>foo  bar baz</first><second>things</second></doc>");
  //   expect(doc1.childNodes[0].childNodes).beEquivalentTo("<first xmlns='foo:bar'>foo  bar baz</first><second xmlns='foo:bar'>things</second>");
  // });

  it("should compare cdata", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first><![CDATA[bits & bobs]]></first><second></second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'><second></second><first><![CDATA[bits & bobs]]></first></doc>");

    var doc3 = XML("<doc xmlns='foo:bar'><first><![CDATA[nuts & bolts]]></first><second></second></doc>");

    expect(doc1).beEquivalentTo(doc2);
    expect(doc1).not.beEquivalentTo(doc3);
  });

  it("should compare cdata to normal text element", function(){
    var doc1 = XML("<doc xmlns='foo:bar'><first><![CDATA[bits & bobs]]></first><second></second></doc>");
    var doc2 = XML("<doc xmlns='foo:bar'><second></second><first>bits &amp; bobs</first></doc>");

    var doc3 = XML("<doc xmlns='foo:bar'><first>nuts &amp; bolts</first><second></second></doc>");

    expect(doc1).beEquivalentTo(doc2);
    expect(doc1).not.beEquivalentTo(doc3);
  });

});
