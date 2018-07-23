# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

import math
import time
from PyQt4.QtGui import *
from PyQt4.Qt import *
# from sloth.gui import AnnotationScene
from sloth.annotations.model import GET_ANNOTATION, findConnectSourceOfRectModelItemForRectModelItem, findConnectSourceOfRectModelItemForPointModelItem, ImageModelItem, findConnectSourceOfRectModelItemForSequenceModelItem
from sloth.annotations.model import findClosestParentRectModelItemForRectModelItem, findClosestParentRectModelItemForPointModelItem, findClosestParentRectModelItemForSequenceModelItem
from sloth.annotations.model import findConnectSourceOfRectModelItemForPolygonModelItem, findClosestParentRectModelItemForPolygonModelItem, convertQPolygonFToModelItemKeyValues, getQRectFFromModelItem, getQPointFFromModelItem, convertQRectFToModelItemKeyValues, convertQPointFToModelItemKeyValues, convertQLineFToModelItemKeyValues
import logging
from sloth.conf import config
from sloth.gui import utils



LOG = logging.getLogger(config.LOG_FILE_NAME)

class ItemInserter(QObject):
    """
    The base class for all item insertion handlers.
    """
    # Signals
    annotationFinished = pyqtSignal()
    inserterFinished = pyqtSignal()

    def __init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties=None,
                 prefix="", commit=True):
        QObject.__init__(self)
        self._labeltool = labeltool
        self._scene = scene
        self._default_properties = default_properties or {}
        # print "_default_properties = {}".format(GET_ANNOTATION(self._default_properties))
        self._prefix = prefix
        self._ann = {}
        self._commit = commit
        self._item = None   # display item. i.e.: sceneItem
        self._idName = idName
        self._signalObj = signalObj
        self._pen = QColor(Qt.red) # utils.colorStrToQtColor(self._default_properties.get(config.METADATA_DISPLAYCOLOR_TOKEN, None))
        self._parent_modelItem = None
        self._acceptDoubleClickEvent = True
        self._QRectBoundary = None
        self._enableRemoveSceneItemAfterInserted = True
        self._enableAddSceneItemWhenInserting = True
        self._enableEmitAnnotationFinishedSignal = True
        self._sceneRect = sceneRect
        self._idxInSequence = -1
        self._inserterFailedSignalObj = None
        self._itemPos = None
        
    def set_inserterFailedSignalObj(self, signalObj):
        self._inserterFailedSignalObj = signalObj;
           
    def set_idxInSequence(self, idxInSequence):
        self._idxInSequence = idxInSequence
        
    def cast_scence_pos(self, pt):
        sz = self._scene.currentImageSize()
        if(pt.x() < 0): pt.setX(0)
        if(pt.y() < 0): pt.setY(0)
        if(pt.x() > sz[0]-1): pt.setX(sz[0]-1)
        if(pt.y() > sz[1]-1): pt.setY(sz[1]-1)
        return pt

    def set_enableRemoveSceneItemAfterInserted(self, enabled = True):
        self._enableRemoveSceneItemAfterInserted = enabled

    def set_enableAddSceneItemWhenInserting(self, enabled = True):
        self._enableAddSceneItemWhenInserting = enabled

    def set_enableEmitAnnotationFinishedSignal(self, enabled = True):
        self._enableEmitAnnotationFinishedSignal = enabled
        
    def set_parent_modelItem(self, parentModeItem):
        self._parent_modelItem = parentModeItem

    def set_rectBoundaryWRTScene(self, qRrectF):
        self._QRectBoundary = qRrectF
        
    def set_acceptDoubleClickEvent(self, isEnabled = False):
        self._acceptDoubleClickEvent = isEnabled
    
    def annotation(self):
        return self._ann

    def item(self):
        return self._item
        
    def pos(self):
        return self._itemPos

    def pen(self):
        return self._pen

    def setPen(self, pen):
        self._pen = pen

    def mousePressEvent(self, event, image_item):
        event.accept()

    def mouseDoubleClickEvent(self, event, image_item):
        if self._acceptDoubleClickEvent :
            event.accept()

    def mouseReleaseEvent(self, event, image_item):
        event.accept()

    def mouseMoveEvent(self, event, image_item):
        event.accept()

    def keyPressEvent(self, event, image_item):
        event.ignore()

    def imageChange(self, flush = False, display = True):
        """
        Slot which gets called if the current image in the labeltool changes.
        """
        pass

    def allowOutOfSceneEvents(self):
        return False

    def abort(self):
        self.inserterFinished.emit()



