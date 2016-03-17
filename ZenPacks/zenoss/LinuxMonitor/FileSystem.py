##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import itertools

from zope.interface import implements

from Products.ZenModel.FileSystem import FileSystem as BaseFileSystem
from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos.component.filesystem import FileSystemInfo as BaseFileSystemInfo
from Products.Zuul.interfaces.component import IFileSystemInfo as IBaseFileSystemInfo
from Products.Zuul.utils import ZuulMessageFactory as _t


class FileSystem(BaseFileSystem):

    """Model class for FileSystem.

    Instances of this class get stored in ZODB.

    """

    class_label = "File System"
    plural_class_label = "File Systems"

    meta_type = 'LinuxFileSystem'

    def logicalVolume(self):
        """Return the underlying LogicalVolume."""
        if not self.mount:
            return

        results = itertools.chain.from_iterable(
            self.device().search(name, mountpoint=self.mount)
            for name in ('LogicalVolume', 'SnapshotVolume'))

        for result in results:
            try:
                return result.getObject()
            except Exception:
                pass

    def blockDevice(self):
        """Return the underlying HardDisk."""
        if not self.mount:
            return

        device = self.device()
        results = device.componentSearch.search({'meta_type': 'LinuxHardDisk'})
        for brain in results:
            try:
                hd = brain.getObject()
            except Exception:
                continue
            else:
                if hd.mount == self.mount:
                    return hd

    def impacting_object(self):
        """Return the impacting LogicalVolume, HardDisk, or Device.

        A FileSystem can be impacted by only one of: it's underlying
        LogicalVolume, HardDisk, or Device. In that order.

        """
        lv = self.logicalVolume()
        if lv:
            return lv

        bd = self.blockDevice()
        if bd:
            return bd

        return self.device()

    def getRRDTemplateName(self):
        return "FileSystem"

    def getDefaultGraphDefs(self, drange=None):
        graphs = super(FileSystem, self).getDefaultGraphDefs(drange)
        underlying = self.logicalVolume() or self.blockDevice()
        if underlying:
            for graph in underlying.getDefaultGraphDefs(drange):
                graphs.append(graph)
        return graphs

    def getGraphObjects(self):
        graphs = super(FileSystem, self).getGraphObjects()
        underlying = self.logicalVolume() or self.blockDevice()
        if underlying:
            for graph in underlying.getGraphObjects():
                graphs.append(graph)
        return graphs

    def getIconPath(self):
        '''
        Return the path to an icon for this component.
        '''
        return '/++resource++linux/img/file-system.png'


class IFileSystemInfo(IBaseFileSystemInfo):

    """IInfo interface for FileSystem.

    This is used for JSON API definition. Fields described here are what will
    appear on instance's component details panel.

    """

    logicalVolume = schema.Entity(
        title=_t(u"LVM Logical Volume"),
        group="Details",
        readonly=True)

    blockDevice = schema.Entity(
        title=_t(u"Block Device"),
        group="Details",
        readonly=True)


class FileSystemInfo(BaseFileSystemInfo):

    """Info adapter for FileSystem.

    This is used for API implementation and JSON serialization. Properties
    implemented here will be available through the JSON API.

    """

    implements(IFileSystemInfo)

    @property
    @info
    def logicalVolume(self):
        return self._object.logicalVolume()

    @property
    @info
    def blockDevice(self):
        return self._object.blockDevice()

    @property
    @info
    def storageDevice(self):
        if self._object.logicalVolume():
            storagedevice = self._object.logicalVolume()
        elif self._object.blockDevice():
            storagedevice = self._object.blockDevice()
        else:
            return self._object.storageDevice
        return"<a class='z-entity' href='{0}'>{1}</a>".format(
            storagedevice.getPrimaryUrlPath(), storagedevice.title)
