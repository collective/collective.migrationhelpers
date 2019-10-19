# -*- coding: utf-8 -*-
from OFS.CopySupport import CopyError
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zExceptions import BadRequest
from zope.globalrequest import getRequest

import logging
import transaction

log = logging.getLogger(__name__)

CONTAINER_TYPES = ['Folder', 'Section']
DEFAULT_LANG = 'de'
# might be refactored to work wirth lists of other langs
OTHER_LANG = 'en'


def cleanup_content_for_pam(setup=None):
    """Set languages, add and link translations so that we can migrate to pam
    Run this Plone 4.3.x

    Warning: This is pretty crazy and does a lot of educated guessing.
    It worked fine for a site with 'de' and 'en' where editors made a real mess
    of the structure of multi-language content.
    The problem is tries to solve is that folder in LP can contain content
    in both languages instead of having one folde for each language.

    Use at you own risk!
    """
    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()

    portal = api.portal.get()
    unregister_broken_persistent_components(portal)

    # set language of containers without lang to a sane value
    for brain in api.content.find(portal_type=CONTAINER_TYPES, Language=''):
        obj = brain.getObject()
        content = obj.contentValues()
        lang = set([i.Language() for i in content])
        if lang and len(lang) == 1:
            lang = lang.pop()
            if not lang:
                lang = DEFAULT_LANG
        else:
            lang = DEFAULT_LANG
        obj.setLanguage(lang)
        log.info('Set language of %s to %s' % (obj.absolute_url_path(), lang))
        obj.reindexObject(idxs=['Language'])
    transaction.commit()

    # add missing translations for parents of english content
    brains = [i for i in api.content.find(Language=OTHER_LANG)]
    done = []
    for brain in brains:
        try:
            if brain.getPath() in done:
                continue
            obj = brain.getObject()
        except KeyError:
            continue
        if IPloneSiteRoot.providedBy(obj) or INavigationRoot.providedBy(obj):
            continue
        parent = obj.__parent__
        if IPloneSiteRoot.providedBy(parent):
            continue

        if parent.Language() == OTHER_LANG:
            continue

        if parent.hasTranslation(OTHER_LANG):
            translation = parent.getTranslation(OTHER_LANG)
            if translation.absolute_url_path() != parent.absolute_url_path():
                log.info('Parent container has a translation. Moving %s to %s' % (obj.absolute_url_path(), translation.absolute_url_path()))  # noqa: E501
                api.content.move(source=obj, target=translation, safe_id=True)
            continue

        content = parent.contentValues()
        if content and DEFAULT_LANG not in [i.Language() for i in content]:
            parent.setLanguage(OTHER_LANG)
            log.info('Switched container with english-only content to english. Please link translation of %s!' % parent.absolute_url_path())  # noqa: E501
            obj.reindexObject(idxs=['Language'])
            for child_obj in content:
                if child_obj.Language() != OTHER_LANG:
                    child_obj.setLanguage(OTHER_LANG)
                    child_obj.reindexObject(idxs=['Language'])
            continue

        if not parent.Language():
            log.error('Crap! Container without lang: %s' % parent.absolute_url_path())  # noqa: E501
            continue

        if parent.getId().endswith('-' + OTHER_LANG):
            log.error('Crap! Weird things at: %s' % parent.absolute_url_path())
            continue

        try:
            translation = parent.addTranslation(OTHER_LANG)
        except CopyError:
            log.info('Could not create %s translation of %s' % (
                OTHER_LANG, parent.absolute_url_path()))  # noqa: E501
            pass
        done.append('/'.join(parent.getPhysicalPath()))
        log.info('Add translation of %s: %s' % (
            parent.absolute_url_path(), translation))
    transaction.commit()

    brains = [i for i in api.content.find(Language=DEFAULT_LANG)]
    done = []
    for brain in brains:
        try:
            if brain.getPath() in done:
                continue
            obj = brain.getObject()
        except KeyError:
            continue
        if IPloneSiteRoot.providedBy(obj) or INavigationRoot.providedBy(obj):
            continue
        parent = obj.__parent__
        if IPloneSiteRoot.providedBy(parent):
            continue
        if parent.Language() == DEFAULT_LANG:
            continue

        if parent.hasTranslation(DEFAULT_LANG):
            log.error('Crap! Weird things at: %s' % parent.absolute_url_path())
            continue

        if not parent.Language():
            parent.setLanguage(DEFAULT_LANG)
            log.info('Switched container to DEFAULT_LANG: %s!' % parent.absolute_url_path())  # noqa: E501
            obj.reindexObject(idxs=['Language'])
            continue

        content = parent.contentValues()
        if OTHER_LANG not in [i.Language() for i in content]:
            parent.setLanguage(DEFAULT_LANG)
            log.info('Switched container to german: %s!' % parent.absolute_url_path())  # noqa: E501
            obj.reindexObject(idxs=['Language'])
            for child_obj in content:
                if child_obj.Language() != DEFAULT_LANG:
                    child_obj.setLanguage(DEFAULT_LANG)
                    child_obj.reindexObject(idxs=['Language'])
            continue

        if parent.getId().endswith('-en'):
            log.error('Crap! Weird things at: %s' % parent.absolute_url_path())

    # set language of all neutral content to DEFAULT_LANG
    transaction.commit()
    for brain in api.content.find(Language=''):
        obj = brain.getObject()
        if not obj.Language():
            if not obj.isCanonical() and DEFAULT_LANG in obj.getTranslations():
                lang = OTHER_LANG
            else:
                lang = DEFAULT_LANG
            obj.setLanguage(lang)
            obj.reindexObject(idxs=['Language'])
            log.info('Switched %s to %s' % (obj.absolute_url_path(), lang))

    # log non-default content with different languages than their parents
    find_content_with_wrong_language(portal)
    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()


