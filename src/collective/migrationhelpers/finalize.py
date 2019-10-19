# -*- coding: utf-8 -*-
from plone import api
from plone.app.upgrade.utils import loadMigrationProfile

DEFAULT_PROFILE = 'profile-myaddon.name:default'


def finalize(context=None):
    """This is run in Plone 5.2 on Python 3
    """
    portal_setup = api.portal.get_tool('portal_setup')

    # enable behaviors
    loadMigrationProfile(
        portal_setup,
        DEFAULT_PROFILE,
        steps=['typeinfo', 'catalog', 'plone.app.registry'],
        )

    portal_setup.runAllImportStepsFromProfile(
        'profile-plone.app.registry:default', purge_old=False)

    # set dropdown-navigation depth to 3
    api.portal.set_registry_record('plone.navigation_depth', 3)
