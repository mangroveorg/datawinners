$(document).ready(function(){
    console.log("yes");
    var data = ["india", "japan", "america"]
    $("#commune").autocomplete("/places", {
		minChars: 0,
		max: 12,
		autoFill: true,
		mustMatch: true,
		matchContains: false,
		scrollHeight: 220});
    $("#commune").bind("click", function(){
        $(this).val("");
    })
})