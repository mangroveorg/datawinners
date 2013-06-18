import logging

logger = logging.getLogger(__name__)

class SyncOnlyChangedViews():
    def update_views(self, current_views, new_views, manager):
        for key, value in new_views.iteritems():
            if key not in current_views or current_views[key] != new_views[key]:
                map_function = (value['map'] if 'map' in value else None)
                reduce_function = (value['reduce'] if 'reduce' in value else None)
                msg = "Syncing view ..... %s" % key
                logger.info(msg)
                print msg
                manager.create_view(key, map_function, reduce_function)

    def sync_view(self, manager):
        from datawinners.main.utils import find_views
        from mangrove.bootstrap.views import _find_views

        current_views = self.current_view_dictionary(manager)
        datawinners_views = find_views('couchview')
        mangrover_views = _find_views()
        new_views = dict(datawinners_views.items() + mangrover_views.items())
        self.update_views(current_views, new_views, manager)

    def sync_feed_views(self, manager):
        from datawinners.main.utils import find_views

        current_views = self.current_view_dictionary(manager)
        self.update_views(current_views, find_views('feedview'), manager)

    def current_view_dictionary(self, manager):
        design_docs = manager._get_design_docs()
        view_dict = {}
        for design_doc in design_docs:
            for view in design_doc['views']:
                view_dict.update({view: design_doc['views'][view]})
        return view_dict

