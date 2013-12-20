
function drawTable(answers, total, $locator, type){
    $legendTable = $('<table class="legend_table"></table>');
    drawTableHeader(answers, total, $legendTable);
    var total_count = drawTableRows(answers, total, $legendTable);

    if(type == 'select1'){
        drawTableFooter(total, total_count, $legendTable);
    }

    $locator.empty().append($legendTable);

    drawNotes($locator, type, total, total_count);
}

function drawTableHeader(answers, total, $legendTable) {
    $header = $('<tr ></tr>');
    $choiceHdr = $('<td class="lengendHeader">' + gettext('Choice') + '</td>');
    $amountHdr = $('<td class="lengendHeader">' + gettext('Frequency') + '</td>');
    $header.append($choiceHdr).append($amountHdr);
    if(total != 0){
        $percentHdr = drawPercentHeader(answers, total);
        $header.append($percentHdr);
    }

    $legendTable.append($header);
}

function drawPercentHeader(answers, total) {
    first_row = answers[0];
    $percentHdr = $('<td class="percentHeader">' + gettext('Percent') + '</td>');
    $tooltip_icon = $('<img src=" /media/images/help_icon.png" class="help_icon_1">');
    $percentHdr.append($tooltip_icon);
    percent_tip = gettext('Percentage = Frequency / Total number of Submissions for this question.<br/>Example for ');
    var percentage = (total == 0 ? 'N.A.' : Math.round(first_row[1] / total * 100) + '%');
    formula = first_row[0] + ': ' + first_row[1] + "/" + total + ' = ' + percentage;
    $p = $('<p></p>').append(percent_tip + formula);
    $tooltip = $('<div class="tooltip" ></div>').append($p);

    return $percentHdr.append($tooltip);
}

function drawTableFooter(total, total_count, legendTable) {
    $footer = $('<tr ></tr>');
    $choiceFooter = $('<td class="lengendFooter">' + gettext('Total') + '</td>');
    $amountFooter = $('<td class="lengendFooter">' + total + '</td>');
    $footer.append($choiceFooter).append($amountFooter);
    if (total != 0) {
        $percentFooter = $('<td class="lengendFooter">' + Math.round(total_count / total * 100) + '%</td>');
        $footer.append($percentFooter);
    }
    legendTable.append($footer);
}

function drawTableRows(answers, total, legendTable) {
    var total_count = 0;

    $.each(answers, function(index, answer) {
        $row = $('<tr ></tr>');
        $name = $('<td >' + answer[0] + '</td>');
        $count = $('<td >' + answer[1] + '</td>');
        $row.append($name).append($count);
        if(total != 0){
            var percentage = (total == 0 ? 'N.A.' : Math.round(answer[1] / total * 100)+'%');
            $percentage = $('<td >' + percentage + '</td>');
            $row.append($percentage);
        }
        legendTable.append($row);
        total_count += answer[1];
    });
    return total_count;
}

function drawNotes($locator, type, total, total_count) {
    var summary = gettext("Total number of Submissions for this question: ");
    $total = $('<b></b>').text(total);

    var text = "";
    if (type == 'select' && total != 0) {
        text = gettext("Your Data Senders can choose more than 1 answer.<br>That is why percentages may add up to more than 100%");
    } else if (type == 'select1' && total_count > total) {
        text = gettext("Previously multiple answers were permitted.<br> That is why percentages may add up to more than 100%.");
    }
    $('<div class="tableSummary"></div>').text(summary).append($total).appendTo($locator);
    $('<div class="mcExplaination">' + text + '</div>').appendTo($locator);
}

function drawBar(answers, total, $locator, barColor) {
    if (total == 0) {
        return showNoSubmissionExplanation($locator);
    }
    var chart_data = [];
    var axis_label = [];
    $.each(answers, function(index, answer){
        $.each(answer,function(i,ans){
            var label = ans.term;
            label = "<div class='barLabel' title='"+label+"'>" + label + '</div>';
            axis_label.push([i+1, label]);
            chart_data.push([ans.count,i+1]);

        });
    });
    $.plot(
        $locator,
        [
            {
                data:chart_data,
                color:barColor,
                bars:{
                    show:true,
                    barWidth:.4,
                    align:'center',
                    horizontal: true
//                    fillColor: { colors: [barColor, getColorOf(barColor,0.8) , getColorOf(barColor,0.6)] }
                }

            }
        ],
        {
            yaxis:{
                ticks:axis_label,
                tickLength:0,
                labelWidth: 100,
                autoscaleMargin:.05
            },
            xaxis:{
                tickDecimals:0,
                autoscaleMargin:0.01,
                min: 0
            },
            grid:{show:true},
            valueLabels: { show: true }
        }
    );
}

