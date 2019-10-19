# -*- coding: utf-8 -*-
from plone import api
from zope.component import getGlobalSiteManager

import logging

log = logging.getLogger(__name__)


def disable_subscriber(handler, iface, event):
    gsm = getGlobalSiteManager()
    gsm.unregisterHandler(handler, (iface, event))


def enable_subscriber(handler, iface, event):
    gsm = getGlobalSiteManager()
    gsm.registerHandler(handler, (iface, event))


def example_with_disabled_subscriber(context=None):
    """
    Example for a subscriber in:
    plone/app/linkintegrity/configure.zcml:

    <subscriber
        for="plone.app.relationfield.interfaces.IDexterityHasRelations
             zope.lifecycleevent.interfaces.IObjectModifiedEvent"
        handler=".handlers.modifiedContent" />
    """
    from plone.app.linkintegrity.handlers import modifiedContent
    from plone.app.relationfield.interfaces import IDexterityHasRelations
    from zope.lifecycleevent.interfaces import IObjectModifiedEvent
    disable_subscriber(
        modifiedContent, (IDexterityHasRelations, IObjectModifiedEvent))
    # Do something here...
    enable_subscriber(
        modifiedContent, (IDexterityHasRelations, IObjectModifiedEvent))


def rebuild_catalog_without_indexing_blobs(context=None):
    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()
    log.info('rebuilding catalog')
    catalog = api.portal.get_tool('portal_catalog')
    catalog.clearFindAndRebuild()
    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()
    return 'Done'


def pack_database(context=None):
    """Pack the database"""
    portal = api.portal.get()
    app = portal.__parent__
    db = app._p_jar.db()
    db.pack(days=0)


def pass_fn(*args, **kwargs):
    """Empty function used for patching."""
    pass


def patch_indexing_at_blobs():
    from plone.app.blob.content import ATBlob
    from Products.contentmigration.utils import patch
    patch(ATBlob, 'getIndexValue', pass_fn)


def unpatch_indexing_at_blobs():
    from Products.contentmigration.utils import undoPatch
    from plone.app.blob.content import ATBlob
    undoPatch(ATBlob, 'getIndexValue')


def patch_indexing_dx_blobs():
    from Products.contentmigration.utils import patch
    from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
    # from plone.app.blob.content import ATBlob
    patch(ZCTextIndex, 'index_object', patched_index_object)


def unpatch_indexing_dx_blobs():
    from Products.contentmigration.utils import undoPatch
    from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
    undoPatch(ZCTextIndex, 'index_object')


def patched_index_object(self, documentId, obj, threshold=None):
    from plone.app.textfield.interfaces import TransformError
    from Products.PluginIndexes.common import safe_callable
    """Wrapper for  index_doc()  handling indexing of multiple attributes.
    Enter the document with the specified documentId in the index
    under the terms extracted from the indexed text attributes,
    each of which should yield either a string or a list of
    strings (Unicode or otherwise) to be passed to index_doc().
    """

    # patch: ignore Files
    if getattr(obj, 'portal_type', None) == 'File':
        return 0
    # TODO we currently ignore subtransaction threshold

    # needed for backward compatibility
    fields = getattr(self, '_indexed_attrs', [self._fieldname])

    all_texts = []
    for attr in fields:
        try:
            text = getattr(obj, attr, None)
        except TransformError as e:
            log.warn('TransformError accessing {0} of {1}: {2}'.format(attr, obj.absolute_url_path(), e))  # noqa: E501
            continue
        if text is None:
            continue
        if safe_callable(text):
            text = text()
        if text is not None:
            if isinstance(text, (list, tuple, set)):
                all_texts.extend(text)
            else:
                all_texts.append(text)

    # Check that we're sending only strings
    all_texts = [t for t in all_texts if isinstance(t, basestring)]
    if all_texts:
        return self.index.index_doc(documentId, all_texts)
    return 0