def install_pam(setup=None):
    """Run this Plone 4.3.x
    Install pam - we still use Archetypes, so also archetypes.multilingual
    """
    qi = api.portal.get_tool('portal_quickinstaller')
    portal = api.portal.get()

    if not qi.isProductInstalled('plone.app.multilingual'):
        qi.installProduct('plone.app.multilingual')
        qi.installProduct('archetypes.multilingual')
        from plone.app.multilingual.browser.setup import SetupMultilingualSite
        ml_setup_tool = SetupMultilingualSite()
        ml_setup_tool.setupSite(portal)


def migrate_to_pam(setup=None):
    """Run this Plone 4.3.x
    Migrate LinguaPlone to plone.app.multilingual
    This mostly uses the migration that is builtin in plone.app.multilingual
    """

    patch_indexing_at_blobs()
    patch_indexing_dx_blobs()

    qi = api.portal.get_tool('portal_quickinstaller')
    portal_properties = api.portal.get_tool('portal_properties')
    portal = api.portal.get()

    # again set the language of containers without lang to a sane value
    # This information gets lost somehow
    for brain in api.content.find(
            portal_type=['Folder', 'Section'], Language=''):
        obj = brain.getObject()
        content = obj.contentValues()
        lang = set([i.Language() for i in content])
        if lang and len(lang) == 1:
            lang = lang.pop()
            if not lang:
                lang = DEFAULT_LANG
        else:
            lang = DEFAULT_LANG
        obj.setLanguage(lang)
        log.info('Set language of %s to %s' % (obj.absolute_url_path(), lang))
        obj.reindexObject(idxs=['Language'])

    # run all lp migration-steps
    request = getRequest()
    lp_relocate = api.content.get_view('relocate-content', portal, request)
    lp_relocate.blacklist = []
    lp_relocate.step1andstep2()
    transaction.commit()
    lp_relocate.step3()
    transaction.commit()
    transfer_lp_catalog = api.content.get_view(
        'transfer-lp-catalog', portal, request)
    transfer_lp_catalog()
    transaction.commit()

    # remove LinguaPlone
    if qi.isProductInstalled('LinguaPlone'):
        qi.uninstallProducts(['LinguaPlone'])
    try:
        portal_properties.manage_delObjects(['linguaplone_properties'])
    except BadRequest:
        pass
    # run our LP-uninstall-profile
    setup.runAllImportStepsFromProfile(
        'profile-example.migration:to_1005', purge_old=False)
    unpatch_indexing_at_blobs()
    unpatch_indexing_dx_blobs()


