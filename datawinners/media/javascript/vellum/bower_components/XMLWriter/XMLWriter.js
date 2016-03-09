/**
 * XMLWriter - XML generator for Javascript, based on .NET's XMLTextWriter.
 * Copyright (c) 2008 Ariel Flesler - aflesler(at)gmail(dot)com | http://flesler.blogspot.com
 * Licensed under BSD (http://www.opensource.org/licenses/bsd-license.php)
 *
 * @version 1.1.0
 * @author Ariel Flesler, alexandern, Daniel Miller
 *
 * Original version: http://flesler.blogspot.com/2008/03/xmlwriter-for-javascript.html
 */

function XMLWriter( encoding, version ){
	if( encoding )
		this.encoding = encoding;
	if( version )
		this.version = version;
};
(function(){

XMLWriter.prototype = {
	encoding:'ISO-8859-1',// what is the encoding
	version:'1.0', //what xml version to use
	formatting: 'indented', //how to format the output (indented/none)  ?
	indentChar:'\t', //char to use for indent
	indentation: 1, //how many indentChar to add per level
	newLine: '\n', //character to separate nodes when formatting
	//start a new document, cleanup if we are reusing
	writeStartDocument:function( standalone ){
		this.close();//cleanup
		this.stack = [ ];
		this.standalone = standalone;
	},
	//get back to the root
	writeEndDocument:function(){
		this.active = this.root;
		this.stack = [ ];
	},
	//set the text of the doctype
	writeDocType:function( dt ){
		this.doctype = dt;
	},
	//start a new node with this name, and an optional namespace
	writeStartElement:function( name, ns ){
		if( ns )//namespace
			name = ns + ':' + name;

		var node = { n:name, a:{ }, c: [ ] };//(n)ame, (a)ttributes, (c)hildren

		if( this.active ){
			this.active.c.push(node);
			this.stack.push(this.active);
		}else
			this.root = node;
		this.active = node;
	},
	// Delete last node
	deleteEndElement:function(){
		this.stack.pop();
		this.active.c.pop();
	},
	//go up one node, if we are in the root, ignore it
	writeEndElement:function(){
		this.active = this.stack.pop() || this.root;
	},
	//add an attribute to the active node
	writeAttributeString:function( name, value ){
		if( this.active )
			this.active.a[name] = htmlAttr(value);
	},
	//add a pre-escaped attribute to the active node
	writeRawAttributeString:function( name, value ){
		if( this.active )
			this.active.a[name] = value;
	},
	//add a text node to the active node (XML will be escaped)
	writeString:function( text ){
		if( this.active )
			this.active.c.push(html(text));
	},
	//add XML string to the active node without extra escaping
	writeXML:function( text ){
		if( this.active )
			this.active.c.push(text);
	},
	//shortcut, open an element, write the text and close
	writeElementString:function( name, text, ns ){
		this.writeStartElement( name, ns );
		this.writeString(text);
		this.writeEndElement();
	},
	//add a text node wrapped with CDATA
	writeCDATA:function( text ){
		// keep nested CDATA
		text = text.replace(/>>]/g, "]]><![CDATA[>");
		this.writeString( '<![CDATA[' + text + ']]>' );
	},
	//add a text node wrapped in a comment
	writeComment:function( text ){
		this.writeString('<!-- ' + text + ' -->');
	},
	//generate the xml string, you can skip closing the last nodes
	flush:function(){
		if( this.stack && this.stack[0] )//ensure it's closed
			this.writeEndDocument();

		var
			chr = '', indent = '', num = this.indentation,
			formatting = this.formatting.toLowerCase() == 'indented',
			buffer = '<?xml version="'+this.version+'" encoding="'+this.encoding+'"';

		if( this.standalone !== undefined )
			buffer += ' standalone="' +  (this.standalone ? 'yes' : 'no') + '" ';
		buffer += ' ?>';

		buffer = [buffer];

		if( this.doctype && this.root )
			buffer.push('<!DOCTYPE '+ this.root.n + ' ' + this.doctype+'>');

		if( formatting ){
			while( num-- )
				chr += this.indentChar;
		}

		if( this.root )//skip if no element was added
			format( this.root, indent, chr, buffer );

		return buffer.join( formatting ? this.newLine : '' );
	},
	//cleanup, don't use again without calling startDocument
	close:function(){
		if( this.root )
			clean( this.root );
		this.active = this.root = this.stack = null;
	},
	getDocument: window.ActiveXObject
		? function(){ //MSIE
			var doc = new ActiveXObject('Microsoft.XMLDOM');
			doc.async = false;
			doc.loadXML(this.flush());
			return doc;
		}
		: function(){// Mozilla, Firefox, Opera, etc.
			return (new DOMParser()).parseFromString(this.flush(),'text/xml');
	}
};

var ESCAPES = {
	'&': '&amp;',
	'<': '&lt;',
	'>': '&gt;',
	'"': '&quot;',
	'\t': '&#9;',
	'\n': '&#10;',
	'\r': '&#13;'
};

function html(s) {
	return s.replace(/[&<>"]/g, function (c) { return ESCAPES[c]; });
}

// Escape whitespace in attributes so it is preserved during in-browser
// serialize/parse round-trip.
// See http://www.w3.org/TR/REC-xml/#AVNormalize for browser parsing rules.
function htmlAttr(s) {
	return String(s).replace(/[&<>"\n\r\t]/g, function (c) { return ESCAPES[c]; });
}

//utility, you don't need it
function clean( node ){
	var l = node.c.length;
	while( l-- ){
		if( typeof node.c[l] == 'object' )
			clean( node.c[l] );
	}
	node.n = node.a = node.c = null;
};

//utility, you don't need it
function format( node, indent, chr, buffer ){
	var
		xml = indent + '<' + node.n,
		nc = node.c.length,
		attr, child, i = 0;

	for( attr in node.a )
		xml += ' ' + attr + '="' + node.a[attr] + '"';

	xml += nc ? '>' : ' />';

	buffer.push( xml );

	if( nc ){
		do{
			child = node.c[i++];
			if( typeof child == 'string' ){
				if( nc == 1 )//single text node
					return buffer.push( buffer.pop() + child + '</'+node.n+'>' );
				else //regular text node
					buffer.push( indent+chr+child );
			}else if( typeof child == 'object' ) //element node
				format(child, indent+chr, chr, buffer);
		}while( i < nc );
		buffer.push( indent + '</'+node.n+'>' );
	}
};

})();