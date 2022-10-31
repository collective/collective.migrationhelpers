# -*- coding: UTF-8 -*-
from plone import api
from zExceptions import BadRequest

import logging

log = logging.getLogger(__name__)


def disable_solr(context=None):
    try:
        from collective.solr.utils import getConfig
        HAVE_SOLR = True
    except ImportError:
        HAVE_SOLR = False
    if HAVE_SOLR:
        config = getConfig()
        if config:
            config.active = False
            log.info('SOLR disabled')


def disable_ldap(context=None):
    names_of_ldap_plugins = [
        'ldap_ad_mp',
        'adplugin',
        'adplugin_bg48',
        'web_server_auth',
    ]
    acl = api.portal.get_tool('acl_users')
    for ldap_plugin in names_of_ldap_plugins:
        try:
            acl.manage_delObjects([ldap_plugin])
            log.info('Deleted ldap-plugin {}'.format(ldap_plugin))
        except BadRequest:
            log.info('ldap-plugin {} not found'.format(ldap_plugin))


def disable_caching(context=None):
    """Disable caching and purging.

    Especially purging is not useful during a large upgrade:
    you will only swamp the purge queue.

    After the the upgrade, you can call its counter part: enable_caching.
    """
    for name in (
        "plone.caching.interfaces.ICacheSettings.enabled",
        "plone.cachepurging.interfaces.ICachePurgingSettings.enabled",
    ):
        if api.portal.get_registry_record(name, default=False):
            api.portal.set_registry_record(name, False)
            log.info("Switched off %s", name)


def enable_caching(context):
    """Enable caching and purging."""
    portal = api.portal.get()
    portal_url = portal.absolute_url()
    if "http://localhost" in portal_url or "http://127.0.0.1" in portal_url:
        log.info("Not enabling caching and purging on localhost.")
        return
    for name in (
        "plone.caching.interfaces.ICacheSettings.enabled",
        "plone.cachepurging.interfaces.ICachePurgingSettings.enabled",
    ):
        if not api.portal.get_registry_record(name, default=False):
            api.portal.set_registry_record(name, True)
            log.info("Turned on %s", name)


def disable_fingerpointing(context=None):
    """During big upgrades, fingerpointing is mostly useless, so switch it off.

    After the the upgrade, you can call its counter part: enable_fingerpointing.
    """
    from collective.fingerpointing.interfaces import IFingerPointingSettings

    base_name = IFingerPointingSettings.__identifier__
    for event in ["audit_pas", "audit_lifecycle", "audit_workflow", "audit_profile_imports", "audit_registry", "audit_iterate"]:
        name = ".".join([base_name, event])
        if api.portal.get_registry_record(name, default=False):
            api.portal.set_registry_record(name, False)
            log.info("Switched off %s", name)


def enable_fingerpointing(context=None):
    """After big upgrade is done, fingerpointing is welcome again.

    The list of events is hardcoded.
    Please check yourself which ones you want to re-enable.
    """
    from collective.fingerpointing.interfaces import IFingerPointingSettings

    base_name = IFingerPointingSettings.__identifier__
    for event in [
        "audit_pas",
        "audit_lifecycle",
        "audit_workflow",
        "audit_profile_imports",
        "audit_registry",
        "audit_iterate",
    ]:
        name = ".".join([base_name, event])
        if not api.portal.get_registry_record(name, default=False):
            api.portal.set_registry_record(name, True)
            log.info("Switched on %s", name)


def remove_overrides(context=None):
    log.info('removing portal_skins overrides')
    portal_skins = api.portal.get_tool('portal_skins')
    custom = portal_skins['custom']
    for name in custom.keys():
        custom.manage_delObjects([name])
        log.info(u'Removed skin item {}'.format(name))

    log.info('removing portal_view_customizations')
    view_customizations = api.portal.get_tool('portal_view_customizations')
    for name in view_customizations.keys():
        view_customizations.manage_delObjects([name])
        log.info(u'Removed portal_view_customizations item {}'.format(name))


def release_all_webdav_locks(context=None):
    from Products.CMFPlone.utils import base_hasattr
    portal = api.portal.get()

    def unlock(obj, path):
        if base_hasattr(obj, 'wl_isLocked') and obj.wl_isLocked():
            obj.wl_clearLocks()
            log.info(u'Unlocked {}'.format(path))

    portal.ZopeFindAndApply(portal, search_sub=True, apply_func=unlock)
