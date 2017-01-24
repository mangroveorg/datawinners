import requests
from datawinners import settings


def all_db_names(server=settings.COUCH_DB_SERVER):
    all_dbs = requests.get(server + "/_all_dbs", auth=settings.COUCHDBMAIN_CREDENTIALS)
    return filter(lambda x: x.startswith('hni_'), all_dbs.json())


def db_names_with_custom_apps():
    return [
        "hni_ingc_qxb66747", "hni_mcsp_rns27499", "hni_cmcp_ifz989971", "hni_ingc-zambezia_gkg847094",
        "hni_society-for-family-health_mxj467597", "hni_municipio-de-nacala_bpi558204", "hni_marie-stopes-int-cambodia_ejn610045",
        "hni_msie_dlv745775", "hni_pnncseecaline_bpn692977", "hni_world-vision-mozambique_ttx287059"
    ]