function drawPie(answers, total, $locator, baseColor, colorScaleFactor) {
    if (total == 0) {
        return showNoSubmissionExplanation($locator);
    }
    var data = [];
    $.each(answers, function(index, answer){
        var percentFade = (total == 0 ? 1 : answer[1]/total * colorScaleFactor);
        data.push({label:answer[0], data:answer[1], color:getColorOf(baseColor, percentFade)})
    });

    $.plot($locator, data,
        {
            series:{
                pie:{
                    show:true,
                    radius:.9,
                    label:{
                        show:true,
                        radius:1,
                        formatter:function (label, series) {
                            return '<div class="pieLabel" title="'+label+'">' + label + '<br/>' + Math.round(series.data[0][1]/total*100) + '%</div>';
                        }
                    }
                }
            },legend:{show:false}
        });
}

function drawChartInfo(submissionCount, emptySubmissionText) {
    $('#chart_info').empty().append("<b>" + submissionCount + "</b> " + gettext("Submissions"))
    var info_text = (emptySubmissionText != '' ? emptySubmissionText : "View charts of your multiple choice questions.");
    $intro_text = $('<div class="chartInfo2">' + gettext(info_text) + '</div>');
    $('#chart_info_2').empty().append($intro_text);
}

function drawChartSelectLink(index, $question_li) {
    $title = $('<ul></ul>');
    $title_pie_li = $('<li id="pie-li-' + index + '"><a onclick="showPie(' + index + ')">' + gettext("Pie Chart") + '</a></li>');
    $title_sep_label = $('<label > | </label>');
    $title_bar_li = $('<li id="bar-li-' + index + '"><a onclick="showBar(' + index + ')">' + gettext("Bar Chart") + '</a></li>');
    $title.append($title_pie_li).append($title_sep_label).append($title_bar_li);
    $question_li.append($title);
}

function drawChartBlockForQuestions(data, $chart_ol) {

    drawChartDivs = function (index, item) {
        $chart_div = $('<div id = "chart-' + index + '" class="chartDiv" />');
        $pie_div = $('<div id="pie-' + index + '" class="pieDiv"/>');
        var barHeight = item[3].length * 61 ;
        $bar_div = $('<div class="barDiv" id="bar-' + index + '" style="height:' + barHeight + 'px;"/>');
        $table_div = $('<div id="table-' + index + '" class="tableDiv"/>');
        $chart_div.append($pie_div).append($bar_div).append($table_div);
        return $chart_div;
    }

    $.each(data, function(index, item) {
        $question_li = $('<li><h6>' + item[0] + '</h6>');
        if (item[1] == 'select1') {
            drawChartSelectLink(index, $question_li);
        }
        $chart_div = drawChartDivs(index, item);
        $chart_ol.append($question_li).append($chart_div);
    });
}

function drawChartReport(data) {
    baseColors = ["#446F27" ,"#39597C" ,"#4B2B71", "#76312F", "#398AA1"];
    $.each(data, function(index, row) {
        var answers = row[3];
        var type = row[1];
        var total = row[2];
        var colorScaleFactor = (total == 0 ? 1: getColorScaleFactor(answers, total));

        drawBar(answers,  total, $("#bar-" + index), baseColors[index%5]);
        drawPie(answers,  total, $("#pie-" + index), baseColors[index%5], colorScaleFactor);
        drawTable(answers,  total, $("#table-" + index), type);

        if(type == "select"){
            showBar(index);
        }else{
            showPie(index);
        }
    });
}

function drawChart(data, submissionCount, emptySubmissionText) {
    $chart_ol = $('#chart_ol').attr('style', 'width:' + ($(window).width() - 85) + 'px').empty();

    if(emptySubmissionText == '' && data.length == 0){
        emptySubmissionText = gettext('You do not have any multiple choice questions (Answer Type: List of choices) to display here.');
    }

    drawChartInfo(submissionCount, emptySubmissionText);
    drawChartBlockForQuestions(data, $chart_ol);
    drawChartReport(data);
    toolTip();
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
function showNoSubmissionExplanation($locator) {
    var message = gettext("You don't have any submissions for this question yet");
    var $explanation_container = $('<div class="help_accordion text_align_right">' + message + '</div>');
    $explanation_container.css("padding-right", "20px");
    var padding = "60px";
    if ($locator.attr("id").split("-")[0] =="bar"){
        var padding = "40px";
    }
    $locator.append($explanation_container).css("padding-top", padding);
    return;
}