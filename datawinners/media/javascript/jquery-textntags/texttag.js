/**
 * Created by ashwin on 16/5/14.
 */

$.widget("dw.myTextNTags", {
    options: {
        plainText: '',
        contentChangedHandler: function () {
        }
    },

    tags: [],
    initialStateHtml : '',

    _create: function () {
        var self = this;
        self.setText(self.options.plainText);
        var el = self.element;
        el.attr('contenteditable', 'true');
        var before;

        el.on('focus',function () {
            before = el.html();
        }).on('blur keyup paste', function () {
                self.handleAdjacentTags();
                if ($(el).find('span.tags').text() != self.tags.join("").replace(/{/g, '').replace(/}/g, '')) {
                    el.html(before);
                }

                else before = el.html();
            });
        $('.tags').attr('contenteditable', 'false');
        self.initialStateHtml = el.html();
    },

    setText: function (plainText) {
        var self = this;
        self.tags = plainText.match(/\{(.*?)\}/gi);
        var el = self.element;
        var styledText = '<span class="nonTags">' + plainText.replace(/{/g, '</span><span class="tags">').replace(/}/g, '</span><span class="nonTags">');
        el.html(styledText);
        self.handleAdjacentTags();
        var originalContents = self.getText();
        el.blur(function () {
            if (originalContents != self.getText()) {
                self._trigger('contentChangedHandler')
            }
        });
    },

    handleAdjacentTags: function () {
        var firstSpan = $(this.element).find('span')[0];
        var lastSpan = $(this.element).find('span')[$(this.element).find('span').length - 1];

        //Insert empty span at the beginning
        if(!$(firstSpan).hasClass('nonTags')){
            $('<span class="nonTags">&nbsp;</span>').insertBefore(firstSpan)
        }
        //Insert empty Span at the end
        if(!$(lastSpan).hasClass('nonTags')){
            $('<span class="nonTags">&nbsp;</span>').insertAfter(lastSpan)
        }

        //Insert Empty span in between tags.
        $(this.element).find('span').each(function (i, e) {
            if (e.className == 'nonTags' && $(e).text() == '') {
               $(e).html('&nbsp;');
            }
            if(e.className == 'tags' && $(e).next().hasClass('tags')){
                $('<span class="nonTags">&nbsp;</span>').insertAfter(e)
            }
        })
    },

    reset: function(){
        $(this.element).html(this.initialStateHtml);
    },

    getText: function () {
        var el = this.element;
        var returnText = '';
        $(el).find('span').each(function(i, eachSpan){
            if(eachSpan.className == 'nonTags')
                returnText+= ' '+$(eachSpan).text().replace( /^\s+|\s+$/g, "" );
            else if(eachSpan.className == 'tags'){
                returnText += ' {' + $(eachSpan).text() + '}';
            }
        });
        return returnText
    },

    _isTagTextPresentIn: function (selectedText, tags) {
        var arr = selectedText.split(' ');
        for (var i = 0; i < arr.length; i++) {
            if (tags.indexOf(arr[i]) != -1) return true;
        }
        return false;
    }

})
;

