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
        self.initialStateHtml = el.html();
    },

    setText: function (plainText) {
        var self = this;
        self.tags = plainText.match(/\{(.*?)\}/gi);
        var el = self.element;
        var styledText = '<div class="nonTags">' + plainText.replace(/{/g, '</div><span class="tags">').replace(/}/g, '</span><div class="nonTags">');
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
        el.on('focus',function () {
            before = el.html();
        }).on('blur keyup keydown paste', function (e) {
                if(e.keyCode==13) {e.preventDefault(); return false;}
                if ($(el).find('span.tags').text() != self.tags.join("").replace(/{/g, '').replace(/}/g, '')) {
                    
                    var after = $(el).html().replace("<br>","");
                    for(start=0; start<before.length && start< after.length; start++) if(before[start]!=after[start]) break;
                    for(end=0; end<before.length && end< after.length; end++) if(before[before.length - 1 - end]!=after[after.length - 1 - end]) break;
                    var diff = before.substring(start, before.length-end);
                    console.log( "Diff is "+diff);
                    diff = diff.replace(/<div[^>]*[>][^<]*[<][\/]div[>]/g, "")
                        .replace(/[^<]*[<][\/]div[>]/, "</div>")
                        .replace(/[<]div[^>]*[>].*/, "<div class=\"nonTags\">");
                    var modified_html = before.substring(0, start) + diff + before.substring(before.length-end);
                    el.html(modified_html);
                }
                before = el.html();
                self.handleAdjacentTags();
            });
    },

    handleAdjacentTags: function () {
        var firstSpan = $(this.element).find('span,div')[0];
        var lastSpan = $(this.element).find('span,div')[$(this.element).find('span,div').length - 1];

        //Insert empty span at the beginning
        if (!$(firstSpan).hasClass('nonTags')) {
            $('<div class="nonTags">&nbsp;</div>').insertBefore(firstSpan)
        }
        //Insert empty Span at the end
        if (!$(lastSpan).hasClass('nonTags')) {
            $('<div class="nonTags">&nbsp;</div>').insertAfter(lastSpan)
        }

        //Insert Empty span in between tags.
        $(this.element).find('div.nonTags').each(function (i, e) {
            if ($(e).text() == '') {
                $(e).html('&nbsp;');
            }
        });
        $(this.element).find('span.tags').each(function (i, e) {
            if ($(e).next().hasClass('tags')) {
                $('<div class="nonTags">&nbsp;</div>').insertAfter(e)
            }
        })
        $(this.element).remove('br');
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
    },
});