class PointItemInserter(ItemInserter):
    def __init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties=None,
                 prefix="", commit=True):
        ItemInserter.__init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties,
                              prefix, commit)
        self._radius = 2
    
    def mousePressEvent(self, event, image_item):
        sp = event.scenePos()
        # ===========================================================
        # zx delete @ 20161020 for allowing out-of-image-boundary points
        # point = self.cast_scence_pos(sp)
        point = sp + ( QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft() )
        self._itemPos = point
        # ===========================================================
        
        LOG.debug("PointItemInserter: mousePressEvent: point = {} _sceneRect = {} point = {}".format(sp, self._sceneRect, point))
        qRectBoundary = self._QRectBoundary.translated(QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft()) if self._QRectBoundary else None
        parentModelItem = self._parent_modelItem
     
        LOG.debug("@@@@@@@@@ PointItemInserter: mouseReleaseEvent: parentModelItem.get_label_class = {} enableAutoConnectLabelMode = {}".format(parentModelItem.get_label_class() if parentModelItem else None, self._labeltool._enableAutoConnectLabelMode))
        if (self._labeltool._enableAutoConnectLabelMode):
            if (parentModelItem is None):
                parentModelItem = findConnectSourceOfRectModelItemForPointModelItem(point, self._idName, image_item)
                qRectBoundary   = getQRectFFromModelItem(parentModelItem)
            else:
                clowestParentModelItem = findClosestParentRectModelItemForPointModelItem(point, self._idName, parentModelItem)      
                LOG.debug("@@@@@@@@@ PointItemInserter: mouseReleaseEvent: getQRectFFromModelItem(clowestParentModelItem.name = {}) = {}".format(
                    clowestParentModelItem.get_label_class() if clowestParentModelItem else None, getQRectFFromModelItem(clowestParentModelItem) if clowestParentModelItem else None))
                parentModelItem = clowestParentModelItem
                qRectBoundary   = getQRectFFromModelItem(parentModelItem)
        
        
        # LOG.debug("@@@@@@@@@ PointItemInserter: mouseReleaseEvent: point = {} parentModelItem = {}".format(point, parentModelItem)
        
        isValid, rectBoundary = self._scene.checkModelItemValidity(self._idName, point, parentModelItem, image_item, enablePopupMsgBox = True, enableEmitStatusMsg = False, enableCountingThisModelItem = True)
        if not isValid:
            event.accept()
            self._item = None
            if (self._inserterFailedSignalObj is not None):
                self._inserterFailedSignalObj.emit(parentModelItem, self._idName)
            return
            
        self._ann.update(convertQPointFToModelItemKeyValues(point, self._prefix))
        self._ann.update(self._default_properties)
        
        if self._commit:
            image_item.addAnnotation(parentModelItem, self._ann)
            LOG.info("PointItemInserter.mousePressEvent: COMMIT ANNO {} and emit {}".format(self._ann, self._idName))
            if self._signalObj is not None:
                self._signalObj.emit(parentModelItem, self._idName) # zx ad @ 20161015

        self._item = QGraphicsEllipseItem(QRectF(sp.x() - self._radius,
                                          sp.y() - self._radius, 2 * self._radius, 2 * self._radius))

        self._item.setBrush(QBrush(Qt.red))
        self._item.setPen(self.pen())

        if self._enableAddSceneItemWhenInserting:
            LOG.info("=== PointItemInserter {} addItem {} to scene {} ....".format(self._idName, self._item, self._scene))
            self._scene.addItem(self._item)

        if self._enableEmitAnnotationFinishedSignal:
            self.annotationFinished.emit()         

        if self._enableRemoveSceneItemAfterInserted:
            LOG.info("=== PointItemInserter {} removeItem {} from scene {} ....".format(self._idName, self._item, self._scene))
            self._scene.removeItem(self._item)
            self._item = None

            
        event.accept()

    def allowOutOfSceneEvents(self):
        return True
        
        
    def abort(self):
        if self._item is not None:
            self._scene.removeItem(self._item)
            self._item = None
        ItemInserter.abort(self)



