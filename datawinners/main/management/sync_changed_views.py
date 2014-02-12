import logging
import re

logger = logging.getLogger(__name__)


class SyncOnlyChangedViews():
    def has_view_contents_changed(self, current_views, new_views, view_name):
        return current_views[view_name]['map'] != new_views[view_name]['map'] or \
               current_views[view_name].get('reduce') != new_views[view_name].get('reduce')

    def update_views(self, current_views, new_views, manager):
        for view_name, view_def in new_views.iteritems():
            if view_name not in current_views or self.has_view_contents_changed(current_views, new_views, view_name):
                map_function = (view_def['map'] if 'map' in view_def else None)
                reduce_function = (view_def['reduce'] if 'reduce' in view_def else None)
                msg = "Syncing view ..... %s" % view_name
                logger.info(msg)
                print msg
                manager.create_view(view_name, map_function, reduce_function)

    def sync_view(self, manager):
        from datawinners.main.utils import find_views
        from mangrove.bootstrap.views import _find_views

        current_views = self.current_view_dictionary(manager)
        datawinners_views = find_views('couchview')
        mangrover_views = _find_views()
        new_views = dict(datawinners_views.items() + mangrover_views.items())
        self.update_views(current_views, new_views, manager)
        self.delete_old_views(current_views, new_views, manager)

    def sync_feed_views(self, manager):
        from datawinners.main.utils import find_views

        current_views = self.current_view_dictionary(manager)
        self.update_views(current_views, find_views('feedview'), manager)

    def current_view_dictionary(self, manager):
        design_docs = manager.database.view('_all_docs', startkey='_design', endkey='_design0', include_docs=True)
        view_dict = {}
        for design_doc in design_docs.rows:
            view_dict.update(design_doc.doc['views'])
            key_group = re.search('_design/(.+)', design_doc['id'])
            key = key_group.group(1)
            view_dict[key]['_id'] = design_doc['doc']['_id']
            view_dict[key]['_rev'] = design_doc['doc']['_rev']
        return view_dict

    def delete_old_views(self, current_views, new_views, manager):
        for current_view_name in current_views.keys():
            if current_view_name not in new_views:
                print 'Deleting view: %s from db: %s' % (current_view_name, manager.database.name)
                logging.info('Deleting view: %s from db: %s', current_view_name, manager.database.name)
                try:
                    manager.database.delete(current_views[current_view_name])
                except Exception as e:
                    print 'Failed to delete view: %s from db: %s' % (current_view_name, manager.database.name)
                    logging.error('Failed to delete view: %s from db: %s', current_view_name, manager.database.name)
                    logging.error('Exception: %s', e)

