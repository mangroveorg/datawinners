# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):

        db.execute("UPDATE activitylog_useractivitylog set action = 'Imported Identification Number(s)' where action = 'Imported Subject(s)'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Activated Questionnaire' where action = 'Activated Project'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Edited Questionnaire' where action = 'Edited Project'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Registered Identification Number' where action = 'Registered Subject'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Deleted Questionnaire' where action = 'Deleted Project'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Renamed Questionnaire' where action = 'Renamed Project'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Created Questionnaire' where action = 'Created Project'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Imported Identification Number' where action = 'Imported Subjects'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Added Identification Number Type' where action = 'Added Subject Type'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Removed Data Sender from Questionnaire' where action = 'Removed Data Sender from Project'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Added Data Senders to Questionnaire' where action = 'Added Data Senders to Projects'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Deleted Identification Number(s)' where action = 'Deleted Subject(s)'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Created Questionnaire' where action = 'Created project'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Deleted Identification Number(s)' where action = 'Deleted Subjects'")
        db.execute("UPDATE activitylog_useractivitylog set action = 'Added Data Sender(s) to Questionnaire(s)' where action = 'Added Data Sender(s) to Project(s)'")

    def backwards(self, orm):
        pass

    complete_apps = ['activitylog']

