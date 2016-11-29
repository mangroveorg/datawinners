function PaginationWidget(containerSelector, prevCallback, nextCallback, pageSize, count, totalCount) {
    var _this = this;
    _this.currentPageNumber = 1;
    _this.pageSize = pageSize;
    _this.totalCount = totalCount;

    var containerDiv = document.querySelector(containerSelector),
        prevLink = document.createElement('a'),
        prevText = document.createTextNode('< '),
        pageNumberSpan = document.createElement('span'),
        pageNumberText = document.createTextNode(getText(count)),
        nextLink = document.createElement('a'),
        nextText = document.createTextNode(' >'),
        firstLastLinkContainer = document.createElement('div'),
        firstLastLinkList = document.createElement('ul'),
        firstLinkListItem = document.createElement('li'),
        firstLink = document.createElement('a'),
        lastLinkListItem = document.createElement('li'),
        lastLink = document.createElement('a'),
        firstLinkText = document.createTextNode('First'),
        lastLinkText = document.createTextNode('Last');

    var timeoutFirstLastLinkContainer;
    var hideFirstLastLinkContainer = function(event) {
        if (firstLastLinkContainer.className.indexOf('hide') == -1) {
            firstLastLinkContainer.className += ' hide';
        }
    };



//  initializing the styles
    prevLink.id = 'prev';
    pageNumberSpan.id = 'page-number';
    nextLink.id = 'next';
    firstLastLinkContainer.id = 'quick-links-container';
    firstLastLinkContainer.className = 'hide';
    containerDiv.className = 'pagination-widget';

    prevLink.appendChild(prevText);
    pageNumberSpan.appendChild(pageNumberText);
    nextLink.appendChild(nextText);

    firstLink.appendChild(firstLinkText);
    lastLink.appendChild(lastLinkText);

    firstLinkListItem.appendChild(firstLink);
    lastLinkListItem.appendChild(lastLink);

    firstLastLinkList.appendChild(firstLinkListItem);
    firstLastLinkList.appendChild(lastLinkListItem);
    firstLastLinkContainer.appendChild(firstLastLinkList);

    containerDiv.appendChild(pageNumberSpan);
    containerDiv.appendChild(prevLink);
    containerDiv.appendChild(nextLink);
    containerDiv.appendChild(firstLastLinkContainer);
    _this.containerDiv = containerDiv;


    prevLink.addEventListener('click', function(event) {
        prevCallback && prevCallback(--_this.currentPageNumber, updatePageNumber);
    });

    nextLink.addEventListener('click', function(event) {
        nextCallback && nextCallback(++_this.currentPageNumber, updatePageNumber);
    });

    firstLink.addEventListener('click', function(event) {
        _this.currentPageNumber = 1;
        prevCallback && prevCallback(_this.currentPageNumber, updatePageNumber);
    });

    lastLink.addEventListener('click', function(event) {
        _this.currentPageNumber = Math.ceil(_this.totalCount/_this.pageSize);
        prevCallback && prevCallback(_this.currentPageNumber, updatePageNumber);
    });

    pageNumberSpan.addEventListener('mouseenter', function(event) {
        firstLastLinkContainer.className = firstLastLinkContainer.className.replace('hide', '');
    });

    pageNumberSpan.addEventListener('mouseleave', function(event) {
        timeoutFirstLastLinkContainer = setTimeout(hideFirstLastLinkContainer, 100);
    });

    firstLastLinkContainer.addEventListener('mouseenter', function(event) {
        clearTimeout(timeoutFirstLastLinkContainer);
    });

    firstLastLinkContainer.addEventListener('mouseleave', hideFirstLastLinkContainer);

    renderPrev();
    renderNext(count);

    function updatePageNumber(count) {
        var startPageNumber = _this.pageSize * (_this.currentPageNumber - 1);
        var endPageNumber = startPageNumber + count;
        startPageNumber += 1;
        renderPrev();
        renderNext(endPageNumber, _this.totalCount);
        _this.containerDiv.querySelector('#page-number').textContent = getText(count);
    }

    function renderPrev() {
         _this.containerDiv.querySelector('#prev').className = (_this.currentPageNumber == 1) ? 'disabled' : '';
    }

    function renderNext(endPageNumber) {
        _this.containerDiv.querySelector('#next').className =  (endPageNumber == _this.totalCount) ? 'disabled' : '';
    }

    function getText(count) {
        var startPageNumber = _this.pageSize * (_this.currentPageNumber - 1);
        var endPageNumber = startPageNumber + count;
        startPageNumber += 1;
        return startPageNumber + " - " + endPageNumber + " of " + _this.totalCount;
    }

    return _this;
}