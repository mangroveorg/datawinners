DW.ToolTip = function(options){
    options = options || {};
    var params = $.extend({
        target: $('.help_icon')
    }, options);

    params.target.tooltip({
        position: "top right",
        relative: true,
        opacity:0.8,
        events: {
            def:     "mouseover,mouseout",
            input:   "focus,blur",
            widget:  "focus mouseover,blur mouseout",
            tooltip: "click,click"
        }

    }).dynamic({ bottom: { direction: 'down', bounce: true } });
};