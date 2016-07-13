DW.MultiSelectWidget = function (parentSelector, items) {
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

    function toggleSelected(value) {
        if(isSelected(value)) {
            removeSelectedValue(value);
        } else {
            addSelectedValue(value);
        }
    }

    this.parentElement.addEventListener('change', function(event) {
        toggleSelected(event.target.value);
    });

    this.parentElement.addEventListener('click', function(event) {
        var dropdownDiv = _this.parentElement.children[1];

        if(dropdownDiv.children.length) {

            if(event.target === dropdownDiv.children[0]) {
                dropdownDiv.innerHTML = '';
                dropdownDiv.className = 'content-area hide';
                _this.parentElement.dispatchEvent(new CustomEvent('close', { detail: { selectedValues : getSelectedValues() } }));
            }

        } else {
            render();
        }
    });

    setItems(items || []);

    function render() {
        var dropdownDiv = _this.parentElement.children[1],
            closeButton = document.createElement('a'),
            closeButtonText = document.createTextNode('x'),
            ul = document.createElement('ul'),
            items = getItems();

        closeButton.appendChild(closeButtonText);
        closeButton.className = 'close-btn';
        dropdownDiv.className = 'content-area';
        dropdownDiv.appendChild(closeButton);

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
                text = document.createTextNode(item.label);

            checkbox.type = 'checkbox';
            checkbox.value = item.value;
            checkbox.checked = isSelected(item.value);
            label.appendChild(checkbox);
            label.appendChild(text);
            li.appendChild(label);
            ul.appendChild(li);
        }
        dropdownDiv.appendChild(ul);
    }
};