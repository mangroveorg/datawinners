$(document).ready(function(){
  $('#tabs').tabs();
  var selectedIndex = parseInt($('#page-state').html());
  $('#tabs').tabs('selected', selectedIndex);
});

