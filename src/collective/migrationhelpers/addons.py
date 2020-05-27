# -*- coding: UTF-8 -*-
from plone import api
from zExceptions import BadRequest
from zope.lifecycleevent import modified

import logging

log = logging.getLogger(__name__)


def remove_ploneformgen(context=None, check_linkintegrity=True):
    portal = api.portal.get()
    portal_types = api.portal.get_tool('portal_types')
    portal_catalog = api.portal.get_tool('portal_catalog')
    qi = api.portal.get_tool('portal_quickinstaller')

    log.info('removing PloneFormGen')
    old_types = [
        'FormFolder',
    ]
    old_types = [i for i in old_types if i in portal_types]
    for old_type in old_types:
        log.info(u'Deleting Existing Instances of {}!'.format(old_type))
        for brain in portal_catalog(portal_type=old_type):
            log.info(u'Removing {}!'.format(brain.getPath()))
            api.content.delete(brain.getObject(), check_linkintegrity=check_linkintegrity)  # noqa: E501
    try:
        portal.manage_delObjects(['formgen_tool'])
    except AttributeError:
        pass
    try:
        portal.portal_properties.manage_delObjects(['ploneformgen_properties'])
    except BadRequest:
        pass

    if qi.isProductInstalled('PloneFormGen'):
        qi.uninstallProducts(['PloneFormGen'])

    if qi.isProductInstalled('Products.PloneFormGen'):
        qi.uninstallProducts(['Products.PloneFormGen'])


def remove_plonekeywordmanager(context=None):
    qi = api.portal.get_tool('portal_quickinstaller')

    # remove PloneKeywordManager
    log.info('removing PloneKeywordManager')
    if qi.isProductInstalled('PloneKeywordManager'):
        qi.uninstallProducts(['PloneKeywordManager'])


def remove_solgema_fullcalendar(context=None):
    qi = api.portal.get_tool('portal_quickinstaller')
    log.info('removing Solgema.fullcalendar')
    if qi.isProductInstalled('Solgema.fullcalendar'):
        # do not remove types
        cascade = (
            'skins', 'actions', 'portalobjects', 'workflows', 'slots',
            'registrypredicates', 'adapters', 'utilities',
        )
        qi.uninstallProducts(['Solgema.fullcalendar'], cascade=cascade)


