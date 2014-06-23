$.widget("dw.TextNTags", {
    options: {
        plainText: '',
        openingTag: '{',
        closingTag: '}',
        contentChangedHandler: function () {
        }
    },
    tags: [],
    initialStateHtml: '',

    _create: function () {
        var self = this;
        self.create(self.options.plainText);
    },

    create: function(text){
        var self = this;
        self.setText(text);
        var el = self.element;
        el.attr('contenteditable', 'true');
        self.deleteTagHandler();
        $('.tags').attr('contenteditable', 'false');
        $('.tags').attr('unselectable',"on");
        self.initialStateHtml = el.html();
        self._trigger('contentChangedHandler');
    },

    setText: function (plainText){
        var self = this;
        var regexPattern = new RegExp("\\"+ self.options.openingTag +"(.*?)\\" + self.options.closingTag, 'gi');

        self.tags = plainText.match(regexPattern) || [];
        var styledText = plainText;
        if(self.tags){
            $.each(self.tags, function(i, tag){
                var tagValue = _.str.ltrim(tag, self.options.openingTag);
                var tagValue = _.str.rtrim(tagValue, self.options.closingTag);
                var translated_tag = gettext(tagValue);
                styledText = styledText.replace(tag, '<span class="tags" data-tag="'+ tagValue +'">' + translated_tag + '</span>');
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
                    for(start = 0; start < before.length && start < after.length; start++){
                        if(before[start]!=after[start]){
                            break;
                        }
                    }
                    if (start > 0 && before[start-1] == '<'){
                        start--;
                    }
                    for(end = 0; end < before.length && end < after.length; end++){
                        if(before[before.length - 1 - end] != after[after.length - 1 - end]){
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