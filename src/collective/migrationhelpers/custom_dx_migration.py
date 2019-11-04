# -*- coding: utf-8 -*-
# Migrate PloneHelpCenmter to Dexterity default content
from plone import api
from Products.CMFPlone.utils import safe_unicode
from plone.app.textfield.value import RichTextValue
from plone.app.contenttypes.migration.migration import migrateCustomAT
from zope.lifecycleevent import modified

import transaction
import logging

log = logging.getLogger(__name__)


def migrate_helpcenter_to_dx(context=None):
    # unset layouts
    change_phc_layouts()

    # migrate containers
    migrate_helpcenter()
    migrate_helpcenterfaqfolder()
    migrate_helpcenterhowtofolder()
    migrate_helpcentererrorreferencefolder()
    migrate_helpcenterinstructionalvideofolder()
    migrate_helpcenterlinkfolder()
    migrate_helpcenterreferencemanualfolder()
    migrate_helpcentertutorialfolder()

    # migrate items
    migrate_helpcenterhowto()
    migrate_helpcenterleafpage()
    migrate_helpcenterfaq()
    migrate_helpcenterdefinition()
    migrate_helpcentererrorreference()
    migrate_helpcenterglossary()
    migrate_helpcenterinstructionalvideo()
    migrate_helpcenterlink()
    migrate_helpcenterreferencemanual()
    migrate_helpcenterreferencemanualpage()
    migrate_helpcenterreferencemanualsection()
    migrate_helpcentertutorial()
    migrate_helpcentertutorialpage()
    migrate_helpcenterknowledgebase()


def change_phc_layouts(context=None):
    """Some PHC have custom layouts set. Remove the property to fix.
    """
    for brain in api.content.find(portal_type=[
            'HelpCenter',
            'HelpCenterKnowledgeBase',
            'HelpCenterLeafPage',
            'HelpCenterReferenceManualPage',
            ]):
        obj = brain.getObject()
        # unset all phc layouts
        if getattr(obj.aq_base, 'layout', None) is not None:
            obj.manage_delProperties(['layout'])
            modified(obj)
    transaction.commit()


