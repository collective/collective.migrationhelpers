# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
from plone import api
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import iterSchemata
from zope.schema import getFieldsInOrder

import logging

log = logging.getLogger(__name__)


# Old scale name to new scale name
IMAGE_SCALE_MAP = {
    'icon': 'icon',
    'large': 'large',
    'listing': 'listing',
    'mini': 'mini',
    'preview': 'preview',
    'thumb': 'thumb',
    'tile': 'tile',
    # BBB
    'article': 'preview',
    'artikel': 'preview',
    'carousel': 'preview',
    'company_index': 'thumb',
    'content': 'preview',
    'leadimage': 'tile',
    'portlet-fullpage': 'large',
    'portlet-halfpage': 'large',
    'portlet-links': 'thumb',
    'portlet': 'thumb',
    'staff_crop': 'thumb',
    'staff_index': 'thumb',
}


def image_scale_fixer(text, obj):
    if not text:
        return
    soup = BeautifulSoup(text, 'html.parser')
    for img in soup.find_all('img'):
        src = img['src']
        if src.startswith('http'):
            log.info(u'Skip external image {} used in {}'.format(src, obj.absolute_url()))
            continue

        for old, new in IMAGE_SCALE_MAP.items():
            # replace plone.app.imaging old scale names with new ones
            src = src.replace(
                u'@@images/image/{}'.format(old),
                u'@@images/image/{}'.format(new)
            )
            # replace AT traversing scales
            src = src.replace(
                u'/image_{}'.format(old),
                u'/@@images/image/{}'.format(new)
            )

        if '/@@images/' in src:
            scale = src.split('/@@images/image/')[-1]
            if '/' in scale:
                log.info(u'Invalid image-link in {}: {}'.format(obj.absolute_url(), src))
            img['data-scale'] = scale
        else:
            # image not scaled
            img['data-scale'] = ''

        img['src'] = src
        img['data-linktype'] = 'image'
        img['class'] = img.get("class", []) + ['image-richtext']

        if 'resolveuid' in src:
            uuid = src.split('resolveuid/')[1].split('/')[0]
            img['data-val'] = uuid
        else:
            log.info(u'Image-link without resolveuid in {}: {}'.format(obj.absolute_url(), src))

    return soup.decode()


def fix_at_image_scales(context=None):
    """Run this in Plone 5.x
    """
    catalog = api.portal.get_tool('portal_catalog')
    query = {}
    if hasattr(catalog, "getAllBrains"):
        results = catalog.getAllBrains()
    else:
        results = catalog.unrestrictedSearchResults(**query)
    log.info('Starting migration of image scales in rich text fields.')
    for result in results:
        try:
            obj = result.getObject()
        except (KeyError, AttributeError):
            log.warning(
                'Not possible to fetch object from catalog result for '
                'item: {0}.'.format(result.getPath()))
            continue
        changed = False
        for schema in iterSchemata(obj):
            fields = getFieldsInOrder(schema)
            for name, field in fields:
                if not IRichText.providedBy(field):
                    continue
                text = getattr(obj.aq_base, name, None)
                if not text:
                    continue
                clean_text = image_scale_fixer(text.raw, obj)
                if clean_text == text.raw:
                    continue
                setattr(obj, name, RichTextValue(
                    raw=clean_text,
                    mimeType=text.mimeType,
                    outputMimeType=text.outputMimeType,
                    encoding=text.encoding
                ))
                changed = True
                log.info(u'Text cleanup in field {0} for {1}'.format(
                    name, '/'.join(obj.getPhysicalPath())
                ))
        if changed:
            obj.reindexObject(idxs=('SearchableText', ))
            log.info(u'Text cleanup for {0}'.format(
                '/'.join(obj.getPhysicalPath())
            ))
