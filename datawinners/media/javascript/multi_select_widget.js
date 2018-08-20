DW.MultiSelectWidget = function (parentSelector, items, title) {
    var _this = this,
        parentElement = document.querySelector(parentSelector),
        headerDiv = document.createElement('div'),
        dropdownDiv = document.createElement('div'),
        headerContent = parentElement.children[0];

    headerDiv.appendChild(headerContent);
    parentElement.className = 'dw-multi-select-widget';
    headerDiv.className = 'header-area';
    dropdownDiv.className = 'content-area hide';
    parentElement.innerHTML = '';
    parentElement.appendChild(headerDiv);
    parentElement.appendChild(dropdownDiv);
    this.parentElement = parentElement;

    _this.on = function(eventName, callback) {
        _this.parentElement.addEventListener(eventName, callback);
    };

    _this.removeEventListener = function(eventName) {
        _this.parentElement.removeEventListener(eventName);
    }

    _this.setItems = function(items) {
        setItems(items);
    }

    function getWidgetData() {
        return _this.parentElement.widgetData || {};
    }

    function setWidgetData(data) {
        _this.parentElement.widgetData = data || {};
    }

    function getItems() {
        return getWidgetData().items || [];
    }

    function setItems(items) {
        var widgetData = getWidgetData();
        widgetData.items = items;
        setWidgetData(widgetData);
        var selectedItems = items.filter(function (item) { return item.checked; });
        var selectedValues = selectedItems.map(function (item) { return item.value; });
        setSelectedValues(selectedValues);
    }

    function getSelectedValues() {
        var widgetData = getWidgetData();
        return widgetData.selectedValues || [];
    }

    function setSelectedValues(values) {
        var widgetData = getWidgetData();
        widgetData.selectedValues = values || [];
        setWidgetData(widgetData);
    }

    function addSelectedValue(value) {
        setSelectedValues(getSelectedValues().concat(value));
    }

    function removeSelectedValue(value) {
        setSelectedValues(getSelectedValues().filter(function(x) { return x!== value; }));
    }

    function isSelected(value) {
        return getSelectedValues().indexOf(value) !== -1;
    }

    function toggleSelected(target) {
        if(isSelected(target.value)) {
            removeSelectedValue(target.value);
            _this.parentElement.dispatchEvent(new CustomEvent('check', { detail: {show: false, value: target.value} }));
        } else {
            addSelectedValue(target.value);
            _this.parentElement.dispatchEvent(new CustomEvent('check', { detail: {show: true, value: target.value} }));
        }
    }

    this.parentElement.addEventListener('change', function(event) {
        if(event.target.className == 'multiselect-checkbox') {
            toggleSelected(event.target);
        }
    });

    this.parentElement.addEventListener('click', function(event) {
        var dropdownDiv = _this.parentElement.children[1];

        if(dropdownDiv.children.length) {

            if(event.target === dropdownDiv.children[0]) {
                _this.parentElement.dispatchEvent(new CustomEvent('close', { detail: { selectedValues : getSelectedValues() } }));
                dropdownDiv.innerHTML = '';
                dropdownDiv.className = 'content-area hide';
                headerDiv.className = 'header-area';
            }

            if(event.target === dropdownDiv.querySelector(".done-btn")) {
                _this.parentElement.dispatchEvent(new CustomEvent('done', { detail: { selectedValues : getSelectedValues() } }));
                dropdownDiv.innerHTML = '';
                dropdownDiv.className = 'content-area hide';
                headerDiv.className = 'header-area';
            }
        } else {
            _this.parentElement.dispatchEvent(new CustomEvent('select'));
            headerDiv.className = 'header-area highlight';
            render();
        }
    });

    setItems(items || []);

    function render() {
        var dropdownDiv = _this.parentElement.children[1],
            titleSpan = document.createElement('span'),
            titleText = document.createTextNode(title || ''),
            closeButton = document.createElement('a'),
            doneButton = document.createElement('button'),
            doneButtonText = document.createTextNode('Done');
            closeButtonText = document.createTextNode('\u2715'),
            ul = document.createElement('ul'),
            items = getItems();

        titleSpan.appendChild(titleText);

        closeButton.appendChild(closeButtonText);
        closeButton.className = 'close-btn';

        doneButton.className = 'done-btn blue-btn';
        doneButton.appendChild(doneButtonText);

        dropdownDiv.className = 'content-area';
        dropdownDiv.appendChild(closeButton);
        dropdownDiv.appendChild(doneButton);
        dropdownDiv.appendChild(titleSpan);

        if (!items || !items.length) {
            var noItemsMessage = document.createTextNode('There is no item to select');
            dropdownDiv.appendChild(noItemsMessage);
            return;
        }
        for (var i in items) {
            var item = items[i],
                li = document.createElement('li'),
                label = document.createElement('label'),
                checkbox = document.createElement('input'),
                text = document.createElement('p');
                text.innerHTML = item.label;

            checkbox.type = 'checkbox';
            checkbox.value = item.value;
            checkbox.className = 'multiselect-checkbox'
            checkbox.checked = item.checked;
            label.appendChild(checkbox);
            label.appendChild(text);
            li.appendChild(label);
            ul.appendChild(li);
        }
        dropdownDiv.appendChild(ul);
        _this.parentElement.dispatchEvent(new CustomEvent('render', { detail: { items : items } }));
    }
};