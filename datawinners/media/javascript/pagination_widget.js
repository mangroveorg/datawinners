function PaginationWidget(containerSelector, prevCallback, nextCallback, pageSize, count, totalCount) {
    var _this = this;
    _this.currentPageNumber = 1;
    _this.pageSize = pageSize;
    _this.totalCount = totalCount;

    var containerDiv = document.querySelector(containerSelector),
        prevLink = document.createElement('a'),
        prevText = document.createTextNode('< '),

        pageNumberSpan = document.createElement('span'),
        pageNumberStartSpan = document.createElement('span'),
        pageNumberStartText = document.createTextNode(getStartNumber()),
        pageNumberEndSpan = document.createElement('span'),
        pageNumberEndText = document.createTextNode(getEndNumber(count)),
        pageNumberTotalSpan = document.createElement('span'),
        pageNumberTotalText = document.createTextNode(_this.totalCount),
        hyphenText = document.createTextNode(" - "),
        ofText = document.createTextNode(" of "),

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
    firstLink.id = 'first';
    lastLink.id = 'last';
    firstLastLinkContainer.className = 'hide';
    containerDiv.className = 'pagination-widget';

    pageNumberStartSpan.id = 'page-start';
    pageNumberEndSpan.id = 'page-end';
    pageNumberTotalSpan.id = 'page-total';
    pageNumberStartSpan.className = 'digit';
    pageNumberEndSpan.className = 'digit';
    pageNumberTotalSpan.className = 'digit';

    prevLink.appendChild(prevText);
    nextLink.appendChild(nextText);

    firstLink.appendChild(firstLinkText);
    lastLink.appendChild(lastLinkText);

    firstLinkListItem.appendChild(firstLink);
    lastLinkListItem.appendChild(lastLink);

    firstLastLinkList.appendChild(firstLinkListItem);
    firstLastLinkList.appendChild(lastLinkListItem);
    firstLastLinkContainer.appendChild(firstLastLinkList);

    pageNumberStartSpan.appendChild(pageNumberStartText);
    pageNumberEndSpan.appendChild(pageNumberEndText);
    pageNumberTotalSpan.appendChild(pageNumberTotalText);

    pageNumberSpan.appendChild(pageNumberStartSpan);
    pageNumberSpan.appendChild(hyphenText);
    pageNumberSpan.appendChild(pageNumberEndSpan);
    pageNumberSpan.appendChild(ofText);
    pageNumberSpan.appendChild(pageNumberTotalSpan);
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
    renderFirst();
    renderLast();
    function updatePageNumber(count) {
        renderPrev();
        renderNext(count);
        renderFirst();
        renderLast();
        _this.containerDiv.querySelector('#page-start').textContent =  getStartNumber();
        _this.containerDiv.querySelector('#page-end').textContent =  getEndNumber(count);
    }

    function renderPrev() {
         _this.containerDiv.querySelector('#prev').className = (_this.currentPageNumber == 1) ? 'disabled' : '';
    }

    function renderNext(count) {
        _this.containerDiv.querySelector('#next').className =  (getEndNumber(count) == _this.totalCount) ? 'disabled' : '';
    }

    function getStartNumber() {
        return _this.totalCount ? (_this.pageSize * (_this.currentPageNumber - 1) + 1) : 0;
    }

    function getEndNumber(count) {
        return _this.pageSize * (_this.currentPageNumber - 1) + count;
    }

    function renderFirst() {
        _this.containerDiv.querySelector('#first').className =  (_this.currentPageNumber == 1) ? 'disabled' : '';
    }

    function renderLast() {
        _this.containerDiv.querySelector('#last').className =  (_this.currentPageNumber == Math.ceil(_this.totalCount/_this.pageSize)) || _this.totalCount == 0 ? 'disabled' : '';
    }

    return _this;
}