class RectItemInserter(ItemInserter):
    def __init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties=None,
                 prefix="", commit=True):
        ItemInserter.__init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties,
                              prefix, commit)
        self._init_pos = None
        self._hruler = None
        self._vruler = None


    def mousePressEvent(self, event, image_item):
        pos = event.scenePos()
        self._init_pos = pos
        self._item = QGraphicsRectItem(QRectF(pos.x(), pos.y(), 0, 0))
        self._item.setPen(self.pen())
        
        if self._enableAddSceneItemWhenInserting:
            self._scene.addItem(self._item)

        event.accept()

    def mouseMoveEvent(self, event, image_item):
        if self._item is not None:
            assert self._init_pos is not None
            rect = QRectF(self._init_pos, event.scenePos()).normalized()
            
            if self._QRectBoundary is not None:
                rect = rect.intersected(self._QRectBoundary)
                
            self._item.setRect(rect)
            
        # draw ruler
        pos = event.scenePos()
        ruler_pen = QPen(Qt.white)
        # ruler_pen.setStyle(Qt.DashLine)
        if(self._hruler is not None):
            self._scene.removeItem(self._hruler)
        if(self._vruler is not None):
            self._scene.removeItem(self._vruler)

        sz = self._scene.currentImageSize()
        self._hruler = QGraphicsLineItem(0, pos.y(), sz[0], pos.y())
        self._vruler = QGraphicsLineItem(pos.x(), 0, pos.x(), sz[1])
        self._hruler.setPen(ruler_pen)
        self._vruler.setPen(ruler_pen)
        self._scene.addItem(self._hruler)
        self._scene.addItem(self._vruler)
        event.accept()

    def mouseReleaseEvent(self, event, image_item):
        if self._item is not None:
            rect = self._item.rect()
            if (rect.width() >= config.GUI_RECT_MIN_WIDTH) and (rect.height() >= config.GUI_RECT_MIN_HEIGHT):
                
                tl = self.cast_scence_pos(rect.topLeft())
                br = self.cast_scence_pos(rect.bottomRight())
                br += QPointF(1, 1)  # bug fix @ 2017-06-21 for wrong QPointF.bottomRight()  definition 
                rect = QRectF(tl, br)
                rect = rect.translated(QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft())
                self._itemPos = rect
                # LOG.debug("RectItemInserter: mouseReleaseEvent: x = {} y = {} width = {} height = {}".format(tl.x(), tl.y(), rect.width(), rect.height())

                qRectBoundary = self._QRectBoundary.translated(QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft()) if self._QRectBoundary else None
                parentModelItem = self._parent_modelItem
                
                LOG.debug("@@@@@@@@@ parentModelItem.get_label_class = {} enableAutoConnectLabelMode = {}".format(parentModelItem.get_label_class() if parentModelItem else None, self._labeltool._enableAutoConnectLabelMode))
                if (self._labeltool._enableAutoConnectLabelMode):
                    if (parentModelItem is None):
                        parentModelItem = findConnectSourceOfRectModelItemForRectModelItem(rect, self._idName, image_item)
                        qRectBoundary   = getQRectFFromModelItem(parentModelItem)
                    else:
                        clowestParentModelItem = findClosestParentRectModelItemForRectModelItem(rect, self._idName, parentModelItem)
                        if clowestParentModelItem is None:
                            displayTextOfChild = config.getSpecificLabelInfo(self._idName, config.METADATA_DISPLAYTEXT_TOKEN)
                            msg = config.GUI_INSERT_ANNOTATION_NO_PARENT_TIP.format(displayTextOfChild)
                            QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
                            self._scene.removeItem(self._item)
                            self._item = None
                            return
                        LOG.debug("@@@@@@@@@ getQRectFFromModelItem(clowestParentModelItem.name = {}) = {}".format(clowestParentModelItem.get_label_class(), getQRectFFromModelItem(clowestParentModelItem)))
                        parentModelItem = clowestParentModelItem
                        qRectBoundary   = getQRectFFromModelItem(parentModelItem)

                    
                LOG.debug("@@@@@@@@@ getQRectFFromModelItem(parentModelItem) = {} rect = {}".format( getQRectFFromModelItem(parentModelItem), rect ))
                
                if (rect.width() > 0) and (rect.height() > 0):
                    isValid, rectBoundary = self._scene.checkModelItemValidity(self._idName, rect, parentModelItem, image_item, enablePopupMsgBox = True, enableEmitStatusMsg = False, enableCountingThisModelItem = True)
                    if not isValid:
                        self._scene.removeItem(self._item)
                        self._init_pos = None
                        self._item = None
                        event.accept()
                        if (self._inserterFailedSignalObj is not None):
                            self._inserterFailedSignalObj.emit(parentModelItem, self._idName)
                        return
                    
                    if rectBoundary:
                        rect = rect.intersected(rectBoundary)
                   
                    self._ann.update(convertQRectFToModelItemKeyValues(rect, self._prefix))
                    self._ann.update(self._default_properties)
                    
                    if self._commit:
                        LOG.info("self._parent_modelItem = {} parentModelItem = {} qRectBoundary = {}".format(self._parent_modelItem, parentModelItem, qRectBoundary))
                        image_item.addAnnotation(parentModelItem, self._ann)
                        if self._signalObj is not None:
                            self._signalObj.emit(parentModelItem, self._idName) # zx add @ 20161015
                        
            if self._enableEmitAnnotationFinishedSignal:     
                self.annotationFinished.emit()         
                             
            if self._enableRemoveSceneItemAfterInserted:                            
                 self._scene.removeItem(self._item)
                 self._item = None

            self._init_pos = None
            

        event.accept()

    def allowOutOfSceneEvents(self):
        return True

    def abort(self):
        if self._item is not None:
            self._scene.removeItem(self._item)
            self._item = None
        
        self._init_pos = None
        ItemInserter.abort(self)


class FixedRatioRectItemInserter(RectItemInserter):
    def __init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties=None,
                 prefix="", commit=True):
        RectItemInserter.__init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties,
                                  prefix, commit)
        self._ratio = float(default_properties.get('_ratio', 1))

    def mouseMoveEvent(self, event, image_item):
        if self._current_item is not None:
            new_geometry = QRectF(self._current_item.rect().topLeft(),
                                  event.scenePos())
            dx = new_geometry.width()
            dy = new_geometry.height()
            d = math.sqrt(dx * dx + dy * dy)
            r = self._ratio
            k = math.sqrt(r * r + 1)
            h = d / k
            w = d * r / k
            new_geometry.setWidth(w)
            new_geometry.setHeight(h)
            self._current_item.setRect(new_geometry.normalized())

        event.accept()


