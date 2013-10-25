function reload_tables(responseJSON) {
    var markup = "<tr>\
                    <td>${name}</td>\
                    <td>${id}</td>\
                    <td>${location}</td>\
                    <td>${coordinates}</td>\
                    <td>${mobile_number}</td>\
                    <td>${email}</td>\
                  </tr>";
    if(responseJSON.successful_imports.length <= 0){
        $("#success_table").hide();
    }
    $.template("created_datasenders", markup);
    $("#imported_table").html('');
    _.each(responseJSON.successful_imports, function(datasenderjson){
        $("#imported_table").append($.tmpl("created_datasenders", datasenderjson));
    });
}
