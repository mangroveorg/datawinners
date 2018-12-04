$(function(){
     var reminderAddDialogOptions = {
                    link_selector: "#undelete_project_section",
                    title: "Specify Reminders",
                    dialogDiv: "#reminder_add_dialog",
                    successCallBack: function(callback){
                        callback();
                        return true;
                    },
                    open: function(event, ui){
                        //hide the close button
                        $(".ui-dialog-titlebar-close", ui.dialog).hide();
                    },
                    width:500
                };
     new DW.Dialog(reminderAddDialogOptions).init().initializeLinkBindings();

     DW.loading();
     $.ajax({
        type: 'GETT',
        url: "/ajax/project/",
        success: function (response) {
            $.ajaxSetup({async: true});
            $.unblockUI();

            for( i in response) {
                var project = response[i];
                var str = '<tr>';
                if (project.is_poll) {
                    if (project.disable_link_class == '') {
                        str += '<td><a href="'+ project.link +'" class="project-id-class">' + project.name + '</a></td>';
                    } else {
                    str += '<td class="project-id-class">' + project.name + '</td>';
                    }

                    str += '<td class="' + hide_for_data_sender + '" style="width: 90px">' +
                        '<span class="' + project.hide_link_class + '">' +  DW.formatToLongDate(project.created) + '</span></td>';

                    str += '<td><span class="report_links"><a href="' + project.log + '"class="' + project.disabled + ' ' + project.disable_link_class + '">' + gettext("Analyze Data") + '</a><span class="' + project.hide_link_class + '">'+
                                    '|<a href="' + project.delete_links + '" class="delete_project"  id="delete_poll" data-is_poll="true">' + gettext("Delete Poll") + '</a>'+
                                '</span></td></tr>';
                } else {
                    if (project.disable_link_class == '') {
                        str += '<td><a href="' + project.link + '" class="project-id-class">' + project.name + '</a></td>';
                    } else {
                        str += '<td class="project-id-class">' + project.name + '</td>';
                    }

                    str += '<td class="' + hide_for_data_sender + '" style="width: 90px"><span class="' + project.hide_link_class + '">' + DW.formatToLongDate(project.created) + '</span></td>';

                    str += '<td>' +
                        '<span class="report_links">' +
                            '<span class="' + project.hide_link_class + '"><a href="' + project.analysis + '"class="' + project.disabled + ' ' + project.disable_link_class + project.hide_link_class + '">' + gettext("Analyze Data") + '</a>'+
                                '|<a href="' + project.log + '" ' +
                                    'class="' + project.disabled + ' ' + project.disable_link_class + '">' + gettext("View Submissions") + '</a>'+
                                '|' +
                            '</span>'+
                                '<a href="' + project.web_submission_link + '"' +
                                   'class="' + project.disabled + ' ' + project.web_submission_link_disabled + ' send-in-data-link">' + gettext("Make a Submission") + '</a>';

                            if (!project.is_advanced_questionnaire) {
                                str += '|' +
                                    '<a class="' + ((!project.disabled)?'import_link':'') +  project.disabled +'" data-projectname="' + project.encoded_name + '"' +
                                   'data-formcode="' + project.qid + '" data-projectid="' + project.project_id +'"'+
                                   'data-filename="' + project.import_template_file_name +'"' +
                                   'href="javascript:void(0);">' + gettext("Import a List of Submissions") + '</a>';
                                }

                                if (project.create_subjects_link) {
                                    for (entity_type in project.create_subjects_link) {
                                        var subject_link = project.create_subjects_link[entity_type];
                                        str += '|<a href="' + subject_link + '" class="register-subject-link">'+
                                        gettext("Register a new ") +  entity_type +'</a>';
                                    }

                                }

                                if (["NGO Admins","Project Managers","Read Only Users", "Extended Users"].indexOf(user_group) != -1) {
                                    str += '<span class="' + project.hide_link_class + '">' +
                                    '|<a href="' + project.delete_links + '" class="delete_project">' + gettext("Delete Questionnaire") +'</a>'+
                                '</span>';
                                }
                        str += '</span>';
                    str += '</td> </tr>';
                }

                $("#all_projects tbody").append(str);
            }

        }
    });
    
});