class SequenceItemInserter(ItemInserter):
    inserters = []

    def __init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties=None,
                 prefix="", commit=True):
        ItemInserter.__init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties,
                              prefix, commit)
        LOG.debug("=== create SequenceItemInserter ...")
        self._items = []   # display widget items
        self._itemsPos = [] # QPointF or QRectF
        self._state = 0
        self._current_inserter = None
        self._current_image_item = None

        self.nextState(0)

    def set_parent_modelItem(self, parentModeItem):
        self._parent_modelItem = parentModeItem
        if ( self._current_inserter is not None):
            self._current_inserter.set_parent_modelItem(parentModeItem)

    def set_rectBoundaryWRTScene(self, qRrectF):
        self._QRectBoundary = qRrectF
        if ( self._current_inserter is not None):
            self._current_inserter.set_rectBoundaryWRTScene(qRrectF)
        
    def _cleanup(self):
        LOG.debug("=== SequenceItemInserter._cleanup() ...")
        for item in self._items:
            if item.scene() is not None:
                self._scene.removeItem(item)
        self._items = []
        self._itemsPos = []
        self._scene.clearMessage()
        self._current_inserter = None

    def updateAnnotation(self, ann):
        LOG.debug("=== SequenceItemInserter.updateAnnotation() ...")
        self._ann.update(ann)

    def nextState(self, next_state=None):

        if self._current_inserter:
            state = self._current_inserter._idxInSequence
            next_state = state + 1
        else:
            next_state = 0
        orgState = self._state
        self._state = next_state
       
        if self._current_inserter is not None:
            self.updateAnnotation(self._current_inserter.annotation())
            item = self._current_inserter.item()
            if item is not None:
                self._scene.addItem(item)
                self._items.append(item)
                self._itemsPos.append(self._current_inserter.pos())

            self._current_inserter.annotationFinished.disconnect(self.nextState)

            if next_state >= len(self.inserters):
                # -----------------------------------------------------------------

                qRectBoundary = self._QRectBoundary.translated(QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft()) if self._QRectBoundary else None
                parentModelItem = self._parent_modelItem
                
                LOG.debug("@@@@@@@@@ SequenceItemInserter: mouseReleaseEvent: parentModelItem.get_label_class = {} enableAutoConnectLabelMode = {}".format(parentModelItem.get_label_class() if parentModelItem else None, self._labeltool._enableAutoConnectLabelMode))
                itemsPos =  self._itemsPos #[i.modelItem() for i in self._items]
                if (self._labeltool._enableAutoConnectLabelMode):
                    if (parentModelItem is None):
                        parentModelItem = findConnectSourceOfRectModelItemForSequenceModelItem(itemsPos, self._idName, self._image_item)
                        qRectBoundary   = getQRectFFromModelItem(parentModelItem)
                    else:
                        clowestParentModelItem = findClosestParentRectModelItemForSequenceModelItem(itemsPos, self._idName, parentModelItem)      
                        LOG.debug("@@@@@@@@@ SequenceItemInserter: mouseReleaseEvent: getQRectFFromModelItem(clowestParentModelItem.name = {}) = {}".format(clowestParentModelItem.get_label_class() if findClosestParentRectModelItemForSequenceModelItem else None, getQRectFFromModelItem(clowestParentModelItem) if findClosestParentRectModelItemForSequenceModelItem else None))
                        parentModelItem = clowestParentModelItem
                        qRectBoundary   = getQRectFFromModelItem(parentModelItem)
                
                # LOG.debug("@@@@@@@@@ SequenceItemInserter: mouseReleaseEvent: parentModelItem = {}".format(parentModelItem))
                
                # isValid, rectBoundary = self._scene.checkModelItemValidity(self._idName, itemsPos, parentModelItem, self._current_image_item, enablePopupMsgBox = True, enableEmitStatusMsg = False, enableCountingThisModelItem = True)
                # if not isValid:
                #     self._cleanup()
                #     next_state = 0
                #     if (self._inserterFailedSignalObj is not None):
                #         self._inserterFailedSignalObj.emit(parentModelItem, self._idName)
                # else:       
                if True:
                    self._ann.update(self._default_properties)
                
                    if self._commit:
                        self._current_image_item.addAnnotation(parentModelItem, self._ann)
                        LOG.info("@@@@@@@@@ SequenceItemInserter.mousePressEvent: COMMIT ANNO {} and emit {}".format(self._ann, self._idName))
                        if self._signalObj is not None:
                            self._signalObj.emit(parentModelItem, self._idName) # zx ad @ 20161015

                        self.annotationFinished.emit()
                
                # -----------------------------------------------------------------
                self._cleanup()
                next_state = 0

        callable_, prefix, message = self.inserters[next_state]
        LOG.debug("\n=== SequenceItemInserter.nextState() self._state = {} => {} {} self._current_inserter = {} anno = {}...".format(orgState, self._state, prefix, self._current_inserter, self._current_inserter.annotation() if self._current_inserter else None ))
        LOG.debug(u"=== Create callable_ {}  prefix {} message {}".format(callable_, prefix, message))
        self._current_inserter = callable_(self._idName, self._signalObj, self._labeltool, self._scene, self._sceneRect, prefix=prefix, commit=False)
        self._current_inserter.set_enableRemoveSceneItemAfterInserted(enabled = False)
        self._current_inserter.set_enableAddSceneItemWhenInserting(enabled = True)
        self._current_inserter.set_enableEmitAnnotationFinishedSignal(enabled = True)
        self._current_inserter.annotationFinished.connect(self.nextState)
        self._current_inserter.set_parent_modelItem(self._parent_modelItem)
        self._current_inserter.set_rectBoundaryWRTScene(self._QRectBoundary)
        self._current_inserter.set_idxInSequence(next_state)
        
        if message:
            self._scene.setMessage(message)
        else:
            self._scene.clearMessage()
        
        return
 
    def mousePressEvent(self, event, image_item):
        LOG.debug("=== SequenceItemInserter.mousePressEvent() _current_inserter {}...".format(self._current_inserter))
        self._current_image_item = image_item
        self._current_inserter.mousePressEvent(event, image_item)

    def mouseMoveEvent(self, event, image_item):
        # LOG.debug("=== SequenceItemInserter.mouseMoveEvent() ...")
        self._current_image_item = image_item
        self._current_inserter.mouseMoveEvent(event, image_item)

    def mouseReleaseEvent(self, event, image_item):
        LOG.debug("=== SequenceItemInserter.mouseReleaseEvent() ...")
        self._current_image_item = image_item
        self._current_inserter.mouseReleaseEvent(event, image_item)

    def keyPressEvent(self, event, image_item):
        self._current_image_item = image_item
        self._current_inserter.keyPressEvent(event, image_item)

    def abort(self):
        LOG.debug("=== SequenceItemInserter.abort() ...")
        self._cleanup()
        self.inserterFinished.emit()



