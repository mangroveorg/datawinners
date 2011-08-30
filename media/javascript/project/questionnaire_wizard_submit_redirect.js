function redirect() {
    var path = window.location.pathname;
    var element_list = path.split("/");
    window.location.href = '/project/wizard/datasenders/' + element_list[element_list.length - 2];
}