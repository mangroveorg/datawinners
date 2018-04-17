from datawinners.main.database import get_db_manager
import logging,time
from datetime import datetime
from datawinners.entity.views import _set_email_for_contacts
from django.test import RequestFactory
import json

test_env = True

get_deleted_ds_map = """
function(doc) {
    if (doc.document_type == "Contact" && doc.aggregation_paths._type[0] == 'reporter' && doc.void ) {
        var modified_date = doc.modified.substring(0, 13);
        if (modified_date == '2018-03-30T10') {
            var data = doc.data;
            emit([data.mobile_number, doc.short_code], doc);
        }
    }
}
"""

def set_up_global_variable():
    global db_name, org_id, manager, skipped_file, backupped_file, newly_created_then_deleted_file
    if test_env:
        db_name = "hni_testorg_slx364903"
        org_id = "SLX364903"
    else:
        db_name = "hni_marie-stopes_ehg954124"
        org_id = "EHG954124"

    manager = get_db_manager(db_name)

    skipped_file = open("skipped-as-already-existing.txt", 'a')
    backupped_file = open("backupped.txt", 'a')
    newly_created_then_deleted_file = open("created_then_deleted.txt", 'a')

def write_to_skipped(*args, **kwargs):
    skipped_file.writelines("%s, %s, %s\n" % args)
    skipped_file.flush()

def write_to_backupped(*args):
    backupped_file.writelines("%s, %s, %s\n" % args)
    backupped_file.flush()

def write_to_newly_created_then_deleted(*args):
    newly_created_then_deleted_file.writelines("%s, %s, %s\n" % args)
    newly_created_then_deleted_file.flush()


def get_unvoided_mobile_numbers():
    result = {}
    for row in manager.view.datasender_by_mobile(include_docs=True):
        result.update({row.key[0]: row.doc})
    return result


def retrieve_datasender(row, with_web_access=False):
    if not with_web_access:
        row['value']['data'].update({'email':{'value': ''}})
    row['value']['void'] = False
    manager.database.save(row['value'], process_post_update=False)