class BBoxFaceInserter(SequenceItemInserter):
    inserters = [
        (RectItemInserter,  config.ANNOTATION_LABELLING_BBOX_TOKEN,    "Labelling bounding box"),
        (PointItemInserter, config.ANNOTATION_LEFT_EYE_CENTER_TOKEN,   "Labelling left eye center"),
        (PointItemInserter, config.ANNOTATION_RIGHT_EYE_CENTER_TOKEN,  "Labelling right eye center"),
        (PointItemInserter, config.ANNOTATION_MOUTH_CENTER_TOKEN,      "Labelling mouth center") ]


    def toggleOccludedForCurrentInserter(self):
        if self._state > 0:
            prefix = self.inserters[self._state][1]
            occluded = not self._current_inserter._ann.get(prefix + 'occluded', False)
            self._current_inserter._ann[prefix + 'occluded'] = occluded
            if occluded:
                self._scene.setMessage(self.inserters[self._state][2] + ' (occluded)')
            else:
                self._scene.setMessage(self.inserters[self._state][2])

    def mousePressEvent(self, event, image_item):
        if event.buttons() & Qt.RightButton:
            self.toggleOccludedForCurrentInserter()
        SequenceItemInserter.mousePressEvent(self, event, image_item)

    def keyPressEvent(self, event, image_item):
        if event.key() == Qt.Key_O and self._state > 0:
            self.toggleOccludedForCurrentInserter()
            return
        elif Qt.Key_0 <= event.key() <= Qt.Key_9 or Qt.Key_A <= event.key() <= Qt.Key_Z:
            if Qt.Key_0 <= event.key() <= Qt.Key_9:
                self._ann['id'] = int(str(event.text()))
            else:
                self._ann['id'] = ord(str(event.text()).upper()) - 65 + 10
            message = self._scene._message
            if message is None:
                message = ""
            self._scene.setMessage(message + "\nSet id to %d." % self._ann['id'])
            return
        SequenceItemInserter.keyPressEvent(self, event, image_item)

    def imageChange(self, flush = False, display = True):
        if self._state > 0:
            # restart the inserter
            self._cleanup()
            self.nextState(0)
            self._scene.setMessage("<b>Warning</b>: Image changed during insert operation.\n" +
                                   "Resetting the inserter state.\n" +
                                   "Now at: " + self.inserters[self._state][2])


class NPointFaceInserter(SequenceItemInserter):
    inserters = [
#           (PointItemInserter, config.ANNOTATION_LEFT_EYE_OUTER_CORNER_TOKEN ,  config.LEFT_EYE_OUTER_CORNER_DISPLAYTEXT),
#           (PointItemInserter, config.ANNOTATION_LEFT_EYE_INNER_CORNER_TOKEN ,  config.LEFT_EYE_INNER_CORNER_DISPLAYTEXT),
#           (PointItemInserter, config.ANNOTATION_RIGHT_EYE_INNER_CORNER_TOKEN,  config.RIGHT_EYE_INNER_CORNER_DISPLAYTEXT),
#           (PointItemInserter, config.ANNOTATION_RIGHT_EYE_OUTER_CORNER_TOKEN,  config.RIGHT_EYE_OUTER_CORNER_DISPLAYTEXT),
#           (PointItemInserter, config.ANNOTATION_NOSE_TIP_TOKEN              ,  config.NOSE_TIP_DISPLAYTEXT),
#           (PointItemInserter, config.ANNOTATION_UPPER_LIP_CENTER_TOKEN      ,  config.UPPER_LIP_CENTER_DISPLAYTEXT),
            (PointItemInserter, config.ANNOTATION_LEFT_EYE_CENTER_TOKEN       ,  config.LEFT_EYE_CENTER_DISPLAYTEXT),
            (PointItemInserter, config.ANNOTATION_RIGHT_EYE_CENTER_TOKEN      ,  config.RIGHT_EYE_CENTER_DISPLAYTEXT),
            (PointItemInserter, config.ANNOTATION_NOSE_TIP_TOKEN              ,  config.NOSE_TIP_DISPLAYTEXT),
            (PointItemInserter, config.ANNOTATION_LEFT_MOUTH_CORNER_TOKEN     ,  config.LEFT_MOUTH_CORNER_DISPLAYTEXT),
            (PointItemInserter, config.ANNOTATION_RIGHT_MOUTH_CORNER_TOKEN    ,  config.RIGHT_MOUTH_CORNER_DISPLAYTEXT),
    ]

    def toggleOccludedForCurrentInserter(self):
        prefix = self.inserters[self._state][1]
        occluded = not self._current_inserter._ann.get(prefix + 'occluded', False)
        self._current_inserter._ann[prefix + 'occluded'] = occluded
        if occluded:
            self._scene.setMessage(self.inserters[self._state][2] + ' (occluded)')
            self._current_inserter.setPen(Qt.red)
        else:
            self._scene.setMessage(self.inserters[self._state][2])
            self._current_inserter.setPen(Qt.yellow)

    def mousePressEvent(self, event, image_item):
        if event.buttons() & Qt.RightButton:
            self.toggleOccludedForCurrentInserter()
        SequenceItemInserter.mousePressEvent(self, event, image_item)

    def keyPressEvent(self, event, image_item):
        if event.key() == Qt.Key_O:
            self.toggleOccludedForCurrentInserter()
        SequenceItemInserter.keyPressEvent(self, event, image_item)

    def imageChange(self, flush = False, display = True):
        if self._state > 0:
            # restart the inserter
            self._cleanup()
            self.nextState(0)
            self._scene.setMessage("<b>Warning</b>: Image changed during insert operation.\n" +
                                   "Resetting the inserter state.\n" +
                                   "Now at: " + self.inserters[self._state][2])