def remove_multiple_addons(context=None):
    qi = api.portal.get_tool('portal_quickinstaller')
    portal_properties = api.portal.get_tool('portal_properties')
    portal_setup = api.portal.get_tool('portal_setup')
    portal_catalog = api.portal.get_tool('portal_catalog')
    portal = api.portal.get()
    portal_controlpanel = api.portal.get_tool('portal_controlpanel')

    # collective.quickupload
    log.info('removing collective.quickupload')
    if qi.isProductInstalled('collective.quickupload'):
        qi.uninstallProducts(['collective.quickupload'])
    try:
        portal_properties.manage_delObjects(['quickupload_properties'])
    except BadRequest:
        pass

    # collective.plonetruegallery
    log.info('removing collective.plonetruegallery')
    if qi.isProductInstalled('collective.plonetruegallery'):
        qi.uninstallProducts(['collective.plonetruegallery'])

    # Products.RedirectionTool
    log.info('removing Products.RedirectionTool')
    if qi.isProductInstalled('Products.RedirectionTool'):
        qi.uninstallProducts(['Products.RedirectionTool'])
    if qi.isProductInstalled('RedirectionTool'):
        qi.uninstallProducts(['RedirectionTool'])

    # collective.portletclass
    log.info('removing collective.portletclass')
    if qi.isProductInstalled('collective.portletclass'):
        qi.uninstallProducts(['collective.portletclass'])

    # collective.weightedportlets
    log.info('removing collective.weightedportlets')
    if qi.isProductInstalled('collective.weightedportlets'):
        qi.uninstallProducts(['collective.weightedportlets'])

    # starzel.firstitem
    log.info('removing starzel.firstitem')
    for brain in portal_catalog.searchResults(portal_type='Folder'):
        obj = brain.getObject()
        if getattr(obj.aq_base, 'layout', None) == 'firstitem_view':
            obj.manage_delProperties(['layout'])
            modified(obj)
    if qi.isProductInstalled('starzel.firstitem'):
        qi.uninstallProducts(['starzel.firstitem'])
    if getattr(portal, 'layout', None) == 'firstitem_view':
        portal.manage_delProperties(['layout'])

    try:
        portal_properties.manage_delObjects(['cli_properties'])
    except BadRequest:
        pass

    log.info('removing collective.js.fancybox')
    if qi.isProductInstalled('collective.js.fancybox'):
        qi.uninstallProducts(['collective.js.fancybox'])

    log.info('removing collective.z3cform.widgets')
    if qi.isProductInstalled('collective.z3cform.widgets'):
        qi.uninstallProducts(['collective.z3cform.widgets'])

    log.info('removing collective.z3cform.keywordwidget')
    if qi.isProductInstalled('collective.z3cform.keywordwidget'):
        qi.uninstallProducts(['collective.z3cform.keywordwidget'])

    log.info('removing collective.z3cform.datetimewidget')
    if qi.isProductInstalled('collective.z3cform.datetimewidget'):
        qi.uninstallProducts(['collective.z3cform.datetimewidget'])

    # Remove collective.easyslider
    if qi.isProductInstalled('collective.easyslider'):
        from collective.easyslider.interfaces import IViewEasySlider
        for brain in api.content.find(
                object_provides=IViewEasySlider.__identifier__):
            obj = brain.getObject()
            # noLongerProvides(obj, IViewEasySlider)
            if obj.getLayout() == 'sliderview':
                obj.manage_delProperties(['layout'])
                log.info('removed easyslider from {}'.format(brain.getURL()))
        portal_controlpanel.unregisterConfiglet('easyslieder')
        qi.uninstallProducts(['collective.easyslider'])
    try:
        portal_properties.manage_delObjects(['easyslideshow_properties'])
    except BadRequest:
        pass

    # remove cciaa.modulistica
    log.info('removing cciaa.modulistica')
    if qi.isProductInstalled('cciaa.modulistica'):
        portal_catalog._removeIndex('getRawRelatedItems')
        from cciaa.modulistica.interfaces import CCIAAModAbleContent
        for brain in api.content.find(
                object_provides=CCIAAModAbleContent.__identifier__):
            obj = brain.getObject()
            # noLongerProvides(obj, IViewEasySlider)
            if obj.getLayout() == 'cciaa_modulistica_view':
                obj.manage_delProperties(['layout'])
                log.info('removed cciaa.modulistica from {}'.format(brain.getURL()))  # noqa: E501
        qi.uninstallProducts(['cciaa.modulistica'])

    # Solgema.fullcalendar
    log.info('removing Solgema.fullcalendar')
    if qi.isProductInstalled('Solgema.fullcalendar'):
        qi.uninstallProducts(['Solgema.fullcalendar'])

    # collective.imagetags
    log.info('removing collective.imagetags')
    if qi.isProductInstalled('collective.imagetags'):
        portal_controlpanel.unregisterConfiglet('imagetags')
        # do not uninstall utilities since that will nuke the registry
        cascade = [
            'types', 'skins', 'actions', 'portalobjects', 'workflows', 'slots',
            'registrypredicates', 'adapters']
        qi.uninstallProducts(['collective.imagetags'], cascade=cascade)

    # wpd.mmxi.countdown
    # delete portlet instance
    from plone.portlets.interfaces import IPortletAssignmentMapping
    from plone.portlets.interfaces import IPortletManager
    from zope.component import getMultiAdapter
    from zope.component import getUtility
    log.info('removing wpd.mmxi.countdown')
    content = api.content.get(path='/nm/example-intranet')
    if content:
        manager = getUtility(
            IPortletManager, name='plone.leftcolumn', context=content)
        mapping = getMultiAdapter(
            (content, manager), IPortletAssignmentMapping)
        try:
            del mapping['wpd-countdown']
        except KeyError:
            pass

    if qi.isProductInstalled('wpd.mmxi.countdown'):
        qi.uninstallProducts(['wpd.mmxi.countdown'])

    # Products.Carousel
    log.info('removing Products.Carousel')
    if qi.isProductInstalled('Products.Carousel'):
        qi.uninstallProducts(['Products.Carousel'])

    # Products.PlonePopoll
    log.info('removing Products.PlonePopoll')
    if qi.isProductInstalled('PlonePopoll'):
        qi.uninstallProducts(['PlonePopoll'])

    # eea.facetednavigation
    log.info('removing eea.facetednavigation')
    if qi.isProductInstalled('eea.facetednavigation'):
        qi.uninstallProducts(['eea.facetednavigation'])

    # eea.relations
    log.info('removing eea.relations')
    if qi.isProductInstalled('eea.relations'):
        qi.uninstallProducts(['eea.relations'])

    # Products.ECLecture
    log.info('removing Products.ECLecture')
    if qi.isProductInstalled('ECLecture'):
        qi.uninstallProducts(['ECLecture'])

    # Products.ImageEditor
    log.info('removing Products.ImageEditor')
    if qi.isProductInstalled('ImageEditor'):
        qi.uninstallProducts(['ImageEditor'])

    # collective.plonetruegallery
    log.info('removing collective.plonetruegallery')
    if qi.isProductInstalled('collective.plonetruegallery'):
        qi.uninstallProducts(['collective.plonetruegallery'])
    # zettwerk.ui
    log.info('removing zettwerk.ui')
    if qi.isProductInstalled('zettwerk.ui'):
        qi.uninstallProducts(['zettwerk.ui'])

    # Solgema.fullcalendar
    log.info('removing Solgema.fullcalendar')
    if qi.isProductInstalled('Solgema.fullcalendar'):
        qi.uninstallProducts(['Solgema.fullcalendar'])

    # Solgema.ContextualContentMenu
    log.info('removing Solgema.ContextualContentMenu')
    if qi.isProductInstalled('Solgema.ContextualContentMenu'):
        qi.uninstallProducts(['Solgema.ContextualContentMenu'])

    # Products.ImageEditor
    log.info('removing Products.ImageEditor')
    if qi.isProductInstalled('Products.ImageEditor'):
        qi.uninstallProducts(['Products.ImageEditor'])
    try:
        portal_properties.manage_delObjects(['imageeditor'])
    except BadRequest:
        pass

    # collective.easyslideshow
    log.info('removing collective.easyslideshow')
    if qi.isProductInstalled('collective.easyslideshow'):
        qi.uninstallProducts(['collective.easyslideshow'])
    try:
        portal_properties.manage_delObjects(['easyslideshow_properties'])
    except BadRequest:
        pass

    # collective.quickupload
    log.info('removing collective.quickupload')
    if qi.isProductInstalled('collective.quickupload'):
        qi.uninstallProducts(['collective.quickupload'])
    try:
        portal_properties.manage_delObjects(['quickupload_properties'])
    except BadRequest:
        pass

    # collective.prettyphoto
    log.info('removing collective.prettyphoto')
    if qi.isProductInstalled('collective.prettyphoto'):
        qi.uninstallProducts(['collective.prettyphoto'])
    try:
        portal_properties.manage_delObjects(['prettyphoto_properties'])
    except BadRequest:
        pass

    # collective.plonefinder
    log.info('removing collective.plonefinder')
    if qi.isProductInstalled('collective.plonefinder'):
        qi.uninstallProducts(['collective.plonefinder'])

    # Products.PloneFormGen
    log.info('removing Products.PloneFormGen')
    if qi.isProductInstalled('PloneFormGen'):
        qi.uninstallProducts(['PloneFormGen'])
    try:
        portal_properties.manage_delObjects(['ploneformgen_properties'])
    except BadRequest:
        pass

    # DataGridField
    log.info('removing DataGridField')
    if qi.isProductInstalled('DataGridField'):
        qi.uninstallProducts(['DataGridField'])

    # collective.js.fullcalendar
    log.info('removing collective.js.fullcalendar')
    if qi.isProductInstalled('collective.js.fullcalendar'):
        qi.uninstallProducts(['collective.js.fullcalendar'])

    # Products.PloneFlashUpload (not installed)
    log.info('removing Products.PloneFlashUpload')
    if qi.isProductInstalled('Products.PloneFlashUpload'):
        qi.uninstallProducts(['Products.PloneFlashUpload'])

    # p4a.subtyper
    log.info('removing p4a.subtyper')
    if qi.isProductInstalled('p4a.subtyper'):
        qi.uninstallProducts(['p4a.subtyper'])

    # collective.externaleditor
    log.info('removing collective.externaleditor')
    if qi.isProductInstalled('collective.externaleditor'):
        qi.uninstallProducts(['collective.externaleditor'])

    # collective.ckeditor
    log.info('removing collective.ckeditor')
    if qi.isProductInstalled('collective.ckeditor'):
        qi.uninstallProducts(['collective.ckeditor'])
    try:
        portal_properties.manage_delObjects(['ckeditor_properties'])
    except BadRequest:
        pass

    # redturtle.smartlink
    log.info('removing redturtle.smartlink')
    if qi.isProductInstalled('redturtle.smartlink'):
        # run migration
        portal_setup.runAllImportStepsFromProfile(
            'profile-redturtle.smartlink:smartLinkToATLink', purge_old=False)
        qi.uninstallProducts(['redturtle.smartlink'])

    # collective.js.jqueryui
    log.info('removing collective.js.jqueryui')
    if qi.isProductInstalled('collective.js.jqueryui'):
        qi.uninstallProducts(['collective.js.jqueryui'])
    try:
        portal_properties.manage_delObjects(['jqueryui_properties'])
    except BadRequest:
        pass

    addons = [
        'collective.solr',
        'underscore.js',
        'plone.formwidget.recurrence',
        'operun.media',
        'collective.js.colorpicker',
        'fourdigits.portlet.twitter',
        'collective.js.moment',
        'plone.app.relationfield',
        'fourdigits.portlet.twitter',
        'collective.js.colorpicker',
        'plone.formwidget.recurrence',
        'plone.formwidget.autocomplete',
    ]
    for addon in addons:
        if qi.isProductInstalled(addon):
            log.info(u'Uninstalling {}'.format(addon))
            qi.uninstallProducts([addon])
        else:
            log.info(u'{} is not installed'.format(addon))


def cleanup_behaviors(context=None):
    # Remove obsolete behaviors
    portal_types = api.portal.get_tool('portal_types')

    to_delete = [
        'plone.app.stagingbehavior.interfaces.IStagingSupport',
        'collective.plonetruegallery.interfaces.IGallery',
        'plone.app.referenceablebehavior.referenceable.IReferenceable',
    ]
    content_types = [
        'Collection',
        'Document',
        'Event',
        'File',
        'Folder',
        'News Item',
    ]
    for ct in content_types:
        changed = False
        fti = portal_types[ct]
        behaviors = list(fti.behaviors)
        for behavior in to_delete:
            if behavior in behaviors:
                behaviors.remove(behavior)
                changed = True
        if changed:
            fti._updateProperty('behaviors', tuple(behaviors))
