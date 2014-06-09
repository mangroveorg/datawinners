$(document).ready(function () {
    var editable = document.getElementById('myTextTags'),
        selection, range;

// Populates selection and range variables
    var captureSelection = function (e) {
        // Don't capture selection outside editable region
        var isOrContainsAnchor = false,
            isOrContainsFocus = false,
            sel = window.getSelection(),
            parentAnchor = sel.anchorNode,
            parentFocus = sel.focusNode;

        while (parentAnchor && parentAnchor != document.documentElement) {
            if (parentAnchor == editable) {
                isOrContainsAnchor = true;
            }
            parentAnchor = parentAnchor.parentNode;
        }

        while (parentFocus && parentFocus != document.documentElement) {
            if (parentFocus == editable) {
                isOrContainsFocus = true;
            }
            parentFocus = parentFocus.parentNode;
        }

        if (!isOrContainsAnchor || !isOrContainsFocus) {
            return;
        }

        selection = window.getSelection();

        // Get range (standards)
        if (selection.getRangeAt !== undefined) {
            range = selection.getRangeAt(0);

            // Get range (Safari 2)
        } else if (
            document.createRange &&
                selection.anchorNode &&
                selection.anchorOffset &&
                selection.focusNode &&
                selection.focusOffset
            ) {
            range = document.createRange();
            range.setStart(selection.anchorNode, selection.anchorOffset);
            range.setEnd(selection.focusNode, selection.focusOffset);
        } else {
            // Failure here, not handled by the rest of the script.
            // Probably IE or some older browser
        }
    };

// Recalculate selection while typing
    editable.onkeyup = captureSelection;

// Recalculate selection after clicking/drag-selecting
    editable.onmousedown = function (e) {
        editable.className = editable.className + ' selecting';
    };
    document.onmouseup = function (e) {
        if (editable.className.match(/\sselecting(\s|$)/)) {
            editable.className = editable.className.replace(/ selecting(\s|$)/, '');
            captureSelection();
        }
    };

    editable.onblur = function (e) {
        var cursorStart = document.createElement('span'),
            collapsed = !!range.collapsed;

        cursorStart.id = 'cursorStart';
//        cursorStart.appendChild(document.createTextNode('—'));

        // Insert beginning cursor marker
        range.insertNode(cursorStart);

        // Insert end cursor marker if any text is selected
        if (!collapsed) {
            var cursorEnd = document.createElement('span');
            cursorEnd.id = 'cursorEnd';
            range.collapse();
            range.insertNode(cursorEnd);
        }
    };

// Add callbacks to afterFocus to be called after cursor is replaced
// if you like, this would be useful for styling buttons and so on
    var afterFocus = [];
    editable.onfocus = function (e) {
        // Slight delay will avoid the initial selection
        // (at start or of contents depending on browser) being mistaken
        setTimeout(function () {
            var cursorStart = document.getElementById('cursorStart'),
                cursorEnd = document.getElementById('cursorEnd');

            // Don't do anything if user is creating a new selection
            if (editable.className.match(/\sselecting(\s|$)/)) {
                if (cursorStart) {
                    cursorStart.parentNode.removeChild(cursorStart);
                }
                if (cursorEnd) {
                    cursorEnd.parentNode.removeChild(cursorEnd);
                }
            } else if (cursorStart) {
                captureSelection();
                var range = document.createRange();

                if (cursorEnd) {
                    range.setStartAfter(cursorStart);
                    range.setEndBefore(cursorEnd);

                    // Delete cursor markers
                    cursorStart.parentNode.removeChild(cursorStart);
                    cursorEnd.parentNode.removeChild(cursorEnd);

                    // Select range
                    selection.removeAllRanges();
                    selection.addRange(range);
                } else {
                    range.selectNode(cursorStart);

                    // Select range
                    selection.removeAllRanges();
                    selection.addRange(range);

                    // Delete cursor marker
                    document.execCommand('delete', false, null);
                }
            }

            // Call callbacks here
            for (var i = 0; i < afterFocus.length; i++) {
                afterFocus[i]();
            }
            afterFocus = [];

            // Register selection again
            captureSelection();
        }, 10);
    };
});