class PolygonItemInserter(ItemInserter):
    def __init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties=None,
                 prefix="", commit=True):
        ItemInserter.__init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties,
                              prefix, commit)
        self._item = None

    def _removeLastPointAndFinish(self, image_item):
        polygon = self._item.polygon()
        polygon.remove(polygon.size()-1)
        assert polygon.size() > 0
        self._item.setPolygon(polygon)
        self._itemPos = polygon
        
        self._updateAnnotation()
        if self._commit:
            image_item.addAnnotation(self._parent_modelItem, self._ann)
            if self._signalObj is not None:
                self._signalObj.emit(self._parent_modelItem, self._idName) # zx ad @ 20161015
        self._scene.removeItem(self._item)
        self.annotationFinished.emit()
        self._item = None
        self._scene.clearMessage()

        self.inserterFinished.emit()

    def mousePressEvent(self, event, image_item):
        pos = event.scenePos()

        if self._item is None:
            item = QGraphicsPolygonItem(QPolygonF([pos]))
            self._item = item
            self._item.setPen(self.pen())
            self._scene.addItem(item)

            self._scene.setMessage("Press Enter to finish the polygon.")

        polygon = self._item.polygon()
        polygon.append(pos)
        self._item.setPolygon(polygon)

        event.accept()

    def mouseDoubleClickEvent(self, event, image_item):
        """Finish the polygon when the user double clicks."""

        # No need to add the position of the click, as a single mouse
        # press event added the point already.
        # Even then, the last point of the polygon is duplicate as it would be
        # shortly after a single mouse press. At this point, we want to throw it
        # away.
        self._removeLastPointAndFinish(image_item)

        if self._acceptDoubleClickEvent :
            event.accept()


    def mouseMoveEvent(self, event, image_item):
        if self._item is not None:
            pos = event.scenePos()
            polygon = self._item.polygon()
            assert polygon.size() > 0
            polygon[-1] = pos
            self._item.setPolygon(polygon)

        event.accept()

    def keyPressEvent(self, event, image_item):
        """
        When the user presses Enter, the polygon is finished.
        """
        if event.key() == Qt.Key_Return and self._item is not None:
            # The last point of the polygon is the point the user would add
            # to the polygon when pressing the mouse button. At this point,
            # we want to throw it away.
            self._removeLastPointAndFinish(image_item)

    def abort(self):
        if self._item is not None:
            self._scene.removeItem(self._item)
            self._item = None
            self._scene.clearMessage()
        ItemInserter.abort(self)

    def _updateAnnotation(self):
        polygon = self._item.polygon()
        self._ann.update({self._prefix + 'xn':
                              ";".join([str(p.x()) for p in polygon]),
                          self._prefix + 'yn':
                              ";".join([str(p.y()) for p in polygon])})
        self._ann.update(self._default_properties)
        
        
