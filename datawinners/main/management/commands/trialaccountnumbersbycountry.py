# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.core.management.base import BaseCommand
import xlrd
import logging
from mangrove.utils.types import is_not_empty
import json
logger = logging.getLogger("django")

class Command(BaseCommand):
    def _get_network(self, networks, row):
        return [x for x in networks if x['fields']['network_name'] == row[2] and x['fields']['trial_sms_number'] == row[3]]

    def make_mapping_and_network(self, country_pk, mapping, mapping_pk, network_pk, networks, row):
        network = self._get_network(networks, row)
        if not len(network):
            networks.append(dict(pk=network_pk, model='countrytotrialnumbermapping.network',fields=dict(network_name=row[2], trial_sms_number=row[3], country=[country_pk])))
            network_pk += 1
        else:
            index = networks.index(network[0])
            country_list = network[0]['fields']['country']
            country_list.append(country_pk)
            network[0]['fields']['country'] = country_list
            networks[index] = network[0]
        return mapping_pk, network_pk

    def handle(self, *args, **options):
        import os
        import datawinners.settings as settings
        path = os.path.join(settings.PROJECT_DIR,'main/management/commands/trial coverage final.xls')
        work_book = xlrd.open_workbook(path)
        work_sheet = work_book.sheets()[0]
        
        countries = []
        networks = []
        mapping = []
        row_num = 2
        country_pk = 1
        network_pk = 1
        mapping_pk = 1
        while 1:
            if row_num == work_sheet.nrows:
                break

            row = work_sheet.row_values(row_num)
            if is_not_empty(row[0]):
                countries.append(dict(pk=country_pk, model='countrytotrialnumbermapping.country',fields=dict(country_name=row[0], country_code=str(row[1])[0:-2])))
                mapping_pk, network_pk = self.make_mapping_and_network(country_pk, mapping, mapping_pk,
                    network_pk, networks, row)
                row_num += 1
                while 1:
                    if row_num == work_sheet.nrows:
                        break
                    row = work_sheet.row_values(row_num)
                    if is_not_empty(row[0]):
                        break
                    if is_not_empty(row[2]):
                        mapping_pk, network_pk = self.make_mapping_and_network(country_pk, mapping, mapping_pk,
                            network_pk, networks, row)
                    row_num += 1
                country_pk += 1

        f = open('country.json', 'a')
        f.write(json.dumps(countries) + '\n')
        f.close()

        f = open('network.json', 'a')
        f.write(json.dumps(networks) + '\n')
        f.close()

        f = open('mapping.json', 'a')
        f.write(json.dumps(mapping) + '\n')
        f.close()
