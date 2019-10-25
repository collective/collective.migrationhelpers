# -*- coding: utf-8 -*-
from plone import api
from plone.app.contenttypes.migration.migration import ATCTContentMigrator
from plone.app.contenttypes.migration.migration import migrate


class PloneFormGenMigrator(ATCTContentMigrator):
    """Migrator for PFG to easyform"""

    src_portal_type = 'FormFolder'
    src_meta_type = 'FormFolder'
    dst_portal_type = 'EasyForm'
    dst_meta_type = None  # not used

    def migrate_pfg_using_json(self):
        data = self.get_exported_form()
        self.create_easyform_from_json(data)

    def get_data_of_exported_form(self):
        # TODO: Do what the export does!
        # self.old is the PFG instance
        pass

    def create_easyform_from_json(self, data):
        # TODO: Do what the import does!
        # self.new is a new easyform instance
        pass


def migrate_ploneformgen(context=None):
    portal = api.portal.get()
    return migrate(portal, PloneFormGenMigrator)
