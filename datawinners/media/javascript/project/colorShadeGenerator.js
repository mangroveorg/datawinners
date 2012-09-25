
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
