# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from glob import iglob
from mangrove.transport.submissions import get_submissions
import os
from mangrove.datastore.database import get_db_manager, remove_db_manager

SERVER = "http://localhost:5984"

output = open('migration.log', 'w')

def get_all_dbs():
    import urllib2

    all_dbs = urllib2.urlopen(SERVER + "/_all_dbs").read()
    dbs = (eval(all_dbs))
    document_stores = filter(lambda x: x.startswith('hni_'), dbs)
    return document_stores

def find_subject_short_code(dbm):
    rows = dbm.load_all_rows_in_view("inconsistent_subject_short_code")
    if rows:
        print '%d wrong subject short code in (%s)' % (len(rows), dbm.database_name)
        return [row.key for row in rows]
    else:
        return []

def find_entity_question_code(dbm):
    rows = dbm.load_all_rows_in_view("form_code_entity_question_code_mapping")
    if rows:
        return [row.key for row in rows]
    else:
        return []

def sync_views(dbm):
    for fn in iglob(os.path.join(os.path.dirname(__file__), 'views', '*.js')):
        view_name = os.path.splitext(os.path.basename(fn))[0].split('_', 1)[1]
        with open(fn) as f:
            print 'Create view [%s] in database [%s]' % (view_name, dbm.database_name)
            dbm.create_view(view_name, f.read(), "")


def get_entity_question_code_key(entity_question_code, submission):
    if entity_question_code.lower() in submission.values:
        entity_question_code_in_submission = entity_question_code.lower()
    elif entity_question_code.upper() in submission.values:
        entity_question_code_in_submission = entity_question_code.upper()
    else:
        entity_question_code_in_submission = entity_question_code
    return entity_question_code_in_submission


def correct_submissions(dbm, subject_short_codes_dict, entity_question_codes_dict):
    for form_code, entity_question_code in entity_question_codes_dict.items():
        print 'Get submission by form_code: %s' % form_code
        submissions = get_submissions(dbm, form_code, None, None, view_name="success_submission_log")
        for submission in submissions:
            entity_question_code_in_submission = get_entity_question_code_key(entity_question_code, submission)
            short_code_in_submission = submission.values.get(entity_question_code_in_submission)
            if short_code_in_submission in subject_short_codes_dict:
                output.writelines("\nSubmission before migration:\n")
                output.writelines(repr(submission.values))
                submission.values[entity_question_code_in_submission] = subject_short_codes_dict[short_code_in_submission]
                submission.save()
                output.writelines("\nSubmission after migration:\n")
                output.writelines(repr(submission.values))

def migrate(dbs):
    visited_dbs, success_dbs, failed_dbs = [], [], []
    for db in dbs:
        try:
            dbm = get_db_manager(server=SERVER, database=db)
            visited_dbs.append(db)
            sync_views(dbm)

            subject_short_codes_dict = dict(find_subject_short_code(dbm))
            if not subject_short_codes_dict:
                remove_db_manager(dbm)
                continue
            entity_question_codes_dict = dict(find_entity_question_code(dbm))
            output.writelines("\nMigration database [%s]" % db)
            correct_submissions(dbm, subject_short_codes_dict, entity_question_codes_dict)
            remove_db_manager(dbm)
            success_dbs.append(db)
        except Exception as e:
            failed_dbs.append(db)
            print e
            pass

    output.close()

    return visited_dbs, success_dbs, failed_dbs

if __name__ == "__main__":
    dbs = get_all_dbs()
    visited_dbs, success_dbs, failed_dbs = migrate(dbs)
    print '%s database(s) will be migrated:' % len(dbs)
    print dbs
    print "====================================================="
    print '%s database(s) are visited:' % len(visited_dbs)
    print visited_dbs
    print "====================================================="
    print '%s database(s) successfully migrated:' % len(success_dbs)
    print success_dbs
    print "====================================================="
    print '%s database(s) failed to migrated:' % len(failed_dbs)
    print failed_dbs
    print "====================================================="
