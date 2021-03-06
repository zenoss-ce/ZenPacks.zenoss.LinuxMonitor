##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
log = logging.getLogger('zen.lvm.cinder')

from zope.interface import implements
from zope.event import notify

from Products.Zuul.catalog.events import IndexingEvent
from Products.Zuul.interfaces import ICatalogTool

from ZenPacks.zenoss.OpenStackInfrastructure.interfaces \
    import ICinderImplementationPlugin
from ZenPacks.zenoss.OpenStackInfrastructure.cinder_integration \
    import BaseCinderImplementationPlugin


class LinuxCinderImplementationPlugin(BaseCinderImplementationPlugin):
    implements(ICinderImplementationPlugin)

    def getVolumeIntegrationKeys(self, osi_volume):
        # osi_volume.id: volume-366fc7b1-4c11-4ae6-9ec2-d096df0194e0
        # this matches the volume name on LVM side
        return ['cinder.lvm:logicalvolume|' + osi_volume.id]

    def getSnapshotIntegrationKeys(self, osi_snapshot):
        # osi_snapshot.id: snapshot-2908fb56-5dc1-45fd-b4ba-506157f1880c
        # this matches the snapshot name on LVM side
        return ['cinder.lvm:snapshotvolume|' + osi_snapshot.id]

    @classmethod
    def reindex_implementation_components(cls, dmd):
        results = ICatalogTool(dmd).search(
            ('ZenPacks.zenoss.LinuxMonitor.LogicalVolume.LogicalVolume',
             'ZenPacks.zenoss.LinuxMonitor.SnapshotVolume.SnapshotVolume',)
        )

        for brain in results:
            obj = brain.getObject()
            obj.index_object()
            notify(IndexingEvent(obj))
