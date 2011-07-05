$(document).ready(function(){
    var data = ["india", "japan", "america"]
    $("#id_location").autocomplete("/places", {
		minChars: 0,
		max: 12,
		autoFill: true,
		mustMatch: true,
		matchContains: false,
		scrollHeight: 220});
})