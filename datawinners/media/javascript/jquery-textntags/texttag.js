$.widget("dw.TextNTags", {
    options: {
        plainText: '',
        contentChangedHandler: function () {
        }
    },

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
        self.tags = plainText.match(/\{(.*?)\}/gi);
        var el = self.element;
        var styledText = '' + plainText.replace(/{/g, '<span class="tags">').replace(/}/g, '</span>');
        el.html(styledText);
        self.handleAdjacentTags();
        var originalContents = self.getText();
        el.blur(function () {
            if (originalContents != self.getText()) {
                self._trigger('contentChangedHandler')
            }
        });
    },

    deleteTagHandler: function () {
        var self = this;
        var el = self.element;
        var before;
        el.on('keydown', function(e){
            if(e.keyCode==13) {e.preventDefault(); return false;}
        });
        el.on('dragstart', function(){return false;});
        el.on('focus',function () {
            before = el.html();
        }).on('blur keyup paste', function (e) {
                if (e.keyCode == 0) return;
                if ($(el).find('span.tags').text() != self.tags.join("").replace(/{/g, '').replace(/}/g, '')) {
                    
                    var after = $(el).html();
                    for(start=0; start<before.length && start< after.length; start++) if(before[start]!=after[start]) break;
                    if (start > 0 && before[start-1] == '<') start--;
                    for(end=0; end<before.length && end< after.length; end++) if(before[before.length - 1 - end]!=after[after.length - 1 - end]) break;
                    var diff = before.substring(start, before.length-end);
                    if (/([^<]*<span[^>]*>[^<]*<\/span>[^<]*)*/gi.exec(diff)[0] != diff) {
                        el.html(before);
                    }else {
                        diff = diff.replace(/[^<]*(<span[^>]*>[^<]*<\/span>)?[^<]*/gi, "$1");
                        var modified_html = before.substring(0, start) + diff + before.substring(before.length-end);
                        el.html(modified_html);
                    }
                }

                self.handleAdjacentTags();
                before = el.html();
            });
    },

    handleAdjacentTags: function () {
        if(/></.test($(this.element).html())) {
            $(this.element).html($(this.element).html().replace(/></ , "> <"));
        }
        $(this.element).find('br').remove();
    },

    reset: function () {
        $(this.element).html(this.initialStateHtml);
    },

    getText: function () {
        var el = this.element;
        var returnText = '';
        $(el).find('span').each(function (i, eachSpan) {
            if (eachSpan.className == 'nonTags')
                returnText += ' ' + $(eachSpan).text().replace(/^\s+|\s+$/g, "");
            else if (eachSpan.className == 'tags') {
                returnText += ' {' + $(eachSpan).text() + '}';
            }
        });
        return returnText
    }
});