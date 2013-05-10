# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import logging
from find_all_db_managers import all_db_names
from mangrove.datastore.database import get_db_manager
import settings

db_server = "http://localhost:5984"
managers = all_db_names(db_server)

map_fun_project_docs = """
function(doc) {
    if (doc.document_type == 'FormModel' && !doc.void) {
        result ={}
        result[doc.form_code]={}
        result['no_active_lang']='False'

        no_lang = []
        act_lang = doc.metadata['activeLanguages']

        if(!act_lang){
           result['no_active_lang'] = 'True'
        }

        result['active_language'] = act_lang
        for (field in doc.json_fields){
            lang_list = []

            f_lang = doc.json_fields[field]['language']

            if(!f_lang){
                no_lang[no_lang.length]=field
            }else{
                if(doc.json_fields[field]['choices'])
                {
                    choices = doc.json_fields[field]['choices']
                    for(index in choices){
                        lang_list =[]
                        text = choices[index]['text']

                        for(lang_key in text){
                            lang_list[lang_list.length] = lang_key
                        }
                        if(lang_list.indexOf(f_lang) < 0){
                            result[doc.form_code]['lang_conflict'] = [f_lang, lang_list]
                        }
                    }
                }
            }
        }

        result[doc.form_code]['field_no_lang'] = no_lang

        if((result[doc.form_code]['field_no_lang'].length && doc.json_fields[field]['choices']) ||
            result[doc.form_code]['lang_conflict'].length || result['no_active_lang']=='True'){
            emit(doc.form_code, result)
        }
    }
}
"""

logger = logging.getLogger("django")

def find_subject():
    result = {}

    managers = all_db_names()
    for manager_name in managers:
        logger.info(manager_name)

        manager = get_db_manager(server=db_server, database=manager_name,credentials=settings.COUCHDBMAIN_CREDENTIALS)
        database_query = manager.database.query(map_fun_project_docs)
        if database_query:
            result[manager.database_name]=database_query
            logger.info("**********************pro found**********************" + manager_name)

find_subject()
