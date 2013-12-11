import elasticutils
from datawinners.settings import ELASTIC_SEARCH_URL

basic_es = elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes("hni_testorg_slx364903").doctypes("bd20c0ee622b11e3acca001c42a6c505")
# basic_es=basic_es.query(bd20c0ee622b11e3acca001c42a6c505_q4='bad')
basic_es = basic_es.query_raw({ "match" : {
        "ds_name" : "Tester",
    }})
s = basic_es.facet("bd20c0ee622b11e3acca001c42a6c505_q2_value")
s = s.facet("bd20c0ee622b11e3acca001c42a6c505_q3_value")
print s.facet_counts()