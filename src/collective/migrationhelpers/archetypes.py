# -*- coding: UTF-8 -*-
from plone import api

import logging

log = logging.getLogger(__name__)


def remove_archetypes(context=None):
    portal = api.portal.get()

    # remove obsolete AT tools
    tools = [
        'portal_languages',
        'portal_tinymce',
        'kupu_library_tool',
        'portal_factory',
        'portal_atct',
        'uid_catalog',
        'archetype_tool',
        'reference_catalog',
        'portal_metadata',
    ]
    for tool in tools:
        if tool not in portal.keys():
            log.info('Tool {} not found'.format(tool))
            continue
        try:
            portal.manage_delObjects([tool])
            log.info('Deleted {}'.format(tool))
        except Exception as e:
            log.info(u'Problem removing {}: {}'.format(tool, e))
            try:
                log.info(u'Fallback to remove without permission_checks')
                portal._delObject(tool)
                log.info('Deleted {}'.format(tool))
            except Exception as e:
                log.info(u'Another problem removing {}: {}'.format(tool, e))


def fix_conversations(context=None):
    """Conversations from plone.app.discussion may still have the old
    Archetypes content as __parent__ instead of the new migrated DX-content.
    # TODO: Fix in plone.app.contenttypes?
    """
    from Acquisition import aq_base
    portal = api.portal.get()

    def fix_conversation_parent(obj, path):
        annotations = getattr(aq_base(obj), '__annotations__', None)
        if not annotations:
            return
        if 'plone.app.discussion:conversation' not in annotations.keys():
            return
        conversation = annotations['plone.app.discussion:conversation']
        if 'broken' in conversation.__parent__.__repr__() or obj != conversation.__parent__:
            conversation.__parent__ = obj
            log.info(u'Fix conversation for {}'.format(obj.absolute_url()))
    portal.ZopeFindAndApply(portal, search_sub=True, apply_func=fix_conversation_parent)
