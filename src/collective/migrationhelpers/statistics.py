# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from Products.Five import BrowserView
from operator import itemgetter

import logging

log = logging.getLogger(__name__)


class Stats(BrowserView):
    """Get info about the content in the portal or the current context.
    """

    EARLIEST_YEAR = 2001

    def __call__(self):
        context = self.context
        portal_types = api.portal.get_tool('portal_types')
        catalog = api.portal.get_tool('portal_catalog')
        results = {}
        log.info(u'\n\nNumber of items by portal_type\n')
        for portal_type in portal_types:
            brains = catalog.unrestrictedSearchResults(portal_type=portal_type)
            results[portal_type] = len(brains)
        for k, v in sorted(results.items(), key=itemgetter(1), reverse=True):
            log.info('{}: {}'.format(k, v))
        results = {}
        all_children = context.contentItems()
        for i in all_children:
            path = i[1].getPhysicalPath()
            path = '/'.join(path)
            objects_in_path = len(catalog.unrestrictedSearchResults(
                path={'query': path}))
            results[path] = objects_in_path
        log.info(u'\n\nNumber of items by folder\n')
        for k, v in sorted(results.items(), key=itemgetter(1), reverse=True):
            log.info('{}: {}'.format(k, v))
        log.info(u'\n\nNumber of items by type and year\n')
        years = range(self.EARLIEST_YEAR, 2020)
        frequent_types = [
            'Event',
            'News Item',
            'File',
            'Folder',
            'Document',
            'Image',
            'Link',
        ]
        for content_type in frequent_types:
            for year in years:
                modified = {
                    'query': [DateTime(year, 1, 1), DateTime(year + 1, 1, 1)],
                    'range': 'minmax',
                }
                log.info('{} {}'.format(
                    '%ss last modified in %s: ' % (content_type, year),
                    len(catalog.unrestrictedSearchResults(
                        modified=modified, portal_type=content_type))
                ))
        log.info(u'\n\nVery large items\n')
        results = {}
        for brain in catalog.unrestrictedSearchResults(
                portal_type=['File', 'Image']):
            size = brain.getObjSize
            if "MB" in size:
                size = float(size.split()[0])
                if size > 10:
                    results[brain.getPath()] = size

        for item in sorted(results.items(), key=itemgetter(1), reverse=True):
            log.info(u'{} MB {}'.format(item[1], item[0]))
        return u'Done'


class ContentSize(BrowserView):
    """How many MB of which content is there really?
    Takes the current path into account.
    """

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        portal_types = api.portal.get_tool('portal_types')
        results = {}
        report = u''
        path = '/'.join(self.context.getPhysicalPath())
        for portal_type in portal_types:
            results[portal_type] = {}
            results[portal_type]['GB'] = 0
            results[portal_type]['MB'] = 0
            results[portal_type]['KB'] = 0
            for brain in catalog.unrestrictedSearchResults(
                    portal_type=portal_type,
                    path={'query': path},
                    ):
                size = brain.getObjSize
                if not size or size == '0 KB':
                    continue
                elif "GB" in size:
                    size = float(size.split()[0])
                    results[portal_type]['GB'] += size
                elif "MB" in size:
                    size = float(size.split()[0])
                    results[portal_type]['MB'] += size
                elif "KB" in size:
                    size = float(size.split()[0])
                    results[portal_type]['KB'] += size
            total_kb = results[portal_type]['KB'] / 1024.0
            total_mb = results[portal_type]['MB']
            total_gb = results[portal_type]['GB'] * 1024.0
            total = total_kb + total_mb + total_gb
            total = round(total, 2)
            if total:
                log.info('{}: {} MB'.format(portal_type, total))
                report += u'{}: {} MB\n'.format(portal_type, total)
        return report


class ObsoleteInfo(BrowserView):
    """Get info about content-types that may needs to be replaced
    """
    OBSOLETE_TYPES = ['FormFolder', 'HelpCenter', 'Collage', 'CalendarXFolder']

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        for portal_type in self.OBSOLETE_TYPES:
            brains = catalog.unrestrictedSearchResults(portal_type=portal_type)
            log.info('')
            log.info('')
            log.info('{}: {}'.format(portal_type, len(brains)))
            log.info('')
            for brain in brains:
                path = brain.getPath()
                items = catalog.unrestrictedSearchResults(
                    path=path, sort_on='modified', sort_order='descending')
                log.info('{} (modified {}) contains {} items. Newest from {}'.format(
                    path, brain.modified.year(), len(items), items[0].modified.year()))
        return 'Done'


class ExportLocalRoles(BrowserView):
    """A alternative would be zopyx.plone.cassandra
    """

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        results_roles = {}
        results_block = [u'Items with disabled inheriting: ']
        for brain in catalog():
            obj = brain.getObject()
            local_roles = getattr(obj, '__ac_local_roles__', None)
            if local_roles:
                # drop owner
                for user, roles in list(local_roles.items()):
                    if roles == ['Owner']:
                        local_roles.pop(user)
                if local_roles:
                    results_roles[obj.absolute_url_path()] = local_roles
            if getattr(obj, '__ac_local_roles_block__', None):
                results_block.append(obj.absolute_url_path())

        return [results_roles, results_block]
