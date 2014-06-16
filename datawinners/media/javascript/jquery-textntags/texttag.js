$.widget("dw.TextNTags", {
    options: {
        plainText: '',
        openingTag: '{',
        closingTag: '}',
        contentChangedHandler: function () {
        }
    },
    beginsWithTag: false,
    endsWithTag: false,
    tags: [],
    initialStateHtml: '',

    _create: function () {
        var self = this;
        self.setText(self.options.plainText);
        var el = self.element;
        el.attr('contenteditable', 'true');
        self.deleteTagHandler();
        $('.tags').attr('contenteditable', 'false');
        $('.tags').attr('unselectable',"on");
        self.initialStateHtml = el.html();
    },

    setText: function (plainText) {
        var self = this;
        var regexPattern = new RegExp("\\"+ self.options.openingTag +"(.*?)\\" + self.options.closingTag, 'gi');

        self.tags = plainText.match(regexPattern) || [];
        var styledText = plainText;
        if(self.tags){
            $.each(self.tags, function(i, tag){
                var tagValue = _.str.ltrim(tag, self.options.openingTag);
                var tagValue = _.str.rtrim(tagValue, self.options.closingTag);
                var translated_tag = gettext(tagValue);
                styledText = styledText.replace(tag, '<span class="tags" data-tag="'+ tagValue +'" >' + translated_tag + '</span>');
                self.tags[i] = translated_tag;
            });
        }
        var el = self.element;

        el.html(styledText);
        self.handleTags();
    },

    deleteTagHandler: function () {
        var self = this;
        var el = self.element;
        var before;
        el.on('keydown', function(e){
            if(e.which == 13) {
                e.preventDefault();
                return false;
            }
        });
        el.on('dragstart', function(){return false;});
        el.on('focus',function () {
            before = el.html();
        }).on('keydown', function(e){

            if(self.characterCount() >= 160 && isCharacterKeyPress(e)){
                e.preventDefault();
            }
        })
        .on('paste', function(e){
            e.preventDefault();
        })
        .on('blur keyup', function (e) {

                if ($(el).find('span.tags').text() != self.tags.join("").replace(new RegExp(self.options.openingTag, 'g'), '').replace(new RegExp(self.options.closingTag, 'g'), '')) {
                    var after = $(el).html();
                    var start, end;
                    for(start=0; start<before.length && start< after.length; start++){
                        if(before[start]!=after[start]){
                            break;
                        }
                    }
                    if (start > 0 && before[start-1] == '<'){
                        start--;
                    }
                    for(end=0; end<before.length && end< after.length; end++){
                        if(before[before.length - 1 - end]!=after[after.length - 1 - end]){
                            break;
                        }
                    }
                    var diff = before.substring(start, before.length-end);
                    if (/([^<]*<span[^>]*>[^<]*<\/span>[^<]*)*/gi.exec(diff)[0] != diff) {
                        el.html(before);
                    }
                    else {
                        diff = diff.replace(/[^<]*(<span[^>]*>[^<]*<\/span>)?[^<]*/gi, "$1");
                        var modified_html = before.substring(0, start) + diff + before.substring(before.length-end);
                        el.html(modified_html);
                    }
                }

                self.handleTags();
                self._trigger('contentChangedHandler');
                before = el.html();
            });
    },

    _isTextNode: function(el){
        return el.nodeType == 3 && el.textContent == ' ';
    },

    _isTagNode: function(el){
        return el.nodeType == 1 && el.tagName == 'SPAN';
    },

    handleTags: function () {
        var el = $(this.element);
        var self = this;

        if(/></.test(el.html())) {
            el.html(el.html().replace(/></g , "> <"));
        }

        var contents = el.contents();
        var contentLength = contents.length;
        if(contents && contentLength > 0){

            //if tag present at the end, then append a space for cursor to remain within widget - chrome hack
            if(contents[contentLength-1].nodeType && self._isTagNode(contents[contentLength-1])){
                this.endsWithTag = true;
                el.html(el.html() + ' ');
                contents = el.contents();
            }
            else if(contentLength > 1 && self._isTagNode(contents[contentLength-2])){
                if(self._isTagNode(contents[contentLength-1])){
                    this.endsWithTag = true;
                }
            }
            else{
                this.endsWithTag = false;
            }

            //if tag present at the start, then prepend a space for user to be able to add text at the beginning - ff hack
            if(contents[0].nodeType && self._isTagNode(contents[0])){
                this.beginsWithTag = true;
                el.html(' ' + el.html());
            }
            else if(contentLength > 1 && self._isTextNode(contents[0])){
                if(contents[1].nodeType && self._isTagNode(contents[1])){
                    this.beginsWithTag = true;
                }
            }
            else{
                this.beginsWithTag = false;
            }
        }
    },

    reset: function() {
        $(this.element).html(this.initialStateHtml);
    },

    getText: function() {
        var self = this;
        var el = self.element;
        var returnText = '';
        $.each(el.contents(), function(i, e){
            //text nodes
            if(e.nodeType == 3){
                returnText += e.textContent;
            }
            else if(e.nodeType == 1 &&  e.tagName.toLowerCase() === "br"){
                // ignore
            }
            else{
                returnText += self.options.openingTag + $(e).data('tag') + self.options.closingTag;
            }
        });

        if(self.beginsWithTag){
            //ignore starting space
            returnText = returnText.substring(1);
        }
        if(self.endsWithTag){
            //ignore ending space
            returnText = returnText.substring(0, returnText.length-1);
        }

        return returnText;
    },

    characterCount: function(){
        var self = this;
        var el = self.element;
        var textCount = 0;
        var tagsCount = self.tags ? self.tags.length: 0;
        el.contents().filter(function() {
            return this.nodeType == 3;
        }).each(function(i, t) {
            textCount += t.length;
        });

        if(self.beginsWithTag){
            //ignore starting space
            textCount -= 1;
        }

        if(self.endsWithTag){
            //ignore ending space
            textCount -= 1;
        }

        return textCount + tagsCount * 15;
    }
});

function isCharacterKeyPress(evt) {
    if (typeof evt.which == "undefined") {
        // This is IE, which only fires keypress events for printable keys
        return true;
    } else if (typeof evt.which == "number" && evt.which > 0) {
        // In other browsers except old versions of WebKit, evt.which is
        // only greater than zero if the keypress is a printable key.
        // We need to filter out backspace and ctrl/alt/meta key combinations
        // 37-40 (left, top , right, down)
        return !evt.ctrlKey && !evt.metaKey && !evt.altKey && evt.which != 8 && evt.which != 46 && !(evt.which >= 37 && evt.which <=40);
    }
    return false;
}