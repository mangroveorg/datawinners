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
        nextText = document.createTextNode(' >');

    prevLink.id = 'prev';
    pageNumberSpan.id = 'page-number';
    nextLink.id = 'next';

    prevLink.appendChild(prevText);
    pageNumberSpan.appendChild(pageNumberText);
    nextLink.appendChild(nextText);
    containerDiv.appendChild(pageNumberSpan);
    containerDiv.appendChild(prevLink);
    containerDiv.appendChild(nextLink);
    _this.containerDiv = containerDiv;

    prevLink.addEventListener('click', function(event) {
        prevCallback && prevCallback(--_this.currentPageNumber, updatePageNumber);
    });

     nextLink.addEventListener('click', function(event) {
        nextCallback && nextCallback(++_this.currentPageNumber, updatePageNumber);
    });

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
         _this.containerDiv.querySelector('#prev').style = (_this.currentPageNumber == 1) ? 'pointer-events: none; cursor: default' : '';
    }

    function renderNext(endPageNumber) {
        _this.containerDiv.querySelector('#next').style =  (endPageNumber == _this.totalCount) ? 'pointer-events: none; cursor: default' : '';
    }

    function getText(count) {
        var startPageNumber = _this.pageSize * (_this.currentPageNumber - 1);
        var endPageNumber = startPageNumber + count;
        startPageNumber += 1;
        return startPageNumber + " - " + endPageNumber + " of " + _this.totalCount;
    }

    return _this;
}