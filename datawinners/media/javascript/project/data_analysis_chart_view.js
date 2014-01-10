
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
    var percentage = (total == 0 ? 'N.A.' : Math.round(first_row.count / total * 100) + '%');
    formula = first_row.term + ': ' + first_row.count + "/" + total + ' = ' + percentage;
    $p = $('<p></p>').append(percent_tip + formula);
    $tooltip = $('<div class="tooltip" ></div>').append($p);
    $percentHdr.append($tooltip);
    toolTip($tooltip_icon);
    return $percentHdr;
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
        $name = $('<td >' + answer.term + '</td>');
        $count = $('<td >' + answer.count + '</td>');
        $row.append($name).append($count);
        if(total != 0){
            var percentage = (total == 0 ? 'N.A.' : Math.round(answer.count / total * 100)+'%');
            $percentage = $('<td >' + percentage + '</td>');
            $row.append($percentage);
        }
        legendTable.append($row);
        total_count += answer.count;
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
    $.each(answers, function(i, ans){
            var label = ans.term;
            label = "<div class='barLabel' title='"+label+"'>" + label + '</div>';
            axis_label.push([i+1, label]);
            chart_data.push([ans.count,i+1]);
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
                    horizontal: true,
                    fillColor: { colors: [barColor, getColorOf(barColor,0.8) , getColorOf(barColor,0.6)] }
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
        var percentFade = (total == 0 ? 1 : 1.0*answer.count/total * 1.0/ colorScaleFactor);
        data.push({label:answer.term, data:answer.count, color:getColorOf(baseColor, percentFade)})
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

function drawChartBlockForQuestions(label,data,index, $chart_ol) {

    drawChartDivs = function (index) {
        $chart_div = $('<div id = "chart-' + index + '" class="chartDiv" />');
        var height = data.data.length * 61 ;
        $pie_div = $('<div class="pieDiv" id="pie-' + index + '"/>');
        $bar_div = $('<div class="barDiv" id="bar-' + index + '" style="height:' + height+ 'px;"/>');
        $table_div = $('<div id="table-' + index + '" class="tableDiv"/>');
        $chart_div.append($pie_div).append($bar_div).append($table_div);
        return $chart_div;
    }
        $question_li = $('<li><h6>' + label + '</h6>');
        if (data.field_type == 'select1') {
            drawChartSelectLink(index, $question_li);
        }
        $chart_div = drawChartDivs(index);
        $chart_ol.append($question_li).append($chart_div);
}

function drawChartReport(data,type,total,index) {
    baseColors = ["#446F27" ,"#39597C" ,"#4B2B71", "#76312F", "#398AA1"];
        var colorScaleFactor = (total == 0 ? 1: getColorScaleFactor(data, total));
        drawBar(data,  total, $("#bar-" + index), baseColors[index%5]);
        drawPie(data,  total, $("#pie-" + index), baseColors[index%5], colorScaleFactor);
        drawTable(data,  total, $("#table-" + index), type);

        if(type == "select"){
            showBar(index);
        }else{
            showPie(index);
        }
}

function drawChart(result, index,submissionCount, emptySubmissionText) {

    if(emptySubmissionText == '' && submissionCount == 0){
        emptySubmissionText = gettext('You do not have any multiple choice questions (Answer Type: List of choices) to display here.');
    }

    drawChartInfo(submissionCount, emptySubmissionText);
    drawChartReport(result.data,result.field_type,submissionCount,index);
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
        max_percent = Math.max(max_percent, 1.0*answer.count/total);
    });

    return max_percent;
};

function toolTip(element){
    $(element).tooltip({
        position: "top right",
        relative: true,
        opacity:0.8,
        events: {
            def:     "mouseover,mouseout",
            input:   "focus,blur",
            widget:  "focus mouseover,blur mouseout",
            tooltip: "click,click"
        }

    });
}
function showNoSubmissionExplanation($locator, message) {
    $locator.show();
    var $explanation_container = $('<div class="help_accordion">' + message + '</div>');
    $explanation_container.css("padding-right", "20px");
    $locator.append($explanation_container);
    return;
}