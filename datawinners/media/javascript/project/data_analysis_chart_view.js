
function drawReport(data) {
    baseColors = ["#113F96" ,"#A307A8" ,"#A89E08", "#CC2512"]
    $.each(data, function(index, row) {
        var answers = row[3];
        var type = row[1];
        var total = row[2];
        var colorScaleFactor = getColorScaleFactor(answers, total);

        drawBar(answers,  total, "#bar-" + index, baseColors[index%4]);
        drawPie(answers,  total, "#pie-" + index, baseColors[index%4], colorScaleFactor);
        drawTable(answers,  total, "#table-" + index, type);

        if(type == "select"){
            showBar(index);
        }else{
            showPie(index);
        }
    });
}

function drawTable(answers, total, locator, type){
    $(locator).empty();
    $legendTable = $('<table style="width: 400px"></table>');
    total_count = 0;
    $header = $('<tr ></tr>');
    $choiceHdr = $('<td style="font-weight: bold;">'+ gettext('Choice') +'</td>');
    $amountHdr = $('<td style="font-weight: bold;">'+ gettext('Frequency') +'</td>');
    if(type == 'select1'){
        $percentHdr = $('<td style="font-weight: bold;">'+ gettext('Percent') + '</td>');

    }else{
        first_row = answers[0]
        $percentHdr = $('<td style="font-weight: bold;white-space: nowrap;">'+ gettext('Percent') +'</td>');
        $tooltip_icon = $('<img style="margin-top: -4px;margin-left: 5px;"  src=" /media/images/help_icon.png" class="help_icon_1">');
        $percentHdr.append($tooltip_icon);
        $percent_tip = gettext('Percentage = Frequency / Total number of Submissions for this question.<br/>Example for ');
        $formula = first_row[0]+': '+ first_row[1] + "/" + total + ' = ' + Math.round(first_row[1]/total * 100) +'%';
        $p = $('<p></p>').append($percent_tip + $formula);
        $tooltip = $('<div class="tooltip" style="white-space: normal !important;"></div>').append($p);
        $percentHdr.append($tooltip);
    }
    $header.append($choiceHdr).append($amountHdr).append($percentHdr);
    $legendTable.append($header);

    $.each(answers, function(index, answer){
        $row = $('<tr ></tr>');
        $name = $('<td >'+ answer[0] +'</td>');
        $count = $('<td >'+answer[1]+'</td>');
        $percentage = $('<td >'+ Math.round(answer[1]/total*100)+'%</td>');
        $row.append($name).append($count).append($percentage);
        $legendTable.append($row);
        total_count += answer[1];
    });

    if(type == 'select1'){
        $footer= $('<tr ></tr>');
        $choiceFooter = $('<td style="background:#EEE;font-weight: bold;">'+ gettext('Total') +'</td>');
        $amountFooter = $('<td style="background:#EEE;font-weight: bold;">'+ total +'</td>');
        $percentFooter = $('<td style="background:#EEE;font-weight: bold;">'+ Math.round(total_count/total*100) +'%</td>');
        $footer.append($choiceFooter).append($amountFooter).append($percentFooter);
        $legendTable.append($footer);
    }

    $summary = $('<div style="margin-top: 5px">'+gettext("Total number of Submissions for this question: ")+ '<b>'+total+'</b></div>');

    $(locator).append($legendTable).append($summary);
    if(type == 'select'){
        $multi_choice_explaination = $('<div style="margin-top: 5px;font-style: italic; font-size: 11px;">'+
            gettext("Your Data Senders can choose more than 1 answer. That is why percentages may add up to more than 100%")+'</div>');
        $(locator).append($multi_choice_explaination);
    }

}

