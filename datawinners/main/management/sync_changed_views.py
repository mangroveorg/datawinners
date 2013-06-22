import logging

logger = logging.getLogger(__name__)


class SyncOnlyChangedViews():
    def update_views(self, current_views, new_views, manager):
        for view_name, view_def in new_views.iteritems():
            if view_name not in current_views or current_views[view_name] != new_views[view_name]:
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

    def sync_feed_views(self, manager):
        from datawinners.main.utils import find_views

        current_views = self.current_view_dictionary(manager)
        self.update_views(current_views, find_views('feedview'), manager)

    def current_view_dictionary(self, manager):
        design_docs = manager.database.view('_all_docs', startkey='_design', endkey='_design0', include_docs=True)
        view_dict = {}
        for design_doc in design_docs.rows:
            view_dict.update(design_doc.doc['views'])
        return view_dict

        # def current_view_dictionary(self, manager):
        #     design_docs = manager._get_design_docs()
        #     view_dict = {}
        #     for design_doc in design_docs:
        #         for view in design_doc['views']:
        #             view_dict.update({view: design_doc['views'][view]})
        #     return view_dict
        #
