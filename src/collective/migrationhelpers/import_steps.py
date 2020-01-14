# -*- coding: utf-8 -*-
from plone import api

import logging

log = logging.getLogger(__name__)


def remove_all_broken_steps(context=None):
    from plone.app.upgrade.utils import unregisterSteps
    portal_setup = api.portal.get_tool('portal_setup')

    _REMOVE_IMPORT_STEPS = []
    _REMOVE_EXPORT_STEPS = []
    unregisterSteps(
        portal_setup,
        import_steps=_REMOVE_IMPORT_STEPS,
        export_steps=_REMOVE_EXPORT_STEPS)


def remove_broken_steps_manually(context=None):
    portal_setup = api.portal.get_tool('portal_setup')
    broken_import_steps = [
        'collective.z3cform.datetimewidget',
        'languagetool',
        'ploneformgen',
        'redirectiontool_various',
        'solgemacontextualcontentmenu',
        'solgemafullcalendarinstall',
        'solgemafullcalendaruninstall',
    ]
    log.info('remove import-steps')
    registry = portal_setup.getImportStepRegistry()
    for broken_import_step in broken_import_steps:
        if broken_import_step in registry.listSteps():
            registry.unregisterStep(broken_import_step)

    broken_export_steps = [
        'collective.plonetruegallery.export',
        'languagetool',
    ]
    log.info('remove export-steps')
    registry = portal_setup.getExportStepRegistry()
    for broken_export_step in broken_export_steps:
        if broken_export_step in registry.listSteps():
            registry.unregisterStep(broken_export_step)
    portal_setup._p_changed = True
