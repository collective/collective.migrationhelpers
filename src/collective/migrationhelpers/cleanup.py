# -*- coding: utf-8 -*-
from plone import api

import logging
import transaction

log = logging.getLogger(__name__)


def delete_large_items(context=None, max_size=1):
    """Delete all items that are larger than 1 MB.
    """
    catalog = api.portal.get_tool('portal_catalog')
    for brain in catalog.unrestrictedSearchResults(portal_type=['File', 'Image']):
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
    * Plone can delete between 8 and 80 items per second (it depends...)
    * Deleting 500 items can take between 5 seconds and 1 minute.
    * Deleting 10.000 items can take 20 minutes.

    Deleting gets slower over time so when you need to delete more than
    10.000 item you should consider deleting them in batches.

    Never ever run this in production unless you need a new job.
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
        # First get all brains.  If we start getting them lazily and meanwhile
        # delete objects, we may run into a KeyError getting the next brain.
        # Okay, this does not help in my case, but seems good anyway.
        brains = list(brains)[:amount_to_delete]
        index = 0
        for index, brain in enumerate(brains):
            if brain.is_folderish and portal_type not in folderish_types_to_delete:
                log.info(u'Not deleting folderish type {}!'.format(portal_type))
                break
            try:
                obj = brain.getObject()
            except Exception as e:
                # I have had this in one site, and not even brain.getPath worked.
                # But I could get all objects as long as I was not busy deleting any.
                log.info(e)
                # log.warning(u'Not deleting portal_type {} {} because getObject failed.'.format(portal_type, index))
                # continue
            else:
                try:
                    api.content.delete(obj, check_linkintegrity=False)
                except Exception as e:
                    log.info(e)
            if index and not index % 100:
                log.info(u'Deleting portal_type {}: {} ...'.format(portal_type, index))
            if index and not index % 1000:
                log.info(u'Creating transaction savepoint...')
                transaction.savepoint()
        log.info(u'Done deleting {} {}'.format(index, portal_type))
        log.info(u'Committing...')
        transaction.commit()
    log.info(u'Finished!')
    return u'Finished!'
