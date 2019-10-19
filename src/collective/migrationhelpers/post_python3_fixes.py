# -*- coding: utf-8 -*-
from ComputedAttribute import ComputedAttribute
from plone import api
from plone.app.portlets.portlets.navigation import Renderer
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.globalrequest import getRequest

import logging

log = logging.getLogger(__name__)


def fix_event_indexes(context=None):
    # Metadata on brains is still old DateTime
    for brain in api.content.find(portal_type='Event'):
        obj = brain.getObject()
        obj.reindexObject()


def fix_searchable_text(context=None):
    # Fix bytes in opkapiindex
    # See https://github.com/plone/Products.CMFPlone/issues/2905
    from Products.ZCTextIndex.interfaces import IZCTextIndex
    from Products.ZCTextIndex.interfaces import ILexicon
    catalog = api.portal.get_tool('portal_catalog')
    zctextindex = catalog._catalog.indexes['SearchableText']
    opkapiindex = zctextindex.index
    values = opkapiindex._docwords.values()
    first_item = values[0]
    if isinstance(first_item, bytes):
        log.info('Rebuilding ZCTextIndexes. First item is a byte:')
        log.info(first_item)
        lexica = [i for i in catalog.values() if ILexicon.providedBy(i)]
        for lexicon in lexica:
            lexicon.clear()

        indexes = [i for i in catalog.Indexes.objectValues()
                   if IZCTextIndex.providedBy(i)]
        for index in indexes:
            try:
                index.clear()
            except AttributeError as e:
                log.info(e)
            log.info('rebuilding {}'.format(index.__name__))
            catalog._catalog.reindexIndex(index.__name__, getRequest())
    else:
        log.info('Not rebuilding ZCTextIndexes. First item is not bytes:')
        log.info(first_item)


def fix_portlets(context=None):
    """Fix navigation_portlet (has ComputedValue for portal instead of a UUID)
    """
    catalog = api.portal.get_tool('portal_catalog')
    for brain in catalog.getAllBrains():
        try:
            obj = brain.getObject()
        except KeyError:
            log.info('Broken brain for {}'.format(brain.getPath()))
        fix_navigation_portlet_for(obj)
    portal = api.portal.get()
    fix_navigation_portlet_for(portal)


def fix_navigation_portlet_for(obj):
    request = getRequest()
    view = obj.restrictedTraverse('@@view')
    for manager_name in ['plone.leftcolumn', 'plone.rightcolumn']:
        manager = queryUtility(IPortletManager, name=manager_name, context=obj)
        if not manager:
            continue
        mappings = queryMultiAdapter((obj, manager), IPortletAssignmentMapping)
        if not mappings:
            continue
        for key, assignment in mappings.items():
            renderer = queryMultiAdapter(
                (obj, request, view, manager, assignment), IPortletRenderer)
            if not renderer:
                continue
            if isinstance(renderer, Renderer) and isinstance(assignment.root_uid, ComputedAttribute):  # noqa: E501:
                # We have a navigation-portlet!
                assignment.root_uid = None
                log.info('Reset root of navigation-portlet assigned at {} in {}'.format(obj.absolute_url(), manager_name))  # noqa: E501
                log.info('You may need to configure it manually at {}/manage-portlets'.format(obj.absolute_url()))  # noqa: E501