# zx added @ 2016-07-28
class LineItemInserter(ItemInserter):
    def __init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties=None,
                 prefix="", commit=True):
        ItemInserter.__init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties,
                              prefix, commit)
        self._init_pos = None
        self._hruler = None
        self._vruler = None


    def mousePressEvent(self, event, image_item):
        # LOG.info("LineItemInserter.mousePressEvent line  ...")
        pos = event.scenePos()
        self._init_pos = pos
        self._item = QGraphicsLineItem(QLineF(pos.x(), pos.y(), pos.x(), pos.y()))
        self._item.setPen(self.pen())

        if self._enableAddSceneItemWhenInserting:
            self._scene.addItem(self._item)

        event.accept()

    def mouseMoveEvent(self, event, image_item):
        if self._item is not None:
            assert self._init_pos is not None
            line = QLineF(self._init_pos, event.scenePos())
            self._item.set(line)
        # draw ruler
        pos = event.scenePos()
        ruler_pen = QPen(Qt.white)
        # ruler_pen.setStyle(Qt.DashLine)
        if(self._hruler is not None):
            self._scene.removeItem(self._hruler)
        if(self._vruler is not None):
            self._scene.removeItem(self._vruler)

        sz = self._scene.currentImageSize()
        self._hruler = QGraphicsLineItem(0, pos.y(), sz[0], pos.y())
        self._vruler = QGraphicsLineItem(pos.x(), 0, pos.x(), sz[1])
        self._hruler.setPen(ruler_pen)
        self._vruler.setPen(ruler_pen)
        self._scene.addItem(self._hruler)
        self._scene.addItem(self._vruler)
        event.accept()

    def updateAnnoPos(self, qLineF):
        self._ann.update(convertQRectFToModelItemKeyValues(qLineF + QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft(), self._prefix))


    def mouseReleaseEvent(self, event, image_item):
        
        if self._item is not None:
            # LOG.info("mouseReleaseEvent: _item %s line (%f, %f) (%f %f)" % (self._item, self._item.line().p1().x(), self._item.line().p1().y(), self._item.line().p2().x(), self._item.line().p2().y()))
            
            if self._item.line().length() > config.GUI_LINE_MIN_LENGTH:
                line = self._item.line()
                # LOG.info("currentImageSize {}".format(self._scene.currentImageSize()))
                
                # ===========================================================
                # zx delete @ 20161020 for allowing out-of-image-boundary points
                # p1 = self.cast_scence_pos(line.p1())
                # p2 = self.cast_scence_pos(line.p2())
                aline = line
                self._itemPos = aline
                # ===========================================================                
                
                self.updateAnnoPos(aline)

                self._ann.update(self._default_properties)
                if self._commit:
                    image_item.addAnnotation(self._parent_modelItem, self._ann)
                    # LOG.info("LineItemInserter.mouseReleaseEvent: COMMIT ANNO {} and emit {}".format(self._ann, self._idName))
                    if self._signalObj is not None:
                        self._signalObj.emit(self._parent_modelItem, self._idName) # zx ad @ 20161015
            
            if self._enableEmitAnnotationFinishedSignal:     
                self.annotationFinished.emit()
                
            if self._enableRemoveSceneItemAfterInserted:            
                self._scene.removeItem(self._item)
                self._item = None
                
            self._init_pos = None
            
        event.accept()

    def allowOutOfSceneEvents(self):
        return True

    def abort(self):
        if self._item is not None:
            self._scene.removeItem(self._item)
            self._item = None
        self._init_pos = None
        ItemInserter.abort(self)


class UpRightLineItemInserter(LineItemInserter):
    def __init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties=None,
                 prefix="", commit=True):
        LineItemInserter.__init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties,
                                  prefix, commit)

    def mouseMoveEvent(self, event, image_item):
        pos = event.scenePos()
        if self._item is not None:
            assert self._init_pos is not None
            if pos.y() < self._init_pos.y():
                 return
            pos.setX(self._init_pos.x())
            # print "ajust to pos = ", pos
            line = QLineF(self._init_pos, pos)
            # print "now line = ", line
            self._item.setLine(line)
        # draw ruler
        ruler_pen = QPen(Qt.white)
        # ruler_pen.setStyle(Qt.DashLine)
        if(self._hruler is not None):
            self._scene.removeItem(self._hruler)
        if(self._vruler is not None):
            self._scene.removeItem(self._vruler)

        sz = self._scene.currentImageSize()
        # print "now pos = ", pos
        self._hruler = QGraphicsLineItem(0, pos.y(), sz[0], pos.y())
        self._vruler = QGraphicsLineItem(pos.x(), 0, pos.x(), sz[1])
        self._hruler.setPen(ruler_pen)
        self._vruler.setPen(ruler_pen)
        self._scene.addItem(self._hruler)
        self._scene.addItem(self._vruler)
        event.accept()


