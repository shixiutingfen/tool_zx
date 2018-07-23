# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"
import logging, sys
from PyQt4.Qt import *
import datetime
from sloth.conf import config
from sloth.gui.frameviewer import GraphicsView
from sloth.gui import utils
from sloth.annotations.model import convertQPointFToModelItemKeyValues, getQRectFFromModelItem, getQLineFFromModelItem, getQPointFFromModelItem
from sloth.gui.utils import ROUND_VALUE
from sloth.items import RectItem, PointItem, LineItem

LOG = logging.getLogger(config.LOG_FILE_NAME)

# Reference:
# https://stackoverflow.com/questions/27890404/in-pyqt-image-wont-show-after-override-mousepressevent-of-qgraphicsview
"""
from sloth.gui.annotationscene import AnnotationScene
class override_AnnotationScene (AnnotationScene):
    # def __init__(self,parent = None):
    def __init__(self, labeltool, items=None, inserters=None, parent=None):
        super(override_AnnotationScene, self).__init__(labeltool, items, inserters, parent)

    def mousePressEvent(self, event):
        # handle the event as you like
        print "overide mousePressEvent ...event = {} scenePos = {}".format(event, event.scenePos())

        sceneRect = None if self._sceneViewMode == config.IMG_VIEW_MODE else self._objViewModeSceneRectWRTImg
        mindistance_modelitem, mindistance, mindistancec = findScenePositionClosetModelItem(self._image_item, self, sceneRect, event.scenePos())

        # then call default implementation
        if mindistance_modelitem:
            mindistance_modelitem.mousePressEvent(event)
            event.acept()

        super(override_AnnotationScene, self).mousePressEvent(event)
"""

# ================================================================
# zx comment: find model item whose scene position is closest to scenePos
# Usage:
# sceneRect = None if self._sceneViewMode == config.IMG_VIEW_MODE else self._objViewModeSceneRectWRTImg
# findScenePositionClosetModelItem(self._image_item, self._scene, sceneRect, event.scenePos())
# ================================================================
def findScenePositionClosetModelItem(parent_modelItem, scene, sceneRect, scenePos):
    mindistance = sys.maxint
    mindistancec = sys.maxint
    mindistance_modelitem = None
    if parent_modelItem:
        mindistance_modelitem, mindistance, mindistancec = _findClosetSceneItem(parent_modelItem, scene, sceneRect, scenePos, mindistance_modelitem, mindistance, mindistancec)
        # print "mindistance_modelitem = {} {}, mindistance = {}, mindistancec = {}".format(mindistance_modelitem.get_label_class(), mindistance_modelitem, mindistance, mindistancec)
    return mindistance_modelitem, mindistance, mindistancec

def _findClosetSceneItem(parent_modelItem, scene, sceneRect, scenePos, cur_mindistance_modelitem, cur_mindistance,
                         cur_mindistancec):
    first = 0
    last = parent_modelItem.rowCount() - 1
    sp = scenePos + (QPointF(0, 0) if sceneRect is None else sceneRect.topLeft())
    spx = sp.x()
    spy = sp.y()

    for row in range(first, last + 1):
        childModelItem = parent_modelItem.childAt(row)
        if not hasattr(childModelItem, 'get_label_class'):
            continue
        childModelItem_class = childModelItem.get_label_class()
        # print "Now check item {} ...".format(childModelItem_class)
        # if child.get_label_class() == targetClassName:
        #    found += [(child, iterativeLevelsNum)]

        childSceneItem = scene.modelItem_to_baseItem(childModelItem)
        if not childSceneItem:
            continue

        if isinstance(childSceneItem, RectItem):
            rect = getQRectFFromModelItem(childModelItem)
            if rect and rect.contains(sp):
                distance0 = (rect.x() - spx) ** 2 + (rect.y() - spy) ** 2
                distance1 = (rect.x() + rect.width() - 1 - spx) ** 2 + (rect.y() - spy) ** 2
                distance2 = (rect.x() - spx) ** 2 + (rect.y() + rect.height() - 1 - spy) ** 2
                distance3 = (rect.x() + rect.width() - 1 - spx) ** 2 + (rect.y() + rect.height() - 1 - spy) ** 2
                distance = min(distance0, distance1, distance2, distance3)
                cur_mindistance = min(distance, cur_mindistance)
                # print "Now check item {} distance {} cur_mindisatnce {}...".format(childModelItem_class, distance, cur_mindistance)
                if cur_mindistance == distance:
                    rectcenter = rect.center()
                    distancec = (rectcenter.x() - spx) ** 2 + (rectcenter.y() - spy) ** 2
                    cur_mindistancec = min(distancec, cur_mindistancec)
                    if cur_mindistancec == distancec:
                        cur_mindistance_modelitem = childModelItem

        if isinstance(childSceneItem, PointItem):
            point = getQPointFFromModelItem(childModelItem)
            if point:
                distance = (point.x() - spx) ** 2 + (point.y() - spy) ** 2
                cur_mindistance = min(distance, cur_mindistance)
                if cur_mindistance == distance:
                    cur_mindistance_modelitem = childModelItem

        if isinstance(childSceneItem, LineItem):
            line = getQLineFFromModelItem(childModelItem)
            if line:
                distance0 = (line.x1() - spx) ** 2 + (line.y1() - spy) ** 2
                distance1 = (line.x2() - spx) ** 2 + (line.y2() - spy) ** 2
                distance = min(distance0, distance1)
                cur_mindistance = min(distance, cur_mindistance)
                if cur_mindistance == distance:
                    cur_mindistance_modelitem = childModelItem

        # _iterativeLevelsNum = iterativeLevelsNum - 1
        # if _iterativeLevelsNum > 0
        if True:
            sub_mindistance_modelitem, sub_mindistance, sub_mindistancec = \
                _findClosetSceneItem(childModelItem, scene, sceneRect, scenePos, cur_mindistance_modelitem,
                                     cur_mindistance,
                                     cur_mindistancec)
            if sub_mindistance_modelitem is not None:
                if sub_mindistance < cur_mindistance:
                    cur_mindistance = sub_mindistance
                    cur_mindistancec = sub_mindistancec
                    cur_mindistance_modelitem = sub_mindistance_modelitem
                elif sub_mindistance == cur_mindistance and sub_mindistancec < cur_mindistancec:
                    cur_mindistancec = sub_mindistancec
                    cur_mindistance_modelitem = sub_mindistance_modelitem

    return cur_mindistance_modelitem, cur_mindistance, cur_mindistancec
