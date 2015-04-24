from datawinners.settings import ELASTIC_SEARCH_HOST, ELASTIC_SEARCH_PORT


def get_elasticsearch_server_list():
    return [{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}]

