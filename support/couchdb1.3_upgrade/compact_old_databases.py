import couchdb

old_databases = ["hni_self_ftc732088",
"hni_urge-group_fkd503995",
"hni_test-lkg_fat909370",
"hni_biotech-services_lhe204912",
"hni_independent_apr157469",
"hni_krea_lut616387",
"hni_lp_xmu704769",
"hni_marie-stopes-international-sn_rcp754544",
"hni_pact_szw556981",
"hni_peace-corps-senegal_dga916366",
"hni_pact-myanmar_lie199211",
"hni_wwhps_kdt419593"]

server = couchdb.Server("http://admin:admin@localhost:5984/")
def get_survey_resp_count(db):
    d = server[db]
    d.compact()

for db in old_databases:
    get_survey_resp_count(db)