function drawBar(answers, total, locator, barColor) {
    var chart_data = [];
    var axis_label = [];
    $.each(answers, function(index, answer){
        var label = answer[0];
        label = label.replace(/'/g, '"')
        label = "<div style='-moz-text-overflow: ellipsis;font-size:8pt;padding:2px;color:black;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;' title='"+label+"'>" + label + '</div>';
        axis_label.push([index+1, label]);
        chart_data.push([answer[1],index+1]);
    });
    $.plot(
        $(locator),
        [
            {
                data:chart_data,
                color:barColor,
                bars:{
                    show:true,
                    barWidth:.4,
//                    align:"center",
                    horizontal: true,
                    fillColor: { colors: [barColor, getColorOf(barColor,0.8) , getColorOf(barColor,0.6)] }
                }

            }
        ],
        {
            yaxis:{
                ticks:axis_label,
                tickLength:0,
                labelWidth: 100
            },
            xaxis:{
                tickDecimals:0,
                autoscaleMargin:0.01
            },
            grid:{show:true},
            valueLabels: { show: true }
        }
    );
}

function drawPie(answers, total, locator, baseColor, colorScaleFactor) {
    var data = [];
    var parse = JSON.parse('[1,2,3,4,5]');
    $.each(answers, function(index, answer){
        data.push({label:answer[0], data:answer[1], color:getColorOf(baseColor, answer[1]/total * colorScaleFactor)})
    });

    $.plot($(locator), data,
        {
            series:{
                pie:{
                    show:true,
                    radius:.7,
                    label:{
                        show:true,
                        radius:5/6,
                        formatter:function (label, series) {
                            return '<div style="font-size:8pt;width:100px;text-align:center;padding:2px;color:black;overflow:hidden;white-space: nowrap;text-overflow: ellipsis;" title="'+label+'">' + label + '<br/>' + Math.round(series.data[0][1]/total*100) + '%</div>';
                        }
                    }
                }
            },legend:{show:false}
        });
}

function drawChart(data, submissionCount) {
    $chart_ol = $('#chart_ol');
    $('#chart_info').empty();
    $('#chart_info').append("<b>"+submissionCount + "</b> " +gettext("Submissions"))
    $intro_text = $('<div style="margin-top: 5px;color: #545454;font-style: italic;">'+gettext("View charts of your multiple choice questions.")+'</div>');
    $('#chart_info').append($intro_text);
    $chart_ol.empty();
    $.each(data, function(index, item) {
        $question_li = $('<li style="margin-bottom:50px"><h6>'+item[0]+'</h6>');
        if(item[1]=='select1'){
            $title = $('<ul style="margin-bottom:10px"></ul>');
            $title_pie_li = $('<li id="pie-li-'+index+'" style="float:left" ><a onclick="showPie('+index+')">'+gettext("Pie Chart")+'</a></li>');
            $title_sep_label = $('<label style="float:left;padding:0 5px  0 5px"> | </label>');
            $title_bar_li = $('<li id="bar-li-'+index+'" style="float:left" ><a onclick="showBar('+index+')">'+gettext("Bar Chart")+'</a></li>');
            $title.append($title_pie_li).append($title_sep_label).append($title_bar_li);
            $question_li.append($title);
        }

        $chart_div = $('<div id = "chart-'+index+'" style="display:inline-block;min-height:600px,margin-top: 30px;"/>');
        $pie_div = $('<div id="pie-'+index+'" style="width:500px;height:450px;float: left;margin-left: 50px;"/>');
        var barHeight = item[3].length*60;
        $bar_div = $('<div id="bar-'+index+'" style="margin-bottom:50px;width:500px;height:'+barHeight+'px;float: left;margin-left: 50px;"/>');
        $table_div = $('<div id="table-'+index+'" style="float:left;margin-left:100px"/>');
        $chart_div.append($pie_div).append($bar_div).append($table_div);
        $chart_ol.append($question_li).append($chart_div);;
    });
    drawReport(data);
}

function showPie(index){
    $("#pie-"+index).fadeIn(500);
    $("#bar-"+index).hide();
    $("#pie-li-"+index).addClass("title-selected");
    $("#bar-li-"+index).removeClass("title-selected");
}
function showBar(index){
    $("#bar-"+index).fadeIn(500);
    $("#pie-"+index).hide();
    $("#bar-li-"+index).addClass("title-selected");
    $("#pie-li-"+index).removeClass("title-selected");
}

function getColorOf(colorBase, percentFade){
    var whiteColor = new RGBColor('#FFFFFF').getDecimalVals()
    colorBase = new RGBColor(colorBase).getDecimalVals()
    var diffRed = colorBase.red -whiteColor.red ;
    var diffGreen = colorBase.green -whiteColor.red;
    var diffBlue = colorBase.blue -whiteColor.red;

    red = Math.round((diffRed * percentFade) + whiteColor.red);
    green = Math.round((diffGreen * percentFade) + whiteColor.green);
    blue = Math.round((diffBlue * percentFade) + whiteColor.blue);

    return colorToHex("rgb("+red+", "+green+", "+blue+")");
}

function colorToHex(color) {
    if (color.substr(0, 1) === '#') {
        return color;
    }
    var digits = /(.*?)rgb\((\d+), (\d+), (\d+)\)/.exec(color);

    var red = parseInt(digits[2]);
    var green = parseInt(digits[3]);
    var blue = parseInt(digits[4]);

    return digits[1] + '#' + formatNumberStringToTwoDigit((red).toString(16)) +
        formatNumberStringToTwoDigit((green).toString(16)) +
        formatNumberStringToTwoDigit((blue).toString(16));
};

function formatNumberStringToTwoDigit(numberString){
    return numberString.length >= 2 ? numberString: "0" + numberString;
}

function RGBColor (color) {
    this.color = color;

    this.getColor = function(){
        return this.color;
    };

    this.getDecimalVals = function(){
        var color = this.color;

        var rgb;
        var colorObj;

        color = color.replace("0x", "");
        color = color.replace("#", "");

        rgb = parseInt(color, 16);

        colorObj = new Object();
        colorObj.red = (rgb & (255 << 16)) >> 16;
        colorObj.green = (rgb & (255 << 8)) >> 8;
        colorObj.blue = (rgb & 255);

        return colorObj;
    };
};

function getColorScaleFactor(answers, total) {
    max_percent = 0;
    $.each(answers, function(index,answer){
        max_percent = Math.max(max_percent, answer[1]/total);
    });

    return 1.0/max_percent;
};

function toolTip(){
    $(".help_icon_1").tooltip({
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
}
$(document).ready(function () {
    toolTip();
});