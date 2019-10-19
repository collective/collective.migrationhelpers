# -*- coding: utf-8 -*-
from plone import api

import logging

log = logging.getLogger(__name__)


def delete_items_larger_than_1mb(context=None):
    """Delete all items that are larger than 1MB
    and all imported build-reports for phoenics-software.

    Never use in production!!!
    """
    catalog = api.portal.get_tool('portal_catalog')
    for brain in catalog.unrestrictedSearchResults(
            portal_type=[
                'File',
                'Image',
            ]):
        size = brain.getObjSize
        if "MB" in size:
            size = float(size.split()[0])
            if size > 1:
                log.info(u'Deleting {}'.format(brain.getPath()))
                api.content.delete(
                    brain.getObject(), check_linkintegrity=False)


def remove_all_revisions(context=None):
    """Remove all revisions.
    After packing the DB this could significantly shrink its size.
    """
    hs = api.portal.get_tool('portal_historiesstorage')
    zvcr = hs.zvc_repo
    zvcr._histories.clear()
    storage = hs._shadowStorage
    storage._storage.clear()


def disable_theme(context=None):
    """Disable a custom diazo theme and enable sunburst.
    Useful for cleaning up a site in Plone 4
    """
    THEME_NAME = 'custom.theme'
    from plone.app.theming.utils import applyTheme
    portal_skins = api.portal.get_tool('portal_skins')
    qi = api.portal.get_tool('portal_quickinstaller')
    log.info('remove {}'.format(THEME_NAME))
    if qi.isProductInstalled(THEME_NAME):
        qi.uninstallProducts([THEME_NAME])
    applyTheme(None)
    portal_skins.default_skin = 'Sunburst Theme'
    if THEME_NAME in portal_skins.getSkinSelections():
        portal_skins.manage_skinLayers([THEME_NAME], del_skin=True)
