# -*- coding: UTF-8 -*-
from plone import api

import logging
import transaction

log = logging.getLogger(__name__)


def remove_utility(iface):
    """Remove an interface from all utility and adapter registrations.

    There are several places where an interface like IKSSRegistry can have lodged itself.
    We need to find them all, otherwise you are not even able to see
    the ZMI when going to Plone 5.2.
    """
    portal = api.portal.get()
    sm = portal.getSiteManager()

    for component in (sm.utilities, sm.adapters):
        subscribers = component._subscribers
        if subscribers:
            subscribers = subscribers[0]
            if iface in subscribers:
                del subscribers[iface]
                logging.info(u'Unregistering subscriber for %s', iface)

        adapters = component._adapters
        if adapters:
            adapters = adapters[0]
            if iface in adapters:
                del adapters[iface]
                logging.info(u'Unregistering adapter for %s', iface)

        provided = component._provided
        if iface in provided:
            del provided[iface]
            logging.info(u'Unregistering provided for %s', iface)

        # Mark the component as changed, even when maybe there was no change.
        # There is no harm in a technically unneeded persistent change here.
        component._p_changed = True

    for registrations in (sm._utility_registrations, sm._adapter_registrations):
        reg_keys = registrations.keys()
        for reg_key in reg_keys:
            # registration key is (interface, name)
            # Note that the interface can probably be there under several names.
            if iface is reg_key[0]:
                del registrations[reg_key]
                logging.info(u'Unregistering registration for %s', reg_key)

    transaction.commit()


def remove_utilities(context=None):
    """Example that removes collective.zipfiletransport
    """
    from collective.zipfiletransport.utilities.interfaces import IZipFileTransportUtility  # noqa: E501

    remove_utility(IZipFileTransportUtility)


def remove_kss(context=None):
    """Example that removes portal_kss and related utilities

    This code works for me when I run it in Plone 4.3,
    on a site that originally started at Plone 3 (or maybe even earlier).

    There are several places where IKSSRegistry can have lodged itself.
    We need to find them all, otherwise you are not even able to see
    the ZMI when going to Plone 5.2.

    The same might be true for other utilities,
    like the IZipFileTransportUtility above.
    """
    portal = api.portal.get()
    if 'portal_kss' in portal:
        portal.manage_delObjects(['portal_kss'])
        log.info(u'Removed portal_kss tool.')

    try:
        from Products.ResourceRegistries.interfaces import IKSSRegistry
    except ImportError:
        return
    remove_utility(IKSSRegistry)


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
        remove_utility(IPortalTypedFolderishDescriptor)
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
