# -*- coding: utf-8 -*-

# Patch missing or broken interfaces and classes
# This code belongs in a __init__.py
# For more inspiration look at
# https://github.com/plone/plone.app.upgrade/blob/master/plone/app/upgrade/__init__.py

from datetime import timedelta
from datetime import tzinfo
from OFS.SimpleItem import SimpleItem
from plone.app.upgrade.utils import alias_module
from zope.interface import Interface


class IBBB(Interface):
    pass


class BBB(object):
    pass


UITool = SimpleItem
SlideshowDescriptor = SimpleItem
ClickmapTool = SimpleItem


class DummyFakeZone(tzinfo):
    """Fake timezone to be applied to EventBasic start and end dates before
    data_postprocessing event handler sets the correct one.
    """
    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "FAKEZONE"

    def dst(self, dt):
        return timedelta(0)


# stuff from incompletely uninstalled addons
try:
    from collective.zipfiletransport.utilities.interfaces import IZipFileTransportUtility
    IZipFileTransportUtility  # noqa
except ImportError:
    alias_module('collective.zipfiletransport.utilities.interfaces.IZipFileTransportUtility', IBBB)  # noqa: E501


try:
    from collective.z3cform.widgets.interfaces import ILayer
    ILayer  # noqa
except ImportError:
    alias_module('collective.z3cform.widgets.interfaces.ILayer', IBBB)  # noqa: E501


try:
    from App.interfaces import IPersistentExtra
    IPersistentExtra  # noqa
except ImportError:
    alias_module('App.interfaces.IPersistentExtra', IBBB)  # noqa: E501


try:
    from plone.app.stagingbehavior.relation import StagingRelationValue
    StagingRelationValue  # noqa
except ImportError:
    from z3c.relationfield.relation import RelationValue
    alias_module('plone.app.stagingbehavior.relation.StagingRelationValue', RelationValue)  # noqa: E501


try:
    from webdav.interfaces import IFTPAccess
    IFTPAccess  # noqa
except ImportError:
    alias_module('webdav.interfaces.IFTPAccess', IBBB)  # noqa: E501


try:
    from plone.app.event.dx.behaviors import FakeZone
    FakeZone  # noqa
except ImportError:
    alias_module('plone.app.event.dx.behaviors.FakeZone', DummyFakeZone)  # noqa: E501


try:
    from collective.easyslideshow.descriptors import SlideshowDescriptor
    SlideshowDescriptor  # noqa
except ImportError:
    alias_module('collective.easyslideshow.descriptors.SlideshowDescriptor', SlideshowDescriptor)  # noqa: E501


try:
    from zettwerk.clickmap.ClickmapTool import ClickmapTool
    ClickmapTool  # noqa
except ImportError:
    alias_module('zettwerk.clickmap.ClickmapTool.ClickmapTool', SlideshowDescriptor)  # noqa: E501


try:
    from zettwerk.ui.tool.tool import UITool
    UITool  # noqa
except ImportError:
    alias_module('zettwerk.ui.tool.tool.UITool', UITool)


try:
    from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor
    IPortalTypedFolderishDescriptor  # noqa
except ImportError:
    alias_module('p4a.subtyper.interfaces.IPortalTypedFolderishDescriptor', IBBB)  # noqa: E501

try:
    from collective.solr import interfaces
    interfaces  # noqa
except ImportError:
    alias_module('collective.solr.indexer.SolrIndexProcessor', BBB)
    alias_module('collective.solr.manager.SolrConnectionManager', BBB)
    alias_module('collective.solr.search.Search', BBB)
    alias_module('collective.solr.interfaces.ISolrIndexQueueProcessor', IBBB)
    alias_module('collective.solr.interfaces.ISolrConnectionManager', IBBB)
    alias_module('collective.solr.interfaces.ISearch', IBBB)
    alias_module('collective.solr.interfaces.ISolrSchema', IBBB)
