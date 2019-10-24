# -*- coding: utf-8 -*-
from plone import api

import logging

log = logging.getLogger(__name__)


def delete_large_items(context=None, max_size=1):
    """Delete all items that are larger than 1 MB.
    """
    catalog = api.portal.get_tool('portal_catalog')
    for brain in catalog(portal_type=['File', 'Image']):
        size = brain.getObjSize
        if "MB" in size:
            size = float(size.split()[0])
            if size > max_size:
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
    if qi.isProductInstalled(THEME_NAME):
        log.info('Uninstalling {}'.format(THEME_NAME))
        qi.uninstallProducts([THEME_NAME])
    log.info('Disabling all diazo themes')
    applyTheme(None)
    log.info('Enabled Sunburst Theme')
    portal_skins.default_skin = 'Sunburst Theme'
    if THEME_NAME in portal_skins.getSkinSelections():
        portal_skins.manage_skinLayers([THEME_NAME], del_skin=True)