list_mailinators = ['l99@mailinator.com', 'l98@mailinator.com', 'l93@mailinator.com', 'l92@mailinator.com', 'l91@mailinator.com', 'l89@mailinator.com', 'l88@mailinator.com', 'l87@mailinator.com', 'l86@mailinator.com', 'l85@mailinator.com', 'l82@mailinator.com', 'l81@mailinator.com', 'l8@mailinator.com', 'l79@mailinator.com', 'l77@mailinator.com', 'l76@mailinator.com', 'l71@mailinator.com', 'l70@mailinator.com', 'l7@mailinator.com', 'l69@mailinator.com', 'l67@mailinator.com', 'l66@mailinator.com', 'l65@mailinator.com', 'l64@mailinator.com', 'l63@mailinator.com', 'l62@mailinator.com', 'l61@mailinator.com', 'l602@mailinator.com', 'l601@mailinator.com', 'l600@mailinator.com', 'l60@mailinator.com', 'l6@mailinator.com', 'l599@mailinator.com', 'l598@mailinator.com', 'l597@mailinator.com', 'l596@mailinator.com', 'l595@mailinator.com', 'l594@mailinator.com', 'l593@mailinator.com', 'l592@mailinator.com', 'l591@mailinator.com', 'l59@mailinator.com', 'l589@mailinator.com', 'l587@mailinator.com', 'l582@mailinator.com', 'l581@mailinator.com', 'l580@mailinator.com', 'l58@mailinator.com', 'l574@mailinator.com', 'l573@mailinator.com', 'l572@mailinator.com', 'l571@mailinator.com', 'l570@mailinator.com', 'l569@mailinator.com', 'l568@mailinator.com', 'l567@mailinator.com', 'l566@mailinator.com', 'l565@mailinator.com', 'l564@mailinator.com', 'l563@mailinator.com', 'l562@mailinator.com', 'l561@mailinator.com', 'l560@mailinator.com', 'l56@mailinator.com', 'l559@mailinator.com', 'l558@mailinator.com', 'l557@mailinator.com', 'l556@mailinator.com', 'l555@mailinator.com', 'l554@mailinator.com', 'l553@mailinator.com', 'l552@mailinator.com', 'l551@mailinator.com', 'l550@mailinator.com', 'l55@mailinator.com', 'l549@mailinator.com', 'l548@mailinator.com', 'l547@mailinator.com', 'l546@mailinator.com', 'l545@mailinator.com', 'l544@mailinator.com', 'l543@mailinator.com', 'l542@mailinator.com', 'l541@mailinator.com', 'l540@mailinator.com', 'l539@mailinator.com', 'l538@mailinator.com', 'l537@mailinator.com', 'l536@mailinator.com', 'l535@mailinator.com', 'l534@mailinator.com', 'l532@mailinator.com', 'l531@mailinator.com', 'l530@mailinator.com', 'l53@mailinator.com', 'l529@mailinator.com', 'l528@mailinator.com', 'l527@mailinator.com', 'l526@mailinator.com', 'l525@mailinator.com', 'l524@mailinator.com', 'l52@mailinator.com', 'l519@mailinator.com', 'l518@mailinator.com', 'l517@mailinator.com', 'l516@mailinator.com', 'l515@mailinator.com', 'l514@mailinator.com', 'l513@mailinator.com', 'l512@mailinator.com', 'l511@mailinator.com', 'l51@mailinator.com', 'l508@mailinator.com', 'l507@mailinator.com', 'l506@mailinator.com', 'l504@mailinator.com', 'l503@mailinator.com', 'l502@mailinator.com', 'l501@mailinator.com', 'l500@mailinator.com', 'l50@mailinator.com', 'l5@mailinator.com', 'l49@mailinator.com', 'l488@mailinator.com', 'l487@mailinator.com', 'l486@mailinator.com', 'l485@mailinator.com', 'l483@mailinator.com', 'l482@mailinator.com', 'l480@mailinator.com', 'l48@mailinator.com', 'l478@mailinator.com', 'l477@mailinator.com', 'l476@mailinator.com', 'l475@mailinator.com', 'l472@mailinator.com', 'l471@mailinator.com', 'l470@mailinator.com', 'l47@mailinator.com', 'l463@mailinator.com', 'l462@mailinator.com', 'l46@mailinator.com', 'l458@mailinator.com', 'l457@mailinator.com', 'l452@mailinator.com', 'l451@mailinator.com', 'l449@mailinator.com', 'l446@mailinator.com', 'l443@mailinator.com', 'l441@mailinator.com', 'l440@mailinator.com', 'l437@mailinator.com', 'l427@mailinator.com', 'l426@mailinator.com', 'l425@mailinator.com', 'l424@mailinator.com', 'l423@mailinator.com', 'l422@mailinator.com', 'l420@mailinator.com', 'l42@mailinator.com', 'l419@mailinator.com', 'l418@mailinator.com', 'l417@mailinator.com', 'l415@mailinator.com', 'l411@mailinator.com', 'l41@mailinator.com', 'l406@mailinator.com', 'l40@mailinator.com', 'l4@mailinator.com', 'l395@mailinator.com', 'l394@mailinator.com', 'l393@mailinator.com', 'l392@mailinator.com', 'l388@mailinator.com', 'l387@mailinator.com', 'l386@mailinator.com', 'l385@mailinator.com', 'l383@mailinator.com', 'l382@mailinator.com', 'l379@mailinator.com', 'l377@mailinator.com', 'l375@mailinator.com', 'l373@mailinator.com', 'l363@mailinator.com', 'l362@mailinator.com', 'l361@mailinator.com', 'l360@mailinator.com', 'l36@mailinator.com', 'l359@mailinator.com', 'l358@mailinator.com', 'l357@mailinator.com', 'l356@mailinator.com', 'l355@mailinator.com', 'l354@mailinator.com', 'l352@mailinator.com', 'l351@mailinator.com', 'l350@mailinator.com', 'l35@mailinator.com', 'l349@mailinator.com', 'l348@mailinator.com', 'l345@mailinator.com', 'l344@mailinator.com', 'l343@mailinator.com', 'l342@mailinator.com', 'l341@mailinator.com', 'l340@mailinator.com', 'l34@mailinator.com', 'l339@mailinator.com', 'l338@mailinator.com', 'l337@mailinator.com', 'l336@mailinator.com', 'l335@mailinator.com', 'l333@mailinator.com', 'l332@mailinator.com', 'l331@mailinator.com', 'l330@mailinator.com', 'l329@mailinator.com', 'l328@mailinator.com', 'l327@mailinator.com', 'l325@mailinator.com', 'l324@mailinator.com', 'l323@mailinator.com', 'l322@mailinator.com', 'l321@mailinator.com', 'l320@mailinator.com', 'l32@mailinator.com', 'l310@mailinator.com', 'l31@mailinator.com', 'l309@mailinator.com', 'l308@mailinator.com', 'l307@mailinator.com', 'l306@mailinator.com', 'l305@mailinator.com', 'l304@mailinator.com', 'l303@mailinator.com', 'l30@mailinator.com', 'l3@mailinator.com', 'l299@mailinator.com', 'l297@mailinator.com', 'l295@mailinator.com', 'l293@mailinator.com', 'l291@mailinator.com', 'l29@mailinator.com', 'l287@mailinator.com', 'l285@mailinator.com', 'l283@mailinator.com', 'l281@mailinator.com', 'l28@mailinator.com', 'l279@mailinator.com', 'l275@mailinator.com', 'l273@mailinator.com', 'l271@mailinator.com', 'l27@mailinator.com', 'l269@mailinator.com', 'l267@mailinator.com', 'l265@mailinator.com', 'l263@mailinator.com', 'l261@mailinator.com', 'l26@mailinator.com', 'l257@mailinator.com', 'l255@mailinator.com', 'l253@mailinator.com', 'l251@mailinator.com', 'l25@mailinator.com', 'l247@mailinator.com', 'l243@mailinator.com', 'l241@mailinator.com', 'l24@mailinator.com', 'l235@mailinator.com', 'l233@mailinator.com', 'l231@mailinator.com', 'l23@mailinator.com', 'l229@mailinator.com', 'l227@mailinator.com', 'l22@mailinator.com', 'l219@mailinator.com', 'l217@mailinator.com', 'l213@mailinator.com', 'l209@mailinator.com', 'l208@mailinator.com', 'l207@mailinator.com', 'l204@mailinator.com', 'l203@mailinator.com', 'l201@mailinator.com', 'l20@mailinator.com', 'l18@mailinator.com', 'l17@mailinator.com', 'l16@mailinator.com', 'l15@mailinator.com', 'l1455@mailinator.com', 'l14@mailinator.com', 'l13@mailinator.com', 'l12@mailinator.com', 'l118@mailinator.com', 'l117@mailinator.com', 'l116@mailinator.com', 'l113@mailinator.com', 'l111@mailinator.com', 'l110@mailinator.com', 'l11@mailinator.com', 'l103@mailinator.com', 'l1@mailinator.com', 'spo01@mailinator.com', 'spo02@mailinator.com', 'spo03@mailinator.com', 'spo04@mailinator.com', 'spo05@mailinator.com', 'spo06@mailinator.com', 'spo07@mailinator.com', 'spo08@mailinator.com', 'spo09@mailinator.com', 'spo10@mailinator.com', 'spo11@mailinator.com', 'spo12@mailinator.com', 'spo13@mailinator.com', 'spo14@mailinator.com', 'spo15@mailinator.com', 'spo16@mailinator.com', 'spo17@mailinator.com', 'spo18@mailinator.com', 'spo19@mailinator.com', 'spo20@mailinator.com', 'spo21@mailinator.com', 'spo22@mailinator.com', 'spo23@mailinator.com', 'spo24@mailinator.com', 'spo25@mailinator.com', 'spo26@mailinator.com', 'spo27@mailinator.com', 'spo28@mailinator.com', 'spo29@mailinator.com', 'spo30@mailinator.com', 'spo31@mailinator.com', 'spo32@mailinator.com', 'spo33@mailinator.com', 'spo34@mailinator.com', 'spo35@mailinator.com', 'spo36@mailinator.com', 'spo37@mailinator.com']

