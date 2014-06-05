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
//        var styledText = '<div class="nonTags">' + plainText.replace(/{/g, '</div><span class="tags">').replace(/}/g, '</span><div class="nonTags">');
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
//            if($.browser.msie && (e.keyCode==46 || e.keyCode == 8)){
//                var range = document.selection.createRange();
//                if (range.htmlText && range.htmlText.indexOf("SPAN")!= -1) {
//                    e.preventDefault();
//                    return false;
//                }
//            }
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
                    //if (end<(before.length-1) && before[before.length-end] == '>') end--; // tag close element is same for span and div
                    var diff = before.substring(start, before.length-end);
                    if (/([^<]*<span[^>]*>[^<]*<\/span>[^<]*)*/gi.exec(diff)[0] != diff) {
                        el.html(before);
                    }else {

                        // <span sdfsdf> abc</span><span sdfsdf> abd</span>
                        // <span sdfsdf> abd</span>
                        console.log( "Diff is "+diff);
                        diff = diff.replace(/[^<]*(<span[^>]*>[^<]*<\/span>)?[^<]*/gi, "$1");
    //                        replace(/<div[^>]*[>][^<]*[<][\/]div[>]/gi, "")
    //                        .replace(/[^<]*[<][\/]div[>]/i, "</div>")
    //                        .replace(/[<]div[^>]*[>].*/i, "<div class=\"nonTags\">");
                        var modified_html = before.substring(0, start) + diff + before.substring(before.length-end);
                        console.log(modified_html);
                        el.html(modified_html);
                    }
                }

                self.handleAdjacentTags();
                before = el.html();
            });
    },

    handleAdjacentTags: function () {
//        var firstSpan = $(this.element).find('span,div')[0];
//        var lastSpan = $(this.element).find('span,div')[$(this.element).find('span,div').length - 1];
//
        //Insert empty span at the beginning
//        if (!$(firstSpan).hasClass('nonTags')) {
//            $('<div class="nonTags">&nbsp;</div>').insertBefore(firstSpan)
//        }
//        //Insert empty Span at the end
//        if (!$(lastSpan).hasClass('nonTags')) {
//            $('<div class="nonTags">&nbsp;</div>').insertAfter(lastSpan)
//        }
//
//        $(this.element).find('span.tags').each(function (i, e) {
//            if ($(e).next().hasClass('tags')) {
//                $('<div class="nonTags">&nbsp;</div>').insertAfter(e)
//            }
//        })
        if(/></.test($(this.element).html())) {
            $(this.element).html($(this.element).html().replace(/></ , "> <"));
        }
        $(this.element).find('br').remove();
//        if ($.browser.mozilla) {
//            var text_in_div = /([<][\/][^>]*[>])([^<]+)([<][^>]*[>])?/;
//            if(text_in_div.test($("#myTextTags").html()))
//               $("#myTextTags").html($("#myTextTags").html().replace(text_in_div, "$1<div class=\"nonTags\">$2</div>$3"));
//            var text_at_start = /^(\S+)([<][^>]*[>])/;
//            if(text_at_start.test($("#myTextTags").html()))
//               $("#myTextTags").html($("#myTextTags").html().replace(text_at_start, "<div class=\"nonTags\">$1</div>$2"));
//        }
//        $(this.element).find(".nonTags").attr('contenteditable', 'true');
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