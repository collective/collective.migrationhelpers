# -*- coding: utf-8 -*-
from plone import api
from zope.globalrequest import getRequest

import logging

log = logging.getLogger(__name__)

# You could also look at:
# 1. This Talk by Alessandro Pisa:
#    https://2017.ploneconf.org/talks/really-unconventional-migrations.html
# 2. The Inplace Migrator in ftw.upgrade


def install_pac(context=None):
    """Run this in Plone 5.2
    """
    portal = api.portal.get()
    request = getRequest()
    installer = api.portal.get_view('installer', portal, request)
    installer.install_product('plone.app.contenttypes')


def migrate_all(context=None):
    """Run this in Plone 5.2
    """
    migrate_folders()
    migrate_files()
    migrate_images()
    migrate_documents()
    migrate_collections()
    migrate_events()
    migrate_links()
    migrate_newsitems()
    migrate_topics()


def migrate_folders(context=None):
    portal = api.portal.get()
    request = getRequest()
    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['Folder']
    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=False,
        patch_searchabletext=True,
    )


def migrate_files(context=None):
    portal = api.portal.get()
    request = getRequest()
    pac_migration = api.content.get_view(
        'migrate_from_atct', portal, request)
    content_types = ['BlobFile', 'File']
    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=False,
        patch_searchabletext=True,
    )


def migrate_images(context=None):
    portal = api.portal.get()
    request = getRequest()
    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['BlobImage', 'Image']
    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=False,
        patch_searchabletext=True,
    )


def migrate_documents(context=None):
    portal = api.portal.get()
    request = getRequest()
    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['Document']
    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=False,
        patch_searchabletext=True,
    )


def migrate_collections(context=None):
    portal = api.portal.get()
    request = getRequest()
    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['Collection']
    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=False,
        patch_searchabletext=True,
    )


def migrate_events(context=None):
    portal = api.portal.get()
    request = getRequest()
    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['Event']
    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=False,
        patch_searchabletext=True,
    )


def migrate_links(context=None):
    portal = api.portal.get()
    request = getRequest()
    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['Link']
    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=False,
        patch_searchabletext=True,
    )


def migrate_newsitems(context=None):
    portal = api.portal.get()
    request = getRequest()
    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['News Item']
    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=False,
        patch_searchabletext=True,
    )


def migrate_topics(context=None):
    portal = api.portal.get()
    request = getRequest()
    pac_migration = api.content.get_view('migrate_from_atct', portal, request)
    content_types = ['Topic']
    pac_migration(
        migrate=True,
        content_types=content_types,
        migrate_schemaextended_content=True,
        reindex_catalog=False,
        patch_searchabletext=True,
    )


def migrate_ATBTreeFolder(context=None):
    """Replace very old containers for news, events and Members
    """
    portal = api.portal.get()
    # unlock all locked items in 'news'
    from plone.locking.interfaces import ILockable
    for obj in portal['news'].contentValues():
        lockable = ILockable(obj)
        if lockable.locked():
            lockable.unlock()

    # create new containers:
    if not portal['news'].__class__.__name__ == 'ATBTreeFolder':
        log.info('Migrating ATBTreeFolder not needed')
        return
    log.info('Migrating ATBTreeFolders')
    news_new = api.content.create(
      container=portal,
      type='Folder',
      id='news_new',
      title=u'Nachrichten',
    )
    for item in portal.news.contentValues():
        api.content.move(
            source=item,
            target=news_new,
            )
    api.content.delete(obj=portal['news'], check_linkintegrity=False)
    if 'events' in portal and portal['events'].__class__.__name__ == 'ATBTreeFolder':
        api.content.delete(obj=portal['events'], check_linkintegrity=False)
    if 'Members' in portal and portal['Members'].__class__.__name__ == 'ATBTreeFolder':
        api.content.delete(obj=portal['Members'], check_linkintegrity=False)
    api.content.rename(obj=portal['news_new'], new_id='news')
