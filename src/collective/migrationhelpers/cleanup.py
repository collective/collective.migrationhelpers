# -*- coding: utf-8 -*-
from plone import api

import logging
import transaction

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


def trim_content(
    context=None, percent=95, types_to_keep=None, folderish_types_to_delete=None
):
    """Remove 95% of all content leaving at least one item for each.
    Keep all folderish items unless they are specified

    Deleting a lot of content takes time:
    * Plone can delete about 8 items per second (folderish itmes take longer)
    * Deleting 500 items takes 1 minute.
    * Deleting 10.000 item takes 20 minutes.
    """
    if not types_to_keep:
        types_to_keep = ['Folder', 'Discussion Item']
    if not folderish_types_to_delete:
        folderish_types_to_delete = ['FormFolder', 'HelpCenter', 'Collage']

    portal_types = api.portal.get_tool('portal_types')
    for portal_type in portal_types:
        if types_to_keep and portal_type in types_to_keep:
            log.info(u'Keeping items of type {}'.format(portal_type))
            continue

        brains = api.content.find(portal_type=portal_type)
        total_amount = len(brains)
        if total_amount == 0:
            continue
        amount_to_delete = float(percent) / 100 * total_amount
        amount_to_delete = int(amount_to_delete)
        if amount_to_delete >= total_amount:
            amount_to_delete = total_amount - 1

        log.info(u'Deleting {} {}'.format(amount_to_delete, portal_type))
        for index, brain in enumerate(brains):
            if index >= amount_to_delete:
                log.info(u'Done deleting {} {}'.format(index, portal_type))
                break
            if brain.is_folderish and portal_type not in folderish_types_to_delete:
                log.info(u'Not deleting folderish type {}!'.format(portal_type))
                break
            obj = brain.getObject()
            try:
                api.content.delete(obj, check_linkintegrity=False)
            except Exception as e:
                log.info(e)
            if index and not index % 100:
                log.info(u'Deleted {} {} ...'.format(index, portal_type))
        log.info(u'Committing...')
        transaction.commit()
    log.info(u'Finished!')
    return u'Finished!'