def compare_mails(deleted, mailinators):
    result = []
    for m in mailinators:
        if m not in deleted:
            result.append(m)
    return result


def save_web_users(user_dict):
    data = json.dumps(user_dict)
    request = RequestFactory().post("url", data={'post_data':data})
    request.LANGUAGE_CODE = "en"
    #print request.POST['post_data']
    print _set_email_for_contacts(manager, org_id, request)


def get_ids(row):
    if not isinstance(row.value.get('data').get('email'), unicode):
        email = row.value.get('data').get('email', {'value':''}).get('value')
    else:
        email = row.value.get('data').get('email', '')
    mobile_number = row.value.get('data').get('mobile_number').get('value')
    short_code = row.value.get('short_code')
    return short_code, mobile_number, email

def delete_entry(row):
    row['void'] = True
    manager.database.save(row, process_post_update=False)
    write_to_newly_created_then_deleted(row['short_code'], row['data']['mobile_number']['value'], row['data']['email']['value'])
    
def retrieve_deleted_ds():
    set_up_global_variable()
    
    rows = manager.database.query(get_deleted_ds_map)
    unvoided_mobile_numbers = get_unvoided_mobile_numbers()
    list_users, total = [], 0

    for row in rows:
        try:
            short_code, mobile_number, email = get_ids(row)

            if email in list_mailinators:
                if mobile_number in unvoided_mobile_numbers.keys():
                    delete_entry(unvoided_mobile_numbers.get(mobile_number))

                retrieve_datasender(row, True)
                #list_users.append({'email':email, 'reporter_id': short_code, '_id':row.value.get('_id')})
                web_user_to_save = [{'email':email, 'reporter_id': short_code, '_id':row.value.get('_id')}]
                write_to_backupped(short_code, mobile_number, email)
                save_web_users(web_user_to_save)

            elif mobile_number in unvoided_mobile_numbers.keys():
                write_to_skipped(mobile_number, email, short_code)
                continue
            else:
                retrieve_datasender(row)
                write_to_backupped(short_code, mobile_number, "%s, *" % email)
                
            total += 1
            
        except Exception as e:
            raise e

    print "total retrieved %d" % total

print datetime.now()
retrieve_deleted_ds()
print datetime.now()
