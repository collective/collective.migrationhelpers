# -*- coding: UTF-8 -*-
from plone import api
from plone.app.textfield.value import RichTextValue

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


def image_scale_fixer(text):
    if text:
        for old, new in IMAGE_SCALE_MAP.items():
            # replace plone.app.imaging old scale names with new ones
            text = text.replace(
                '@@images/image/{0}'.format(old),
                '@@images/image/{0}'.format(new)
            )
            # replace AT traversing scales
            text = text.replace(
                '/image_{0}'.format(old),
                '/@@images/image/{0}'.format(new)
            )
    return text


def fix_at_image_scales(context=None):
    """Run this in Plone 5.x
    """
    catalog = api.portal.get_tool('portal_catalog')
    query = {}
    query['object_provides'] = 'plone.app.contenttypes.behaviors.richtext.IRichText'  # noqa: E501
    results = catalog.unrestrictedSearchResults(**query)
    log.info('There are {0} items with rich text behavior in total, starting migration...'.format(
        len(results)))
    for result in results:
        try:
            obj = result.getObject()
        except:
            log.warning(
                'Not possible to fetch object from catalog result for '
                'item: {0}.'.format(result.getPath()))
            continue

        text = getattr(obj.aq_base, 'text', None)
        if text:
            clean_text = image_scale_fixer(text.raw)
            if clean_text != text.raw:
                obj.text = RichTextValue(
                    raw=clean_text,
                    mimeType=text.mimeType,
                    outputMimeType=text.outputMimeType,
                    encoding=text.encoding
                )
                obj.reindexObject(idxs=('SearchableText', ))
                log.info('Text cleanup for {0}'.format(
                    '/'.join(obj.getPhysicalPath())
                ))
