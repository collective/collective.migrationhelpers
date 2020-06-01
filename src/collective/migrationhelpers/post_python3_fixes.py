# -*- coding: utf-8 -*-
from ComputedAttribute import ComputedAttribute
from plone import api
from persistent.list import PersistentList
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zc.relation.interfaces import ICatalog
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.globalrequest import getRequest
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified
from z3c.relationfield import RelationValue

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
    portal = api.portal.get()
    fix_portlets_for(portal)
    for brain in catalog.getAllBrains():
        try:
            obj = brain.getObject()
        except KeyError:
            log.info('Broken brain for {}'.format(brain.getPath()))
            continue
        fix_portlets_for(obj)


def fix_portlets_for(obj):
    attrs_to_fix = [
        'root_uid',
        'search_base_uid',
        'uid',
    ]
    if getattr(obj.aq_base, 'getLayout', None) is not None and obj.getLayout() is not None:
        view = obj.restrictedTraverse(obj.getLayout())
    else:
        view = obj.restrictedTraverse('@@view')
    for manager_name in ['plone.leftcolumn', 'plone.rightcolumn', 'plone.footerportlets']:
        manager = queryUtility(IPortletManager, name=manager_name, context=obj)
        if not manager:
            continue
        mappings = queryMultiAdapter((obj, manager), IPortletAssignmentMapping)
        if not mappings:
            continue
        for key, assignment in mappings.items():
            for attr in attrs_to_fix:
                if getattr(assignment, attr, None) is not None and isinstance(getattr(assignment, attr), ComputedAttribute):
                    setattr(assignment, attr, None)
                    log.info('Reset {} for portlet {} assigned at {} in {}'.format(attr, key, obj.absolute_url(), manager_name))  # noqa: E501
                    log.info('You may need to configure it manually at {}/@@manage-portlets'.format(obj.absolute_url()))  # noqa: E501


def get_all_relations():
    portal = api.portal.get()
    results = []

    # Get all data from relation_catalog
    relation_catalog = getUtility(ICatalog)
    for rel in relation_catalog.findRelations():
        if rel.from_object and rel.to_object:
            results.append({
                'from_uuid': rel.from_object.UID(),
                'to_uuid': rel.to_object.UID(),
                'relationship': rel.from_attribute,
            })
    return results


def rebuild_relations(context=None):
    from collective.relationhelpers import api as relapi
    relapi.rebuild_relations()


def export_relations(context=None):
    """Export all relations as a json file all_relations.json in you buildout directory."""
    from collective.relationhelpers import api as relapi
    relapi.export_relations()


def restore_relations(all_relations=None):
    """Recreate relations from a annotation on the portal or a list of dicts
    (e.g. restored from the json-file created by export_relations).
    This works fine for all kinds of relations, RelationList- or RelationChoice-fields
    (including the default field "Related Items") as well as for linkintegrity-relations
    and relations between working-copies."""
    from collective.relationhelpers import api as relapi
    relapi.restore_relations(all_relations=all_relations)


def cleanup_intids(context=None):
    """Purge all RelationValues and all references to broken objects from the IntId catalog."""
    from collective.relationhelpers import api as relapi
    relapi.cleanup_intids()

