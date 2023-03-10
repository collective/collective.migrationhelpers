# -*- coding: utf-8 -*-
from ComputedAttribute import ComputedAttribute
from plone import api
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.registry.interfaces import IRegistry
from Products.ZCatalog.ProgressHandler import ZLogHandler
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
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


def fix_searchable_text(context=None, name='portal_catalog'):
    # Fix bytes in opkapiindex
    # See https://github.com/plone/Products.CMFPlone/issues/2905
    from Products.ZCTextIndex.interfaces import IZCTextIndex
    from Products.ZCTextIndex.interfaces import ILexicon
    catalog = api.portal.get_tool(name)
    zctextindex = catalog._catalog.indexes['SearchableText']
    opkapiindex = zctextindex.index
    values = opkapiindex._docwords.values()
    if len(values):
        first_item = values[0]
    else:
        first_item = None
    if first_item is None or isinstance(first_item, bytes):
        log.info('Rebuilding ZCTextIndexes. First item is a byte or mising:')
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
            # If we have an unknown lexicon use the most recently added one
            lex_id = getattr(index, 'lexicon_id', None)
            if lex_id and len(lexica) and getattr(catalog, lex_id, None) is None:
                new_lex_id = lexica[-1].getId()
                log.warn(f'Replacing bad lexicon {lex_id} with {new_lex_id} in {index.__name__}')
                index.lexicon_id = new_lex_id
        index_names = [index.__name__ for index in indexes]
        log.info('rebuilding indexes: {}'.format(', '.join(index_names)))
        catalog.reindexIndex(index_names, getRequest(), pghandler=ZLogHandler(1000))
    else:
        log.info('Not rebuilding ZCTextIndexes. First item is not bytes:')
        log.info(first_item)


def fix_portlets(context=None):
    """Fix portlets that use ComputedValue for path-storage instead of a UUID.
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


def fix_portlets_for(obj, managers=('plone.leftcolumn',
                                    'plone.rightcolumn',
                                    'plone.footerportlets')):
    """Fix portlets for a certain object."""
    attrs_to_fix = [
        'root_uid',
        'search_base_uid',
        'uid',
    ]
    for manager_name in managers:
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


def fix_discussions(context=None):
    """Fix conversations that still have the old AT content as __parent__"""
    portal = api.portal.get()
    log.info('Fixing conversations...')

    def fix_at_parent_for_discussions(obj, path):
        annotations = IAnnotations(obj, None)
        if not annotations:
            return
        if 'plone.app.discussion:conversation' not in annotations.keys():
            return
        conversation = annotations['plone.app.discussion:conversation']
        if 'broken' in str(conversation.__parent__):
            conversation.__parent__ = obj
            log.info(f'Fix conversation for {obj.absolute_url()}')
        else:
            log.info(f'Conversation parent ok: {conversation.__parent__}')

    portal.ZopeFindAndApply(
        portal, search_sub=True, apply_func=fix_at_parent_for_discussions
    )
    log.info('Fixed conversations!')


def fix_registry(context=None):
    """Remove registry-records where the interface is no longer there."""
    registry = getUtility(IRegistry)
    keys = [i for i in registry.records.keys()]
    for key in keys:
        record = registry.records[key]
        if not record.field.interface:
            # That's fine...
            continue
        try:
            iface = record.field.interface()
        except TypeError:
            # That's also fine...
            continue
        if 'broken' in str(iface):
            log.info(f'Removing broken record {key}')
            del registry.records[key]


def rebuild_relations(context=None):
    """Export all valid reations from the relation-catalog, purge the relation-catalog
    (and cleanup the intid-catalog) and restores all valid relations."""
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
