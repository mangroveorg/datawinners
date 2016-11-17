function PaginationWidget(containerSelector, prevCallback, nextCallback) {
    var _this = this;
    _this.currentPageNumber = 1;

    var containerDiv = document.querySelector(containerSelector),
        prevLink = document.createElement('a'),
        prevText = document.createTextNode('<'),
        pageNumberSpan = document.createElement('span'),
        pageNumberText = document.createTextNode(_this.currentPageNumber),
        nextLink = document.createElement('a'),
        nextText = document.createTextNode('>');

    prevLink.id = 'prev';
    prevLink.className = 'hide';
    pageNumberSpan.id = 'page-number';
    nextLink.id = 'next';

    prevLink.appendChild(prevText);
    pageNumberSpan.appendChild(pageNumberText);
    nextLink.appendChild(nextText);
    containerDiv.appendChild(prevLink);
    containerDiv.appendChild(pageNumberSpan);
    containerDiv.appendChild(nextLink);
    _this.containerDiv = containerDiv;

    prevLink.addEventListener('click', function(event) {
        prevCallback && prevCallback(--_this.currentPageNumber);
        updatePageNumber();
    });

     nextLink.addEventListener('click', function(event) {
        nextCallback && nextCallback(++_this.currentPageNumber);
        updatePageNumber();
    });

    function updatePageNumber() {
        if(_this.currentPageNumber == 1) {
            _this.containerDiv.querySelector('#prev').className = 'hide';
        } else {
            _this.containerDiv.querySelector('#prev').className = '';
        }

        _this.containerDiv.querySelector('#page-number').textContent = _this.currentPageNumber;
    }

    return _this;
}