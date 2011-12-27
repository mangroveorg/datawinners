jQuery(function($){
	$.datepicker.regional['fr'] = {
		closeText: 'Fermer',
		prevText: '&#x3c;Pr\351c',
		nextText: 'Suiv&#x3e;',
		currentText: 'Courant',
		monthNames: ['Janvier','F&eacute;vrier','Mars','Avril','Mai','Juin',
		'Juillet','Ao&ucirc;t','Septembre','Octobre','Novembre','D\351cembre'],
		monthNamesShort: ['Jan','F&eacute;v','Mar','Avr','Mai','Juin',
		'Juil','Ao&ucirc;t','Sept','Oct','Nov','D&eacute;c'],
		dayNames: ['Dimanche','Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi'],
		dayNamesShort: ['Dim','Lun','Mar','Mer','Jeu','Ven','Sam'],
		dayNamesMin: ['Di','Lu','Ma','Me','Je','Ve','Sa'],
		weekHeader: 'Sm',
		dateFormat: 'dd/mm/yy',
		firstDay: 1,
		isRTL: false,
		showMonthAfterYear: false,
		yearSuffix: ''};
	$.datepicker.setDefaults($.datepicker.regional['fr']);
});

//jQuery.fn.daterangepicker.options.rangeStartTitle = "Voalohany";
//alert(JSON.stringify(jQuery.fn.daterangepicker));