class QuadrangleItemInserter(PolygonItemInserter):
    def __init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties=None,
                 prefix="", commit=True):
        ItemInserter.__init__(self, idName, signalObj, labeltool, scene, sceneRect, default_properties,
                              prefix, commit)
        self._item = None
        self._hruler = None
        self._vruler = None
        
        
    def _removeLastPointAndFinish(self, image_item):
    
        self._scene.clearMessage()
        
        polygon = self._item.polygon()
        polygon.remove(polygon.size()-1)
        assert polygon.size() > 0
        self._item.setPolygon(polygon)
       
        # =================  
        polygon = polygon.translated(QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft())
        self._itemPos = polygon

        qRectBoundary = self._QRectBoundary.translated(QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft()) if self._QRectBoundary else None
        parentModelItem = self._parent_modelItem
        
        # print "qRectBoundary = {}".format(qRectBoundary)
        
        LOG.debug("@@@@@@@@@ parentModelItem = {}, {} enableAutoConnectLabelMode = {}".format(GET_ANNOTATION(parentModelItem) if parentModelItem else None,  parentModelItem.get_label_class() if parentModelItem else None, self._labeltool._enableAutoConnectLabelMode))
        if (self._labeltool._enableAutoConnectLabelMode):
            if (parentModelItem is None):
                parentModelItem = findConnectSourceOfRectModelItemForPolygonModelItem(polygon, self._idName, image_item)
                qRectBoundary   = getQRectFFromModelItem(parentModelItem)
            else:
                clowestParentModelItem = findClosestParentRectModelItemForPolygonModelItem(polygon, self._idName, parentModelItem)
                if clowestParentModelItem is None:
                    displayTextOfChild = config.getSpecificLabelInfo(self._idName, config.METADATA_DISPLAYTEXT_TOKEN)
                    msg = config.GUI_INSERT_ANNOTATION_NO_PARENT_TIP.format(displayTextOfChild)
                    QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
                    self._scene.removeItem(self._item)
                    self._item = None
                    return
                LOG.debug("@@@@@@@@@ getQRectFFromModelItem(clowestParentModelItem.name = {}) = {}".format(clowestParentModelItem.get_label_class(), getQRectFFromModelItem(clowestParentModelItem)))
                parentModelItem = clowestParentModelItem
                qRectBoundary   = getQRectFFromModelItem(parentModelItem)
        
        LOG.debug("@@@@@@@@@ getQRectFFromModelItem(parentModelItem) = {} polygon = {}".format( getQRectFFromModelItem(parentModelItem), polygon ))

        brect = polygon.boundingRect()
        if (brect.width() > 0 and brect.height() > 0):
            isValid, rectBoundary = self._scene.checkModelItemValidity(self._idName, polygon, parentModelItem, image_item, enablePopupMsgBox = True, enableEmitStatusMsg = False, enableCountingThisModelItem = True)
            if not isValid:
                self._scene.removeItem(self._item)
                self._item = None
                if (self._inserterFailedSignalObj is not None):
                    self._inserterFailedSignalObj.emit(parentModelItem, self._idName)
                return

            if rectBoundary:
                # print "qRectBoundary = {}  rectBoundary = {}".format(qRectBoundary, rectBoundary)
                polygon = polygon.intersected(rectBoundary)
            
            
            self._ann.update(convertQPolygonFToModelItemKeyValues(polygon, self._prefix))
            self._ann.update(self._default_properties)
            self.inserterFinished.emit()
            
            if self._commit:
                LOG.info("Inserter {} commit anno {} to parentModelItem = {} qRectBoundary = {}".format(self._idName,  self._ann, parentModelItem, qRectBoundary))
                image_item.addAnnotation(parentModelItem, self._ann)
                if self._signalObj is not None:
                    self._signalObj.emit(parentModelItem, self._idName) # zx add @ 20161015
            
                
            if self._enableEmitAnnotationFinishedSignal:     
                self.annotationFinished.emit()         
                             
        if self._enableRemoveSceneItemAfterInserted:                            
             self._scene.removeItem(self._item)
             self._item = None
             

        # =================
        
 
    def mousePressEvent(self, event, image_item):
        pos = event.scenePos()

        if self._item is None:
            item = QGraphicsPolygonItem(QPolygonF([pos]))
            self._item = item
            self._item.setPen(self.pen())
            self._scene.addItem(item)

 
        polygon = self._item.polygon()
        polygon.append(pos)
        self._item.setPolygon(polygon)
       
        if len(polygon) == 5:
            self._removeLastPointAndFinish(image_item)
        else:
            self._scene.setMessage(config.GUI_ADD_ONE_MORE_VERTEX_MESSAGE) 
        

        event.accept()
                

    def mouseDoubleClickEvent(self, event, image_item):
    	pass
    	
        """Finish the polygon when the user double clicks."""

        # No need to add the position of the click, as a single mouse
        # press event added the point already.
        # Even then, the last point of the polygon is duplicate as it would be
        # shortly after a single mouse press. At this point, we want to throw it
        # away.
        self._removeLastPointAndFinish(image_item)

        if self._acceptDoubleClickEvent :
            event.accept()


    def mouseMoveEvent(self, event, image_item):
        if self._item is not None:
            pos = event.scenePos()
            polygon = self._item.polygon()
            assert polygon.size() > 0
            polygon[-1] = pos
            self._item.setPolygon(polygon)
            
        # draw ruler
        pos = event.scenePos()
        ruler_pen = QPen(Qt.white)
        # ruler_pen.setStyle(Qt.DashLine)
        if(self._hruler is not None):
            self._scene.removeItem(self._hruler)
        if(self._vruler is not None):
            self._scene.removeItem(self._vruler)

        sz = self._scene.currentImageSize()
        self._hruler = QGraphicsLineItem(0, pos.y(), sz[0], pos.y())
        self._vruler = QGraphicsLineItem(pos.x(), 0, pos.x(), sz[1])
        self._hruler.setPen(ruler_pen)
        self._vruler.setPen(ruler_pen)
        self._scene.addItem(self._hruler)
        self._scene.addItem(self._vruler)

        event.accept()

    def keyPressEvent(self, event, image_item):
        """
        When the user presses Enter, the polygon is finished.
        """
        if event.key() == Qt.Key_Return and self._item is not None:
            # The last point of the polygon is the point the user would add
            # to the polygon when pressing the mouse button. At this point,
            # we want to throw it away.
            self._removeLastPointAndFinish(image_item)

    def abort(self):
        if self._item is not None:
            self._scene.removeItem(self._item)
            self._item = None
            self._scene.clearMessage()
        ItemInserter.abort(self)

    def _updateAnnotation(self):
        polygon = self._item.polygon()
        self._ann.update({self._prefix + 'xn':
                              ";".join([str(p.x()) for p in polygon]),
                          self._prefix + 'yn':
                              ";".join([str(p.y()) for p in polygon])})
        self._ann.update(self._default_properties)