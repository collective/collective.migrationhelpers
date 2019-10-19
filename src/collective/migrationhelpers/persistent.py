# -*- coding: UTF-8 -*-
from plone import api

import logging
import transaction

log = logging.getLogger(__name__)


def remove_utilities(context=None):
    """Example that removes collective.zipfiletransport
    """
    portal = api.portal.get()

    from collective.zipfiletransport.utilities.interfaces import IZipFileTransportUtility  # noqa: E501
    sm = portal.getSiteManager()

    if IZipFileTransportUtility in sm.utilities._subscribers[0]:
        del sm.utilities._subscribers[0][IZipFileTransportUtility]
        log.info(u'Unregistering subscriber for IZipFileTransportUtility')

    if IZipFileTransportUtility in sm.utilities._adapters[0]:
        del sm.utilities._adapters[0][IZipFileTransportUtility]
        log.info(u'Unregistering adapter for IZipFileTransportUtility')

    sm.utilities._p_changed = True
    transaction.commit()


def _unregisterUtility(portal):
    """Example that removes p4a.subtyper
    """
    try:
        from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor
        HAS_P4A = True
    except ImportError:
        HAS_P4A = False

    sm = portal.getSiteManager()
    if HAS_P4A:
        util = sm.queryUtility(
            IPortalTypedFolderishDescriptor, u'collective.easyslideshow.slideshow')
        sm.unregisterUtility(
            util,
            IPortalTypedFolderishDescriptor,
            name=u'collective.easyslideshow.slideshow')
        if IPortalTypedFolderishDescriptor in sm.utilities._subscribers[0]:
            del sm.utilities._subscribers[0][IPortalTypedFolderishDescriptor]
    # reuse code from collective.lineage
    try:
        from collective.lineage.upgrades import removeP4A
        removeP4A(portal)
    except ImportError:
        pass


def remove_vocabularies(setup):
    """Example that removes stuff from LinguaPlone
    """
    from plone.i18n.locales.interfaces import IContentLanguageAvailability
    from plone.i18n.locales.interfaces import IMetadataLanguageAvailability

    portal = api.portal.get()
    sm = portal.getSiteManager()

    # remove subscriber
    if IContentLanguageAvailability in sm.utilities._subscribers[0]:
        del sm.utilities._subscribers[0][IContentLanguageAvailability]
        log.info(u'Unregistering subscriber for IContentLanguageAvailability')
    if IMetadataLanguageAvailability in sm.utilities._subscribers[0]:
        del sm.utilities._subscribers[0][IMetadataLanguageAvailability]
        log.info(u'Unregistering subscriber for IMetadataLanguageAvailability')

    # remove adapter
    if IContentLanguageAvailability in sm.utilities._adapters[0]:
        del sm.utilities._adapters[0][IContentLanguageAvailability]
        log.info(u'Unregistering adapter for IContentLanguageAvailability')
    if IMetadataLanguageAvailability in sm.utilities._adapters[0]:
        del sm.utilities._adapters[0][IMetadataLanguageAvailability]
        log.info(u'Unregistering adapter for IMetadataLanguageAvailability')

    # make sure it sticks
    sm.utilities._p_changed = True
    transaction.commit()
