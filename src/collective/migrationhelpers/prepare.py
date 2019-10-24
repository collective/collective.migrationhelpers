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