def appending_richtext_migrator(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """Append text to a existing Richtext Value (if it exists).
    """
    field = src_obj.getField(src_fieldname)
    if not field:
        return
    value = ''
    value = safe_unicode(field.getRaw(src_obj))
    if value.strip() == '':
        return
    existing_value = getattr(dst_obj, dst_fieldname)
    if existing_value and existing_value.raw:
        heading = u'<h2>{0}</h2>'.format(src_fieldname)
        value = existing_value.raw + heading + value
    value = RichTextValue(
        raw=value,
        mimeType='text/html',
        outputMimeType='text/x-html-safe')
    setattr(dst_obj, dst_fieldname, value)


def appending_text_migrator(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """Append text to a existing text Value (if it exists).

    Use it to merge multiple PlainText-Fields into one.
    """
    field = src_obj.getField(src_fieldname)
    if field:
        at_value = field.get(src_obj)
    else:
        at_value = getattr(src_obj, src_fieldname, None)
        if at_value and hasattr(at_value, '__call__'):
            at_value = at_value()
    at_value = safe_unicode(at_value)
    existing_value = getattr(dst_obj, dst_fieldname)
    if existing_value:
        heading = u'\n{0}:\n'.format(src_fieldname)
        value = existing_value + heading + at_value
    setattr(dst_obj, dst_fieldname, value)


def migrate_helpcenter(context=None):
    fields_mapping = (
        {'AT_field_name': 'rights',
         'DX_field_name': 'text',
         'field_migrator': appending_richtext_migrator},
    )
    log.info('Migrating HelpCenter...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenter',
        dst_type='Folder')


def migrate_helpcenterfaqfolder(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterFAQFolder...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterFAQFolder',
        dst_type='Folder',
    )


def migrate_helpcenterhowtofolder(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterHowToFolder...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterHowToFolder',
        dst_type='Folder',
    )


def migrate_helpcentererrorreferencefolder(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterErrorReferenceFolder...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterErrorReferenceFolder',
        dst_type='Folder',
        )


def migrate_helpcenterinstructionalvideofolder(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterInstructionalVideoFolder...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterInstructionalVideoFolder',
        dst_type='Folder',
        )


def migrate_helpcenterlinkfolder(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterLinkFolder...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterLinkFolder',
        dst_type='Folder',
        )


def migrate_helpcenterreferencemanualfolder(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterManualFolder...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterReferenceManualFolder',
        dst_type='Folder',
        )


def migrate_helpcentertutorialfolder(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterTutorialFolder...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterTutorialFolder',
        dst_type='Folder',
        )


def migrate_helpcenterreferencemanual(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterReferenceManual...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterReferenceManual',
        dst_type='Folder',
        )


def migrate_helpcenterhowto(context=None):
    fields_mapping = (
        {'AT_field_name': 'text',
         'DX_field_name': 'text',
         'DX_field_type': 'RichText',
         },
    )
    log.info('Migrating HelpCenterHowTo...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterHowTo',
        dst_type='Folder',
    )


def migrate_helpcenterreferencemanualsection(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterReferencemanualsection...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterReferenceManualSection',
        dst_type='Folder',
        )


def migrate_helpcenterknowledgebase(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterKnowledgebase...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterKnowledgebase',
        dst_type='Folder',
        )


def migrate_helpcentertutorial(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterTutorial...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterTutorial',
        dst_type='Folder',
        )


def migrate_helpcenterfaq(context=None):
    fields_mapping = (
        {'AT_field_name': 'text',
         'DX_field_name': 'text',
         'DX_field_type': 'RichText',
         },
    )
    log.info('Migrating HelpCenterFAQ...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterFAQ',
        dst_type='Document',
    )


def migrate_helpcenterleafpage(context=None):
    fields_mapping = (
        {'AT_field_name': 'text',
         'DX_field_name': 'text',
         'DX_field_type': 'RichText',
         },
    )
    log.info('Migrating HelpCenterLeafPage...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterLeafPage',
        dst_type='Document',
    )


def migrate_helpcenterdefinition(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterDefinition...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterDefinition',
        dst_type='Document',
        )


def migrate_helpcentererrorreference(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterErrorReference...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterErrorReference',
        dst_type='Document',
        )


def migrate_helpcenterglossary(context=None):
    fields_mapping = []
    log.info('Migrating HelpCenterGlossary...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterGlossary',
        dst_type='Document',
        )


def migrate_helpcenterinstructionalvideo(context=None):
    fields_mapping = (
        {'AT_field_name': 'video_file',
         'DX_field_name': 'file',
         'DX_field_type': 'NamedBlobFile',
         },
    )
    log.info('Migrating HelpCenterInstructionalVideo...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterInstructionalVideo',
        dst_type='File',
        )


def migrate_helpcenterlink(context=None):
    fields_mapping = (
        {'AT_field_name': 'url',
         'DX_field_name': 'remoteUrl'},
    )
    log.info('Migrating HelpCenterLink...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterLink',
        dst_type='Link',
        )


def migrate_helpcenterreferencemanualpage(context=None):
    fields_mapping = (
        {'AT_field_name': 'text',
         'DX_field_name': 'text',
         'DX_field_type': 'RichText',
         },
    )
    log.info('Migrating HelpCenterReferenceManualpage...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterReferenceManualpage',
        dst_type='Document',
        )


def migrate_helpcentertutorialpage(context=None):
    fields_mapping = (
        {'AT_field_name': 'text',
         'DX_field_name': 'text',
         'DX_field_type': 'RichText',
         },
    )
    log.info('Migrating HelpCenterTutorialpage...')
    migrateCustomAT(
        fields_mapping,
        src_type='HelpCenterTutorialpage',
        dst_type='Document',
        )