def remove_vocabularies(setup=None):
    from plone.i18n.locales.interfaces import IContentLanguageAvailability
    from plone.i18n.locales.interfaces import IMetadataLanguageAvailability
    from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor
    portal = api.portal.get()
    sm = portal.getSiteManager()

    if IContentLanguageAvailability in sm.utilities._subscribers[0]:
        del sm.utilities._subscribers[0][IContentLanguageAvailability]
        log.info(u'Unregistering subscriber for IContentLanguageAvailability')
    if IMetadataLanguageAvailability in sm.utilities._subscribers[0]:
        del sm.utilities._subscribers[0][IMetadataLanguageAvailability]
        log.info(u'Unregistering subscriber for IMetadataLanguageAvailability')

    if IMetadataLanguageAvailability in sm.utilities._adapters[0]:
        del sm.utilities._adapters[0][IMetadataLanguageAvailability]
        log.info(u'Unregistering adapter for IMetadataLanguageAvailability')
    if IContentLanguageAvailability in sm.utilities._adapters[0]:
        del sm.utilities._adapters[0][IContentLanguageAvailability]
        log.info(u'Unregistering adapter for IContentLanguageAvailability')

    if IPortalTypedFolderishDescriptor in sm.utilities._adapters[0]:
        del sm.utilities._adapters[0][IPortalTypedFolderishDescriptor]
        log.info(u'Unregistering adapter for IPortalTypedFolderishDescriptor')
    sm.utilities._p_changed = True
    transaction.commit()


def unregister_broken_persistent_components(portal):
    sm = portal.getSiteManager()

    for item in sm._utility_registrations.items():
        if hasattr(item[1][0], '__Broken_state__'):
            # unregisterUtility(component, provided, name)
            # See: five.localsitemanager.registry.PersistentComponents.unregisterUtility  # noqa: E501
            log.info(u"Unregistering component {0}".format(item))
            sm.unregisterUtility(item[1][0], item[0][0], item[0][1])


def find_content_with_wrong_language(content):
    """log non-default content with different languages than their parents
    Used to make sure we cleaned up everything.
    In part stolen and adapted from
    plone.app.multilingual.browser.migrator.moveContentToProperRLF.findContent
    """
    # only handle portal content
    from plone.dexterity.interfaces import IDexterityContent
    from Products.Archetypes.interfaces import IBaseObject
    from Acquisition import aq_base
    from Acquisition import aq_parent
    try:
        from Products.LinguaPlone.interfaces import ITranslatable
    except ImportError:
        from plone.app.multilingual.interfaces import ITranslatable

    if not IDexterityContent.providedBy(content)\
            and not IBaseObject.providedBy(content)\
            and not IPloneSiteRoot.providedBy(content):
        return
    if hasattr(aq_base(content), 'objectIds'):
        for id in content.objectIds():
            find_content_with_wrong_language(getattr(content, id))
    if ITranslatable.providedBy(content):
        # The content parent has the same language?
        if not IPloneSiteRoot.providedBy(aq_parent(content)) \
           and aq_parent(content).Language() != content.Language():
            log.info('Obj %s (%s) not same language as parent (%s)' % (
                content.absolute_url_path(), content.Language(), aq_parent(content).Language()))  # noqa: E501


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
