# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

"""This is the AnnotationScene module"""
from sloth.items import *
from sloth.core.exceptions import InvalidArgumentException
from sloth.annotations.model import AnnotationModelItem, GET_ANNOTATION, findModelItemsWithSpecificClassName
from sloth.annotations.model import getQRectFFromModelItem, getQLineFFromModelItem, getQPointFFromModelItem, convertQRectFToModelItemKeyValues, convertQPointFToModelItemKeyValues
from sloth.utils import toQImage
from sloth.conf import config
from PyQt4.QtCore import *
from sloth.gui import attrArea
import logging, os
import functools
import fnmatch
import numpy as np
import datetime
import copy
from sloth.items.overideGraphicsScene import findScenePositionClosetModelItem

LOG = logging.getLogger(config.LOG_FILE_NAME)
GUIDIR=os.path.join(os.path.dirname(__file__))
SELECTED_DISPLAYED_ITEMS_LIST_MODELITEM_INDEX      = 1
SELECTED_DISPLAYED_ITEMS_LIST_ITEMLABELCLASS_INDEX = 0


class AnnotationScene(QGraphicsScene):
    mousePositionChanged = pyqtSignal(float, float)
    modeChanged = pyqtSignal(int)
    deleteItmOfZeroSizeSignal = pyqtSignal(object)
    itemIsInsertedOrSelected = pyqtSignal(float, float, int)
    itemIsAddedToScene = pyqtSignal(object)
    inserterFailed = pyqtSignal(object, str)
        
    def __init__(self, labeltool, items=None, inserters=None, parent=None):
        super(AnnotationScene, self).__init__(parent)

        self._model = None
        self._image_item = None
        self._inserter = None
        self._selectedDisplayItemsList = [] # format: [ [selected_item_name, selected_item_modelItem], ... ]
        self._scene_item = None
        self._message = ""
        self._labeltool = labeltool

        self._itemfactory = Factory(items)
        self._inserterfactory = Factory(inserters)
        self._img_pixmap = None
        
        # zx999
        self._mouseSingleClickTimer = QTimer()
        self._mouseSingleClickTimer.timeout.connect(self.onMouseSingleClicked)
        self._mouseSingleClickTimer.setSingleShot(True)

        try:
            self.setBackgroundBrush(config.SCENE_BACKGROUND)
        except:
            self.setBackgroundBrush(Qt.darkGray)
        
        self._mouseIsMove = False
        
        self.deleteItmOfZeroSizeSignal.connect(self.deleteItemOfZeroSize)
        self.inserterFailed.connect(self.onInserterFailed)
        self.itemIsAddedToScene.connect(self.onItemIsAddedToScene)
        
        self._topObjModelItem = None
        self._mousePressClosestSceneItem = None
        self.reset()

    
    def isInsertingMode(self):
        if self._inserter:
            insertingEditorCnt = [i.isInsertingMode() for i in self._labeltool.propertyeditors() if i].count(True)
            if insertingEditorCnt <= 0:
                print "Error: currently we are in inserting mode but there is no any inserters is valid!"
            return True
        else:
            insertingEditorCnt = [i.isInsertingMode() for i in self._labeltool.propertyeditors() if i].count(True)
            # if insertingEditorCnt > 0:
            #    print "Error: currently we are in editing mode but there is {} inserters are valid!".format(insertingEditorCnt)
            return False
            
        return self._current_is_insert_mode
    
    # =====================================================================================================
    # When any button or checkbox in any pannel is selected or deselected, this function will be called
    # e.g.
    # - When one of upper color tags is selected or deselected, this function will be called with : 
    #   checkedAttrsDescDict = {'uppercolor': [{'hotkey': '', 'rgb': '#00FDFF', 'tag': 'Cyan',   'displaytext': u'\u9752'}, 
    #                                   {'hotkey': '', 'rgb': '#FF2600', 'tag': 'Red',    'displaytext': u'\u7ea2'}, 
    #                                   {'hotkey': '', 'rgb': '#FFFF00', 'tag': 'Yellow', 'displaytext': u'\u9ec4'}]}
    # =====================================================================================================
    def onAttrChanged(self, attrBelongingObjClassName, checkedAttrsDescDict):
    
        attrBelongingObjClassName = str(attrBelongingObjClassName)
        # LOG.info("onAttrChanged({}, {})... self.selectedItems() = {}".format(attrBelongingObjClassName, checkedAttrsDescDict, self.selectedItems()))
        # print "onAttrChanged({}, {})... self.selectedItems() = {}".format(attrBelongingObjClassName, checkedAttrsDescDict, self.selectedItems())
        
        selectedSceneItems = self.selectedItems()
        # print "attrBelongingObjClassName = {} checkedAttrsDescDict = {} selectedSceneItems = {}".format(attrBelongingObjClassName, checkedAttrsDescDict, selectedSceneItems)
        
        if not selectedSceneItems:
            parentModelItem = self._objViewModeTopModelItem if self._sceneViewMode == config.OBJ_VIEW_MODE else None
            # print "onAttrChanged objViewMode ... parentModelItem = {}".format(parentModelItem.get_label_class())
            if parentModelItem:
                selectedSceneItems = []
                selectedSceneItems.append(self.modelItem_to_baseItem(parentModelItem))
                parentClass = parentModelItem.get_label_class()
                allowedChildrenClass = config.ALLOWED_DISPLAY_OBJECTS_AND_ATTRIBUTE_STICKERS.get(parentClass, None)
                if allowedChildrenClass:
                    for childClass in allowedChildrenClass:
                        foundModelItemsAndIterativeLevelsNum = findModelItemsWithSpecificClassName(childClass, parentModelItem)
                        if foundModelItemsAndIterativeLevelsNum:
                            selectedSceneItems += [ self.modelItem_to_baseItem(i[0]) for i in foundModelItemsAndIterativeLevelsNum]

        # print "onAttrChanged with checkedAttrsDescDict = {}... selectedSceneItems() = {}".format(checkedAttrsDescDict, [i.get_label_class() for i in selectedSceneItems])
        
        if not checkedAttrsDescDict:
            checkedAttrsDescDict[attrBelongingObjClassName] = ""

        # print "checkedAttrsDescDict = {}".format(checkedAttrsDescDict)
        for attrsClsName, attrsInfo in checkedAttrsDescDict.items():


            objClassNameList = config.ATTRIBUTE_RELATE_TO_OBJECT_KEYVALUE_RELATIONSHIP.get(attrsClsName, None)
            # print "attrsClsName = {} objClassNameList = {}".format(attrsClsName, objClassNameList)
            
            done = False
            
            # ------------------------------------------------------------------------------------------------
            # find object from selected scene items which has indirect relationship with changed attributes
            # ------------------------------------------------------------------------------------------------
            for objClassName in objClassNameList:
                if objClassName:
                    parentObjsClassNameList = config.CHILDOBJ_TO_OBJ_DICT.get(objClassName, None)
                    # print "objClassName = {} parentObjsClassNameList = {}".format(objClassName, parentObjsClassNameList)
                    if parentObjsClassNameList:
                        for sitem in selectedSceneItems:
                            if sitem:
                                lc = sitem.get_label_class()
                                lc = lc if lc is not None else ""
                                # LOG.info("onAttrChanged... item {} itemclass {}...".format(sitem, lc))
                                # print ("3 onAttrChanged... thisSelectedItem {}...".format(lc))
                                if lc in parentObjsClassNameList:
                                    foundModelItemsAndIterativeLevelsNumList = findModelItemsWithSpecificClassName(objClassName, sitem.modelItem(), 5)
                                    if not foundModelItemsAndIterativeLevelsNumList:
                                        continue
                                    """
                                    if (foundModelItemsAndIterativeLevelsNumList[0][0].get_label_class() == 'pedestrain' and  attrBelongingObjClassName == 'lowercolor'):
                                        foundModelItemsAndIterativeLevelsNumList_new = findModelItemsWithSpecificClassName('lower', sitem.modelItem(), 5)
                                        if foundModelItemsAndIterativeLevelsNumList_new:
                                            LOG.info("2 modelitem is changed from {} => {}...".format(foundModelItemsAndIterativeLevelsNumList[0][0].get_label_class(), foundModelItemsAndIterativeLevelsNumList_new[0][0].get_label_class()))
                                            foundModelItemsAndIterativeLevelsNumList = foundModelItemsAndIterativeLevelsNumList_new 
                                    """
                                    targetSceneItem = self.modelItem_to_baseItem(foundModelItemsAndIterativeLevelsNumList[0][0])
                                    # LOG.info("2 addAttrStickers for {} {} with {} : {}...".format(foundModelItemsAndIterativeLevelsNumList[0][0].get_label_class(), attrBelongingObjClassName, attrsClsName, attrsInfo))
                                    targetSceneItem.addAttrStickers(attrBelongingObjClassName, checkedAttrsDescDict, True )
                                    done = True

                                # --------------- [ TBC START ] --------------------------
                                """
                                if ( (lc == config.ANNOTATION_UPPER_TOKEN) and any([(ANNOTATION_PEDESTRAIN_TOKEN == i) or (ANNOTATION_PERSONBIKE_TOKEN == i) for i in parentObjsClassNameList]) ) or
                                   ( (lc == config.ANNOTATION_LOWER_TOKEN) and any([(ANNOTATION_PEDESTRAIN_TOKEN == i) for i in parentObjsClassNameList]) ):
                                    foundModelItemsAndIterativeLevelsNumList = findParentModelItemsWithSpecificClassName(parentObjClassName, sitem.modelItem(), 1)   
                                    if not foundModelItemsAndIterativeLevelsNumList:
                                        continue
                                    targetSceneItem = self.modelItem_to_baseItem(foundModelItemsAndIterativeLevelsNumList[0][0])
                                    LOG.info("addAttrStickers for {} {} with {} : {}...".format(foundModelItemsAndIterativeLevelsNumList[0][0].get_label_class(), attrBelongingObjClassName, attrsClsName, attrsInfo))
                                    # print ("2 addAttrStickers for {} {} with {} : {}...".format(foundModelItemsAndIterativeLevelsNumList[0][0].get_label_class(), attrBelongingObjClassName, attrsClsName, attrsInfo))
                                    targetSceneItem.addAttrStickers(attrBelongingObjClassName, checkedAttrsDescDict, True )
                                """
                                # --------------- [ TBC END  ] --------------------------

            # ------------------------------------------------------------------------------------------------
            # find object from selected scene items which has direct relationship with changed attributes
            # ------------------------------------------------------------------------------------------------
            if done: continue
            
            for objClassName in objClassNameList:
                if objClassName:
                    for sitem in selectedSceneItems:
                        if sitem:
                            lc = sitem.get_label_class()
                            lc = lc if lc is not None else ""
                            # LOG.info("onAttrChanged... item {} itemclass {}...".format(sitem, lc))
                            if (lc == objClassName):
                                # LOG.info("1 addAttrStickers for {} {} with {} - {}...".format(lc, attrBelongingObjClassName, attrsClsName, attrsInfo))
                                sitem.addAttrStickers(attrBelongingObjClassName, checkedAttrsDescDict, True )


        if config.ENABLE_STATISTIC_OBJ_INFO:
            self._labeltool._mainwindow.objViewModeInfoWidget.update(GET_ANNOTATION(self._objViewModeTopModelItem) if self._objViewModeTopModelItem else None)
        
        return
   
    def currentImageSize(self):
        if(self._img_pixmap == None):
            return [-1,-1]
        return [self._img_pixmap.width(), self._img_pixmap.height()]

    #
    # getters/setters
    #______________________________________________________________________________________________________
    def setModel(self, model):
        LOG.info("setModel... model = {} self._model = {}...".format(model, self._model))
        if model == self._model:
            # same model as the current one
            # reset caches anyway, invalidate root
            self.reset()
            return

        # disconnect old signals
        if self._model is not None:
            self._model.dataChanged.disconnect(self.dataChanged)
            self._model.rowsInserted.disconnect(self.rowsInserted)
            self._model.rowsAboutToBeRemoved.disconnect(self.rowsAboutToBeRemoved)
            self._model.rowsRemoved.disconnect(self.rowsRemoved)
            self._model.modelReset.disconnect(self.reset)

        self._model = model

        # connect new signals
        if self._model is not None:
            self._model.dataChanged.connect(self.dataChanged)
            self._model.rowsInserted.connect(self.rowsInserted)
            self._model.rowsAboutToBeRemoved.connect(self.rowsAboutToBeRemoved)
            self._model.rowsRemoved.connect(self.rowsRemoved)
            self._model.modelReset.connect(self.reset)

        # reset caches, invalidate root
        self.reset()


    def sceneItem(self):
        return self._scene_item


    def get_objViewModeInfo(self, current_img_item):
       idx = self._objViewModeTopModelItemRowIdxInParent
       num = current_img_item.rowCount() if current_img_item else -1
             
       if (idx < 0) or (idx >= num):
           LOG.info("get_objViewModeInfo... idx = {} num = {}".format(idx, num))
           return (-1, -1)
       
       minum = 0
       miidx = 0
       for i in range(num):
          if isinstance( current_img_item.childAt(i), AnnotationModelItem):
              minum += 1
              if i <= idx:
                  miidx += 1
                  
       return (miidx, minum)

       
    # if fixedValue < 0: update "rowindex" with "rowindex + delta"
    # otherwise, update "rowindex" with "fixedValue"
    def update_objViewModeTopModelItemRowIdxInParent(self, fixedValue = -1, delta = 1, clearItem = False ):
        LOG.info("update_objViewModeTopModelItemRowIdxInParent(fixedValue = {}, delta = {}) ... _objViewModeTopModelItem = {}".format(fixedValue, delta, self._objViewModeTopModelItem))
        
        if clearItem:
            self._objViewModeTopModelItem = None
            
        # if not self._objViewModeTopModelItem :
        #    return False
        
        index = self._objViewModeTopModelItemRowIdxInParent
            
        if fixedValue < 0:
            index = index + delta
        else:
            index = fixedValue
        
        
        parentModeItem = self._image_item
        if parentModeItem is not None:
            rowcnt = parentModeItem.rowCount()
            if rowcnt <= 0:
                LOG.info("1 update_objViewModeTopModelItemRowIdxInParent ... rowcnt = {}".format(rowcnt))
                return True
                
            if fixedValue < 0:
                if (index < 0) or (index >= rowcnt):
                    # self._objViewModeTopModelItemRowIdxInParent = -1  
                    LOG.info("2 update_objViewModeTopModelItemRowIdxInParent ... rowcnt = {}".format(rowcnt))
                    return True
                # print "index {} parentModeItem.childAt(rowidx) {} rowcnt {}".format(index, parentModeItem.childAt(index), rowcnt)
                while not isinstance(parentModeItem.childAt(index), AnnotationModelItem):
                    index = index + delta
                    if (index < 0) or (index >= rowcnt):
                        # self._objViewModeTopModelItemRowIdxInParent = -1
                        LOG.info("3 update_objViewModeTopModelItemRowIdxInParent ... rowcnt = {}".format(rowcnt))
                        return True # no any annotation exist in current image
            else:
                index = min(rowcnt-1, max(0, index))
                      
            LOG.info("_objViewModeTopModelItemRowIdxInParent is adjusted from {} => {}".format(self._objViewModeTopModelItemRowIdxInParent, index))
            self._objViewModeTopModelItemRowIdxInParent = index

            return False


    def setCurrentDisplayObjImg(self, currentDisplayObjModelItem, flush = False):
        """
        """
        LOG.info("call AnnotationScene.setCurrentDisplayObjImg with {} ...".format( currentDisplayObjModelItem))
        
        if (self._sceneViewMode == config.OBJ_VIEW_MODE) and (currentDisplayObjModelItem == self._objViewModeTopModelItem) and (not flush):
            return
        elif (currentDisplayObjModelItem is None) or (self._image_item is None):
            self.clear()
            self._sceneViewMode = config.IMG_VIEW_MODE
            self.reset_objViewMode()
        elif (currentDisplayObjModelItem is not None) and (isinstance(currentDisplayObjModelItem, AnnotationModelItem)):
            self.clear()
            qRectF = getQRectFFromModelItem(currentDisplayObjModelItem)
            if not qRectF:
                return
            x = int(qRectF.x())
            y = int(qRectF.y())
            w = int(qRectF.width())
            h = int(qRectF.height())

            imgshape = self.getCurrentImageShape()
            ih = imgshape[0]
            iw = imgshape[1]
            
            edgeXRatio = self._labeltool._mainwindow.topViewModeObjEdgeXRatioSliderWidget.value()
            edgeYRatio = self._labeltool._mainwindow.topViewModeObjEdgeYRatioSliderWidget.value()
            edgex = edgeXRatio * w * 2/ 100  # edgex = config.OBJ_VIEW_MAX_EDGE
            edgey = edgeYRatio * h * 1/ 100  # edgey = config.OBJ_VIEW_MAX_EDGE
            edgex = max(4, edgex)
            edgey = max(4, edgey)

            leftedge   = x - max(0, x - edgex)
            rightedge  = min(x + w + edgex, iw) - x - w
            topedge    = y - max(0, y - edgey)
            bottomedge = min(y + h + edgey, ih) - y - h
            shape = list(imgshape)
            shape[0] = eh = h + topedge  + bottomedge
            shape[1] = ew = w + leftedge + rightedge
            imgbuf = np.zeros(shape, self._image.dtype)

            np.copyto(imgbuf, self._image[y-topedge:y+h+bottomedge, x-leftedge:x+w+rightedge, ::])
            self._image_objViewModeTopModelItem_pixmap = QPixmap(toQImage(imgbuf))
            self.setSceneRect(0, 0, shape[1], shape[0])

            self._scene_item = QGraphicsPixmapItem(self._image_objViewModeTopModelItem_pixmap)
            self._scene_item.setZValue(-1)

            LOG.info("setCurrentDisplayObjImg ... addItem for QGraphicsPixmapItem(self._img_pixmap) !!!")
            self.addItem(self._scene_item)

            sceneRect = QRectF(x - leftedge, y - topedge, shape[1], shape[0])
            LOG.info("setCurrentDisplayObjImg ... addItemToScene( {} ) ...".format(currentDisplayObjModelItem))
            sceneItem = self.addItemToScene(currentDisplayObjModelItem, QRectF(0, 0, sceneRect.width(), sceneRect.height()), sceneRect, recursive = True, isInsertingNewItems = False)

            # update objViewModeTopModelItemRowIdx
            self.update_objViewModeTopModelItemRowIdxInParent( fixedValue = currentDisplayObjModelItem.row() )
            
            # display objInfo
            if config.ENABLE_STATISTIC_OBJ_INFO:
                self._labeltool._mainwindow.objViewModeInfoWidget.update(GET_ANNOTATION(currentDisplayObjModelItem, True))
            
            # display autoConnectMode
            self._labeltool.setConnectLabelMode(True)
            
            # display objViewMode
            self._labeltool._mainwindow.displayImgOrObjViewMode(config.OBJ_VIEW_MODE_DISPLAY_TEXT)
            
            self._sceneViewMode = config.OBJ_VIEW_MODE
            self._objViewModeTopModelItem = currentDisplayObjModelItem
            self._objViewModeSceneRectWRTImg = sceneRect
            self._objViewModeTopModelItemRectWRTScene = QRectF(leftedge, rightedge, w, h)

            # set other GUI widget state
            attention_scene_items = []
            attention_scene_items.append(sceneItem)
            # print "call setWidgetState(sceneItem = {})...".format( sceneItem ) 
            self.setWidgetState(attention_scene_items)
            
            self.update()
            
            self._labeltool._mainwindow.currentDisplayContentChanged.emit(False, self._image_item)
           

        if ((not config.ENABLE_TOP_OBJECT_MODE) and (config.ENABLE_EXIT_INSERT_MODE_AFTER_SWTICHING_IMG)):
            self._labeltool.exitInsertMode()
            self._inserter = None
        else:
            if self._inserter:
                # self.onInsertionModeStarted(self._inserter._idName)
                insertingEditors = [i for i in self._labeltool.propertyeditors() if i and i.isInsertingMode()]
                if len(insertingEditors) == 1:
                    insertingEditors[0].onClassButtonPressed(self._inserter._idName)
        
        return

    def getCurrentImageShape(self):
        if self._image is not None:
            return (self._image.shape)
            
        return None

    def setCurrentImage(self, current_image, flush = False, display = True):
        """
        Set the index of the model which denotes the current image to be
        displayed by the scene.  This can be either the index to a frame in a
        video, or to an image.
        """
        LOG.info("call AnnotationScene.setCurrentImage with {} self._image_item = {}...".format( current_image, self._image_item))
        if (current_image == self._image_item) and (not flush):
            return
        elif current_image is None:
            self.clear()
            self._image_item = None
            self._image      = None
            self._img_pixmap = None
        else:
            LOG.info("\ncall AnnotationScene.setCurrentImage ... clear")
            self.clear()

            if self._image_item != current_image :
                self.reset_objViewMode()
            
            self._image_item = current_image
            assert self._image_item.model() == self._model
            LOG.info("call AnnotationScene.setCurrentImage ... getImage")
            (self._image, fileIsExist) = self._labeltool.getImage(self._labeltool._imgDir, self._image_item)

            if self._image is not None:
            
                self._img_pixmap = QPixmap(toQImage(self._image))
                # srcImg = toQImage(self._image)
                isUnlabeled = current_image['unlabeled']
                if isUnlabeled:
                    painter = QPainter(self._img_pixmap)
                    painter.setFont(QFont("Arial", 48, QFont.Bold))
                    painter.setPen(Qt.red)
                    painter.drawText(16, self._img_pixmap.height()/2-16, config.GUI_INVALID_PIC_TIP)
				
                LOG.info("setCurrentImage ... addItem for QGraphicsPixmapItem(self._img_pixmap) !!!")
                self.setSceneRect(0, 0, self._img_pixmap.width(), self._img_pixmap.height())
                
                if display:
                    self._scene_item = QGraphicsPixmapItem(self._img_pixmap)
                    self._scene_item.setZValue(-1)
                    self.addItem(self._scene_item)
                    LOG.info("setCurrentImage ... insertChildItems(first = 0, last = {})!!!".format(len(self._image_item.children())-1))
                    self.insertChildItems(self._image_item, None, 0, len(self._image_item.children())-1, isInsertingNewItems = False)
                    
                    # display imgViewMode
                    self._labeltool._mainwindow.displayImgOrObjViewMode(config.IMG_VIEW_MODE_DISPLAY_TEXT)
                
                self._sceneviewmode = config.IMG_VIEW_MODE
                
                if config.ENABLE_TOP_OBJECT_MODE:
                    # print "current_image = {} current_image.childAt(0) = {}".format(current_image, current_image.childAt(0))
                    self._topObjModelItem = copy.copy(current_image.childAt(0))
                    rect = getQRectFFromModelItem(self._topObjModelItem)
                    rect.setSize(QSizeF(self._img_pixmap.width(), self._img_pixmap.height()))
                    self._topObjModelItem.update(convertQRectFToModelItemKeyValues( rect ), False)
                    self.setCurrentDisplayObjImg(self._topObjModelItem)
                   
                    checkedButtonName= self._labeltool._mainwindow.personbike_pannel.propertyEditorWidget.getChecked()
                    if checkedButtonName:
                        # print "checkedButtonName = {}".format(checkedButtonName)
                        self._labeltool._mainwindow.personbike_pannel.propertyEditorWidget.onClassButtonPressed(checkedButtonName)

                # set other GUI widget state
                attention_scene_items = []
                self.setWidgetState(attention_scene_items)

                
                if display:
                    self.update()

        if self._inserter and hasattr(self._inserter, "set_parent_modelItem"):
            self._inserter.set_parent_modelItem(None)
            self._inserter.set_rectBoundaryWRTScene(None)
            self._inserter._sceneRect = None
      
        if ((not config.ENABLE_TOP_OBJECT_MODE) and (config.ENABLE_EXIT_INSERT_MODE_AFTER_SWTICHING_IMG)):
            self._labeltool.exitInsertMode()
            self._inserter = None
        else:
            if self._inserter:
                # self.onInsertionModeStarted(self._inserter._idName)
                insertingEditors = [i for i in self._labeltool.propertyeditors() if i and i.isInsertingMode()]
                if len(insertingEditors) == 1:
                    insertingEditors[0].onClassButtonPressed(self._inserter._idName)
        
        return
        
    def validateRelationshipWithParent(self, parentModelItem, clsNameOfParent, clsNameOfChild):
        parentRect = getQRectFFromModelItem(parentModelItem)
        relationship = config.OBJ_ANNOTATION_POSTION_BOUND_RELLATIONSHIP.get(clsNameOfChild, None)
        isAllowed = True
        isBoundedInParent = False
        rectBoundary = None
        allowedParentsNameList = None
        allowedChildNum = -1
        if relationship is not None:
            allowedParentsNameList = relationship[config.ALLOWED_PARENTS_INDEX_IN_RELATIONSHIP]
            if (clsNameOfParent not in allowedParentsNameList) and (allowedParentsNameList):
                isAllowed = False
            else:
                allowedParentIndex = allowedParentsNameList.index(clsNameOfParent)
                isBoundedInParent = relationship[config.CHILD_POS_IS_BOUNDED_IN_PARENT_INDEX_IN_RELATIONSHIP]
                allowedChildNum = relationship[config.ALLOWED_CHILD_NUM_IN_RELATIONSHIP][allowedParentIndex]
                rectBoundary = parentRect if isBoundedInParent else None
        return (isAllowed, isBoundedInParent, rectBoundary, allowedParentsNameList, allowedChildNum)
            
                                
    # ================================================================        
    # zx comment: put all child model items's graphic item widget on graphic scene
    # parentModeItem default = self._image_item
    # ================================================================        
    def insertChildItems(self, parentModelItem, _sceneRect, first, last, recursive = True, isInsertingNewItems = False):
        LOG.info("AnnotationScene.insertChildItems(first = {}, last = {})... parentModeItem = {} {})... _image_item = {}".format(first, last, parentModelItem, GET_ANNOTATION(parentModelItem), self._image_item))
        if self._image_item is None:
            return

        assert self._model is not None
        
        # create a graphics item for each model index
        for row in range(first, last+1):
            child = parentModelItem.childAt(row)
            LOG.info("AnnotationScene.insertChildItems... childAt(row={}) = {} _sceneRect = {}...".format(row, child, _sceneRect))
            LOG.info("type(child) = {} child.getAnnotations() = {}...".format(type(child), child.getAnnotations() if hasattr(child, 'getAnnotations') else None ))

            if not isinstance(child, AnnotationModelItem):
                continue

            clsNameOfChild = child.get_label_class()
            isValid, rectBoundary = self.checkModelItemValidity(clsNameOfChild, None, parentModelItem, self._image_item, enablePopupMsgBox = False, enableEmitStatusMsg = True, enableCountingThisModelItem = False)
            if not isValid:
                continue

            rectBoundaryWRTScene = rectBoundary.translated(-_sceneRect.topLeft() if _sceneRect else QPointF(0, 0)) if rectBoundary else None

            self.addItemToScene(child, rectBoundaryWRTScene, _sceneRect, recursive, isInsertingNewItems)
            
        return


                        
    def addItemToScene(self, modelItem, rectBoundaryWRTScene = None, _sceneRect = None, recursive = True, isInsertingNewItems = False):
        if not isinstance(modelItem, AnnotationModelItem):
            return None
            
        try:
            clsNameOfParent = modelItem[config.METADATA_LABELCLASS_TOKEN]
        except KeyError:
            LOG.debug('Could not find key class in annotation item. Skipping this item. Please check your label file.')
            return None
            
        # zx888
        item = self._itemfactory.create(clsNameOfParent, self.deleteItmOfZeroSizeSignal, modelItem, _sceneRect)
        if item is not None:
            item.set_imgsz(self.currentImageSize())
            item.set_rectBoundaryWRTScene(rectBoundaryWRTScene)      
            # if clsNameOfParent == config.ANNOTATION_UMBRELLA_TOKEN:
            #     print "....... rectBoundaryWRTScene = {} _sceneRect = {}".format(rectBoundaryWRTScene, _sceneRect)
            LOG.info("addItemToScene().. addItem( item = {} )...".format(item))
            self.addItem(item)
            LOG.info("addItemToScene() finished")

            # -------------------------------------------------------------------------------
            # Here should have a better interface. TODO in the near future
            # -------------------------------------------------------------------------------
            if ( clsNameOfParent == config.ANNOTATION_PERSONBIKE_TOKEN ) and isInsertingNewItems:

                checkedGroupName, checkedWidgetsOptions = self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.getCheckedWidgetsOptionInfo(config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN)

                # if checkedWidgetsOptions:
                if True:
                    item.addAttrStickers(checkedGroupName, checkedWidgetsOptions, True )
             # -------------------------------------------------------------------------------
            
        else:
             LOG.debug("Could not find item for annotation with class '%s'" % clsNameOfParent)
            

        if recursive:
            children = modelItem.getChildsOfAnnoModelItem()
            for child in children:
                clsNameOfChild = child[config.METADATA_LABELCLASS_TOKEN]
                isValid, rectBoundary = self.checkModelItemValidity(clsNameOfChild, None, modelItem, self._image_item, enablePopupMsgBox = False, enableEmitStatusMsg = True, enableCountingThisModelItem = False)
                if not isValid:
                    continue
                    
                rectBoundaryWRTScene = rectBoundary.translated(-_sceneRect.topLeft() if _sceneRect else QPointF(0, 0)) if rectBoundary else None
                self.addItemToScene(child, rectBoundaryWRTScene, _sceneRect, recursive, isInsertingNewItems)
    
        return item
        
    # convert AnnotationModelItem to baseItem or baseItem's child class (i.e.: SceneItem variants)
    # such as, different QAbstractGraphicsShapeItem implementaion, which include RectItem, PointItem, etc.
    def modelItem_to_baseItem(self, modelitem):
        for item in self.items():
            if isinstance(item, BaseItem):
                if item.modelItem() == modelitem:
                    return item
        return None
         
           
    def deleteItem(self, modelitem, baseitem):
        if modelitem is None:
            return
            
        modelitem.delete()   
        
        if baseitem is None:
            return
            
        if isinstance(baseitem, BaseItem):
            # LOG.info("{} emit signal {} for deletion".format( baseitem, baseitem._idName))
            self._labeltool.itemIsDeleted.emit( baseitem._idName )  
            
            # zx comment: it is not a good way to delete GraphicItem like this. 
            self.removeItem(baseitem)
            
        return      

    def deleteItemOfZeroSize(self, itemOfZeroSize):
        self.deleteItems([itemOfZeroSize], True)

    def deleteItems(self, itemsListToDelete, recursive = True):
        try:
            if not itemsListToDelete:
                return
                
            LOG.info("deleteItems(itemsListToDelete = {})...".format(itemsListToDelete))
            
            # some (graphics) items may share the same model item
            # therefore we need to determine the unique set of model items first
            # must use a dict for hashing instead of a set, because objects are not hashable
           
            if config.ENABLE_TOP_OBJECT_MODE:
                modelitems_to_delete = dict((id(item.modelItem()), item.modelItem()) for item in itemsListToDelete if ( config.ENABLE_TOP_OBJECT_MODE and (item.modelItem().get_label_class() != config.DEFAULT_TOP_OBJECT)))
                baseitems_to_delete  = dict((id(item.modelItem()), item) for item in itemsListToDelete if ( config.ENABLE_TOP_OBJECT_MODE and (item.modelItem().get_label_class() != config.DEFAULT_TOP_OBJECT)))
            else:
                modelitems_to_delete = dict((id(item.modelItem()), item.modelItem()) for item in itemsListToDelete)
                baseitems_to_delete  = dict((id(item.modelItem()), item) for item in itemsListToDelete)

            LOG.info("deleteItems(modelitems_to_delete = {} baseitems_to_delete = {})...".format(modelitems_to_delete, baseitems_to_delete))
            
            if recursive:
            
                # find any child modelitem which is not in modelitems_to_delete
                child_modelitems_to_delete = {}
                for key, modelitem in modelitems_to_delete.iteritems():
                    if not isinstance(modelitem, AnnotationModelItem):
                        continue 
                    sons = modelitem.getChildsOfAnnoModelItem()
                    for k in sons:    
                        if k not in modelitems_to_delete.itervalues():
                            LOG.info("child_modelitems_to_delete {} ....".format(k))
                            child_modelitems_to_delete[id(k)] = k
                    
                # delete all child modelitems which are not deleted yet
                for key, modelitem in child_modelitems_to_delete.iteritems(): 
                    baseitem = self.modelItem_to_baseItem(modelitem)
                    LOG.info("child_modelitems_to_delete .... modelitem = {} baseitem = {} idName = {}....".format(modelitem, baseitem, baseitem._idName))            
                    self.deleteItem(modelitem, baseitem)    
            
            
            # delete all modelitems which are in itemsListToDelete
            for key, modelitem in modelitems_to_delete.iteritems():
                LOG.info("modelitems_to_delete .... modelitem = {} baseitem = {} idName = {}....".format(modelitem, baseitems_to_delete[key], baseitems_to_delete[key]._idName))            
                self.deleteItem(modelitem, baseitems_to_delete[key])
 
        except Exception as e:
            print "deleteItems throw an exception {}!".format(str(e))
            pass
    
            
    def deleteSelectedItems(self, recursive = True):
        selectedItems = self.selectedItems()
        if selectedItems:
            widgetName = selectedItems[0].modelItem().get_label_class() 
        self.deleteItems ( selectedItems, recursive )
        self._labeltool._mainwindow.setWidgetChecked(widgetName, False)
        
        
    def onInserterFailed(self, parentModelItem, itemClsNameToInsert):
        _itemClsNameToInsert = str(itemClsNameToInsert)
        pe = self._labeltool._mainwindow.getBelongingPannel(_itemClsNameToInsert)
        # print "call onInserterFailed ... pe = {}".format(pe)
        if pe:
            pe.setChecked(_itemClsNameToInsert, False)
        self._selectedDisplayItemsList = []
        if self._inserter is not None:
            self._inserter.set_parent_modelItem(None)
            
        self._labeltool.setConnectLabelMode(self._labeltool._enableAutoConnectLabelMode)
 
        # zx add @ 20171016
        self._labeltool.exitInsertModeForCurInsertModeEditor()
        return
		    
    def onItemIsAddedToScene(self, addedSceneItem):
        selected_scene_items = self.selectedItems()
        if not selected_scene_items:
            selected_scene_items = [addedSceneItem]
        self.setWidgetState(selected_scene_items)
        return
        
    def onInserterFinished(self):
        self.sender().inserterFinished.disconnect(self.onInserterFinished)
        self._labeltool.currentImageChanged.disconnect(self.sender().imageChange)
        self._labeltool.exitInsertModeForCurInsertModeEditor()
        self._inserter = None
        LOG.info("AnnotationScene.onInserterFinished .... self._inserter = {} selectedDisplayedItemsList = {}".format(self._inserter, self._selectedDisplayItemsList))

    def clearRuler(self):
        items = QGraphicsScene.items(self)
        for it in items:
            if(type(it)==QGraphicsLineItem):
                QGraphicsScene.removeItem(self, it)

    def onInsertionModeStarted(self, _pannelName, _classNameToInsert, _buttonNameOfInserter):
        
        pannelName = str(_pannelName)
        classNameToInsert = str(_classNameToInsert)
        buttonNameOfInserter = str(_buttonNameOfInserter)
        
        LOG.info("onInsertionModeStarted(pannelName = {}, classNameToInsert = {}, buttonNameOfInserter = {}) ... self._inserter = {} selectedDisplayedItemsList = {}".format(pannelName, classNameToInsert, buttonNameOfInserter, self._inserter, self._selectedDisplayItemsList))
        
        # Abort current inserter
        if self._inserter is not None:
            self._inserter.abort()

        # self.deselectAllItems()
        LOG.info( "onInsertionModeStarted(classNameToInsert = {}) ... call deselectAllItemsExcept(selectedDisplayedItemsList = {})".format(classNameToInsert, self._selectedDisplayItemsList) )
        self.deselectAllItemsExcept(self._selectedDisplayItemsList)
        LOG.info("onInsertionModeStarted(classNameToInsert = {}) ... self._inserter = {} selectedDisplayedItemsList = {}".format(classNameToInsert, self._inserter, self._selectedDisplayItemsList))
        
        # ================================================================
        # zx fix bug: must call this to restore color selection history
        # ================================================================
        if classNameToInsert == config.ANNOTATION_UPPER_BODY_TOKEN:
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_UPPER_COLOR_TOKEN, False)
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_UPPER_CLOTH_TOKEN, False)
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_UPPER_TEXTURE_TOKEN, False)
 
        if classNameToInsert == config.ANNOTATION_LOWER_BODY_TOKEN:
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_LOWER_COLOR_TOKEN, False)
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_LOWER_CLOTH_TOKEN, False)

 
        if (classNameToInsert == config.ANNOTATION_PEDESTRAIN_TOKEN) or (classNameToInsert == config.ANNOTATION_PERSONBIKE_TOKEN):
            self._labeltool._mainwindow.property_editor5.setCheckedGroup(config.ANNOTATION_GENDER_TOKEN,     False)
            self._labeltool._mainwindow.property_editor5.setCheckedGroup(config.ANNOTATION_AGE_TOKEN,        False)
            self._labeltool._mainwindow.property_editor5.setCheckedGroup(config.ANNOTATION_ANGLE_TOKEN,      False)
            self._labeltool._mainwindow.property_editor5.setCheckedGroup(config.ANNOTATION_HAIR_STYLE_TOKEN, False)
 
        
        if classNameToInsert == config.ANNOTATION_VEHICLE_TOKEN:
            self._labeltool._mainwindow.property_editor6.attrAreaWidget.setCheckedGroup(config.ANNOTATION_VEHICLE_COLOR_TOKEN, False)
            
        if classNameToInsert == config.ANNOTATION_PERSONBIKE_TOKEN:
            if self._labeltool._mainwindow._newInsertingPersonBikeType:
                self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.setCheckedCheckbox (config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN, self._labeltool._mainwindow._newInsertingPersonBikeType, True)
                self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.enableCheckboxGroup(config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN, True)
                # print "call isInsertingPersonBikeShortcut..."
                # self._labeltool._mainwindow.isInsertingPersonBikeShortcut()
        
        # clear ruler
        self.clearRuler()
        
        # Add new inserter
        for edit in self._labeltool.propertyeditors():
            if edit is None:
            	continue
            
            if (edit._idName != pannelName):
                continue
                
            LOG.info("onInsertionModeStarted... process for pannelName {} classNameToInsert {} ...".format(pannelName, classNameToInsert))
            
            if classNameToInsert in edit.getSupportedInserters():
                LOG.info("onInsertionModeStarted for classNameToInsert {} found in PropertyEditor {}...".format(classNameToInsert, edit))
                default_property = edit.currentToInsertItemProperty()
                LOG.info("default_property {} ...".format(default_property))
                
                # zx999
                parentModelItem = None
                scenerect = None
                LOG.info( "_sceneViewMode = {} self._objViewModeTopModelItem) = {}".format( self._sceneViewMode, self._objViewModeTopModelItem ) )

                if (self._sceneViewMode == config.IMG_VIEW_MODE):
                    if (not self._labeltool._enableAutoConnectLabelMode) and self._selectedDisplayItemsList:
                        parentModelItem = self._selectedDisplayItemsList[-1][SELECTED_DISPLAYED_ITEMS_LIST_MODELITEM_INDEX]
                    else:
                        parentModelItem = None
                elif (self._sceneViewMode == config.OBJ_VIEW_MODE) and (self._objViewModeTopModelItem is not None):
                    parentModelItem = self._objViewModeTopModelItem
                    scenerect = self._objViewModeSceneRectWRTImg
                
                LOG.info("inserter is created for {} with default_property {}>>>>".format(classNameToInsert, GET_ANNOTATION(default_property)))
                inserter = self._inserterfactory.create(classNameToInsert, self._labeltool.newItemIsInserted, self._labeltool, self, scenerect, default_property)
                
                if parentModelItem is not None:    
                    inserter.set_parent_modelItem(parentModelItem)
                    LOG.info("parentModelItem = {} x = {} y = {} width = {} height = {} ".format(parentModelItem, parentModelItem['x'],  parentModelItem['y'],  parentModelItem['width'],  parentModelItem['height']))
                    clsNameOfChild = classNameToInsert
                    dummy, rectBoundary = self.checkModelItemValidity(clsNameOfChild, None, parentModelItem, self._image_item, enablePopupMsgBox = False, enableEmitStatusMsg = False, enableCountingThisModelItem = True)
                    rectBoundaryWRTScene = rectBoundary.translated(-scenerect.topLeft() if scenerect else QPointF(0, 0)) if rectBoundary else None
                    inserter.set_rectBoundaryWRTScene(rectBoundaryWRTScene)
                            
                if inserter is None:
                    raise InvalidArgumentException("Could not find inserter for class '%s' with default properties '%s'" % (classNameToInsert, default_property))
                    
                inserter.set_inserterFailedSignalObj(self.inserterFailed)    
                inserter.inserterFinished.connect(self.onInserterFinished)
                self._labeltool.currentImageChanged.connect(inserter.imageChange)
                self._inserter = inserter
                LOG.debug("Created inserter for class '%s' with default properties '%s'" % (classNameToInsert, default_property))
                self._labeltool.set_insert_mode_property_editor(edit)

                # since self._inserter.abort() in before calling will make current system exit inserting mode, thus here i need set insertering mode again
                edit.onInsertionModeStarted(classNameToInsert, buttonNameOfInserter)  # edit.setChecked(buttonNameOfInserter, True) 
                
                self._labeltool._mainwindow.displayInsertOrEditMode(config.GUI_INSERT_MODE_DISPLAY_TEXT)

                break
                

    def onInsertionModeEnded(self):
        LOG.info("onInsertionModeEnded... self._inserter = {}".format(self._inserter))
        if self._inserter is not None:
            self._inserter.abort()
        self.clearRuler()

        # zx add @ 20161018 for bug fix ???
        self._inserter = None
        
        self._labeltool._mainwindow.displayInsertOrEditMode(config.GUI_EDIT_MODE_DISPLAY_TEXT)
  

  
    #______________________________________________________________________________________________________
    #
    # common methods
    #______________________________________________________________________________________________________
    def reset_objViewMode(self):
        self._objViewModeTopModelItem = None
        self._objViewModeSceneRectWRTImg = None
        self._objViewModeTopModelItemRectWRTScene = None
        self._objViewModeTopModelItemRowIdxInParent = 0

    
    def reset(self):
        LOG.info("AnnotationScene.reset call setCurrentImage with None...")
        self.clear()
        self._mousePressClosestSceneItem = None
        self._inserter = None
        self.setCurrentImage(None, flush = False, display = True)
        self.clearMessage()
        
        self._sceneViewMode = config.IMG_VIEW_MODE
        self.reset_objViewMode()

        if (self._labeltool._mainwindow is not None) and config.ENABLE_STATISTIC_OBJ_INFO:
            self._labeltool._mainwindow.objViewModeInfoWidget.update(None)


    def clear(self):
        # do not use QGraphicsScene.clear(self) so that the underlying
        # C++ objects are not deleted if there is still another python
        # reference to the item somewhere else (e.g. in an inserter)
        for item in self.items():
            if item.parentItem() is None:
                self.removeItem(item)
        self._scene_item = None
        self._selectedDisplayItemsList = []
        if ((not config.ENABLE_TOP_OBJECT_MODE) and (config.ENABLE_EXIT_INSERT_MODE_AFTER_SWTICHING_IMG)):
            self._inserter = None
        
        self._sceneViewMode = config.IMG_VIEW_MODE
        
        
    def addItem(self, item):
        QGraphicsScene.addItem(self, item)
        
        # TODO: emit signal itemAdded
        # self.itemIsAddedToScene.emit(item)

    #______________________________________________________________________________________________________
    # mouse event handlers
    #______________________________________________________________________________________________________
    
    def onMouseSingleClicked(self):
        # LOG.debug("AnnotationScene.onMouseSingleClicked ...")

        # judge whether it is a click or a move event  
        # if not self._mouseIsMove:
        #     # zx999
        #     if self._selectedDisplayItemsList:
        #         LOG.debug("AnnotationScene.onMouseSingleClicked ... deSelect {}".format(self._selectedDisplayItemsList))
        #         self.deselectItems(self._selectedDisplayItemsList)
                
        self._mouseIsMove = False      
    
    
    def mousePressEvent(self, event):

        # LOG.debug("AnnotationScene.mousePressEvent : Pos {} Inserter {}".format(event.scenePos(), self._inserter))
    
        self._mouseSingleClickTimer.start( QApplication.doubleClickInterval() )
        self._mouseIsMove = False   
        
        if not self._mouseIsMove:
            # zx999
            if self._selectedDisplayItemsList:
                self.deselectItems(self._selectedDisplayItemsList)

      	if self._inserter is not None:
            if not self.sceneRect().contains(event.scenePos()) and \
               not self._inserter.allowOutOfSceneEvents():
                # ignore events outside the scene rect
                return
            # --------------------    
            # insert mode
            # --------------------
            # display connectMode
            parent_modelItem = self._inserter._parent_modelItem
            if ( parent_modelItem) and (not self._selectedDisplayItemsList) :
                self._selectedDisplayItemsList.append((parent_modelItem.get_label_class(), parent_modelItem))
                self._labeltool.setConnectLabelMode(self._labeltool._enableAutoConnectLabelMode)
 
            LOG.info("call self._inserter {} {}.mousePressEvent with scenePos {} for image {}...".format(self._inserter._idName, self._inserter, event.scenePos(), self._image_item))
            self._inserter.mousePressEvent(event, self._image_item)
            
            sp = event.scenePos()
            self.itemIsInsertedOrSelected.emit(sp.x(), sp.y(), 0)

        else:
            # --------------------    
            # edit mode
            # --------------------   
            # print "QGraphicsScene.mousePressEvent... event = {} pos = {}".format(event, event.scenePos())
            sceneRect = None if self._sceneViewMode == config.IMG_VIEW_MODE else self._objViewModeSceneRectWRTImg
            mindistance_modelitem, mindistance, mindistancec = findScenePositionClosetModelItem(self._image_item, self, sceneRect, event.scenePos())
            if self._mousePressClosestSceneItem:
                self._mousePressClosestSceneItem.setSelected(False)
            self._mousePressClosestSceneItem = None
            if mindistance_modelitem:
                mindistance_sceneitem = self.modelItem_to_baseItem(mindistance_modelitem)
                self._mousePressClosestSceneItem = mindistance_sceneitem
                if mindistance_sceneitem:
                    mindistance_sceneitem.setSelected(True)
                    self.sendEvent(mindistance_sceneitem, event)
                    return
            
            QGraphicsScene.mousePressEvent(self, event)
                 
        return
        
    # ========================================================================================================
    # zx add mouseCtrlDoubleClickEvent @ 201611!!
    # (1) If we are in edit mode now, ctrl + double click event will delete all selected items. 
    # (2) If we are in insert mode now, ctrl + double click event will call current inserter's mouseDoubleClickEvent and then delete all  selected items
    # ========================================================================================================
    def mouseCtrlDoubleClickEvent(self, event):
    
        LOG.debug("AnnotationScene.mouseCtrlDoubleClickEvent : Pos {} Inserter {}".format(event.scenePos(), self._inserter)) 
        
        if self._inserter is None:
            # edit mode
            self.deleteSelectedItems()
            QGraphicsScene.mousePressEvent(self, event)
            
        else:
            # insert mode
            if self.sceneRect().contains(event.scenePos()) or self._inserter.allowOutOfSceneEvents():
                # ignore events outside the scene rect
                self._inserter.mouseDoubleClickEvent(event, self._image_item)
               
            self.deleteSelectedItems()
            # QGraphicsScene.mousePressEvent(self, event)
                 
 
                
    # ========================================================================================================
    # zx modify mouseDoubleClickEvent @ 201611!!
    # Whether we are in edit mode or insert mode now, double click event will select item around the mouse cliked position.
    # The Selected item will display in dash line style
    # ========================================================================================================
    def mouseDoubleClickEvent(self, event):
        self._mouseSingleClickTimer.stop()
        
        LOG.debug("AnnotationScene.mouseDoubleClickEvent : Pos {} Inserter {}".format(event.scenePos(), self._inserter)) 
        
        if ( event.modifiers() == Qt.ControlModifier):
            return self.mouseCtrlDoubleClickEvent(event)
        
        
        if self._inserter is None:
            # edit mode
            QGraphicsScene.mousePressEvent(self, event)
        else:
            # insert mode
            if not self.sceneRect().contains(event.scenePos()) and \
                    not self._inserter.allowOutOfSceneEvents():
                # ignore events outside the scene rect
                return
            
            if isinstance(self._inserter, QuadrangleItemInserter) or isinstance(self._inserter, PolygonItemInserter):
                self._inserter.mouseDoubleClickEvent(event, self._image_item)
            else:
                self._labeltool.exitInsertMode()
                QGraphicsScene.mousePressEvent(self, event)    
            
                 
    def statisticSelectedObjsCnt(self):
        vehicleCnt = 0
        pedestrainCnt = 0
        personBikeCnt = 0
        for item in self.items():
            if ( item.isSelected() and (type(item) == RectItem) and (item._model_item is not None) ):
                cls = item._model_item.get_label_class()
                if (cls == config.ANNOTATION_PEDESTRAIN_TOKEN ):
                    pedestrainCnt += 1
                elif (cls == config.ANNOTATION_VEHICLE_TOKEN ):
                    vehicleCnt += 1
                elif (cls == config.ANNOTATION_PERSONBIKE_TOKEN ):
                    personBikeCnt += 1
        return (pedestrainCnt, personBikeCnt, vehicleCnt)          


    def mouseReleaseEvent(self, event):
        LOG.debug("AnnotationScene.mouseReleaseEvent : Pos {} Inserter {}".format(event.scenePos(), self._inserter))
        
        # self.statisticNdisplaySelectedObjsCnt()
                
        if self._inserter is not None:
            # insert mode
            self._inserter.mouseReleaseEvent(event, self._image_item)
            sp = event.scenePos()
            self.itemIsInsertedOrSelected.emit(sp.x(), sp.y(), 2)
        else:
            # edit mode
            if self._mousePressClosestSceneItem:
                self.sendEvent(self._mousePressClosestSceneItem, event)
                return              
            QGraphicsScene.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        self._mouseIsMove = True
        
        sp = event.scenePos()
        self.mousePositionChanged.emit(sp.x(), sp.y())
        
        # LOG.debug("mouseMoveEvent %s %s" % (self.sceneRect().contains(event.scenePos()), event.scenePos()))
        
        # self.statisticNdisplaySelectedObjsCnt()
       
                            
        if self._inserter is not None:
            # insert mode
            # print "inseter QGraphicsScene.mouseMoveEvent ...."
            self._inserter.mouseMoveEvent(event, self._image_item)
            
       	    self.itemIsInsertedOrSelected.emit(sp.x(), sp.y(), 1)
       	    
        else:
            # edit mode
            if self._mousePressClosestSceneItem:
                self.sendEvent(self._mousePressClosestSceneItem, event)
                return 
                       
            QGraphicsScene.mouseMoveEvent(self, event)

    def deselectAllItems(self):
        for item in self.items():
            item.setSelected(False)

    def deselectItems(self, modelItemsList):
        items = [item for item in self.items()  for modelItem in modelItemsList
                 if ( item.modelItem() if hasattr(item, 'modelItem') else None ) == modelItem[SELECTED_DISPLAYED_ITEMS_LIST_MODELITEM_INDEX] ]
        for i in items:
            i.setSelected(False)
            
    def deselectAllItemsExcept(self, exceptModelItemsList):
        items = [item for item in self.items() for modelItem in exceptModelItemsList if
                 (item.modelItem() if hasattr(item, 'modelItem') else None) != modelItem[SELECTED_DISPLAYED_ITEMS_LIST_MODELITEM_INDEX]]
        for i in items:
            i.setSelected(False)

        """
        for item in self.items():
            modelItem = item.modelItem() if hasattr(item, 'modelItem') else None
            if modelItem is None:
                continue
            isExcept = any([i[SELECTED_DISPLAYED_ITEMS_LIST_MODELITEM_INDEX] == modelItem for i in exceptInstersList])
            if not isExcept:
                item.setSelected(False)
        """

    def onSelectionChanged(self):
        
        model_items = [item.modelItem() for item in self.selectedItems()]
        LOG.info("call onSelectionChanged... model_items {}".format(model_items))
        self._labeltool.treeview().setSelectedItems(model_items)
        self.editSelectedItems()

    def onSelectionChangedInTreeView(self, model_items):
        block = self.blockSignals(True)
        selected_items = set()
        for model_item in model_items:
            for item in self.itemsFromIndex(model_item.index()):
                selected_items.add(item)
        for item in self.items():
            item.setSelected(False)
        for item in selected_items:
            if item is not None:
                item.setSelected(True)
        self.blockSignals(block)
        self.editSelectedItems()
        
    def get_label_classes(self, annotationModelItems):
    	_label_classes = set([item[config.METADATA_LABELCLASS_TOKEN] for item in annotationModelItems if config.METADATA_LABELCLASS_TOKEN in item])
    	return _label_classes

    def get_label_class(self, annotationModelItem):
    	return annotationModelItem.get(config.METADATA_LABELCLASS_TOKEN, None)

    def getSelectedItemsClass(self):
        selected_scene_items = self.selectedItems()
        
        if len(selected_scene_items) > 0 :  
            annotationModelItems = [item.modelItem() for item in selected_scene_items]
            label_classes = self.get_label_classes(annotationModelItems)
            return label_classes
        else:
            return None    
            

    def getSelectedItemsNum(self):
        return len(self.selectedItems())


    def setWidgetState(self, selected_scene_items):
        # print "setWidgetState... selected_scene_items = {} ENABLE_TOP_OBJECT_MODE = {} _topObjModelItem = {}".format(
        #    selected_scene_items, config.ENABLE_TOP_OBJECT_MODE, self._topObjModelItem
        #  )
        if (not selected_scene_items) and config.ENABLE_TOP_OBJECT_MODE and self._topObjModelItem:
            selected_scene_items = [ self.modelItem_to_baseItem(self._topObjModelItem) ]
            # print "setWidgetState... selected_scene_items = {}".format(selected_scene_items)

        if (not selected_scene_items) and self._sceneViewMode == config.OBJ_VIEW_MODE and self._objViewModeTopModelItem:
            selected_scene_items = [ self.modelItem_to_baseItem(self._objViewModeTopModelItem) ]
            # print "setWidgetState... selected_scene_items = {}".format(selected_scene_items)

        lc = [item.get_label_class() for item in selected_scene_items if item ]
        LOG.info("AnnotaionScene.editSelectedItems ... selectedItems {} ...".format(lc))
        # print ("AnnotaionScene.editSelectedItems ... selectedItems {} ...".format(lc))
       
        shouldEnableInserterWidget = False
        if ((not config.ENABLE_TOP_OBJECT_MODE) and (not config.ENABLE_EXIT_INSERT_MODE_AFTER_SWTICHING_IMG)):
            if self.isInsertingMode(): 
                if lc:
                    if (self._inserter._idName != lc[0]):
                        shouldEnableInserterWidget = True
            
        shouldDisplayUpperColor = False
        shouldDisplayLowerColor = False

        parentModelItem = selected_scene_items[0].modelItem() if selected_scene_items and selected_scene_items[0] else None

        # print "[j for i in lc for j in config.ALLOWED_DISPLAY_OBJECTS_AND_ATTRIBUTE_STICKERS.get(i, [])] = {}".format([j for i in lc for j in config.ALLOWED_DISPLAY_OBJECTS_AND_ATTRIBUTE_STICKERS.get(i, [])])
        if any([j == config.ANNOTATION_UPPER_BODY_TOKEN for i in lc for j in config.ALLOWED_DISPLAY_OBJECTS_AND_ATTRIBUTE_STICKERS.get(i, [])] ):
           
            if config.BODY_COLOR_MUST_ATTACH_TO_BODY_PART:
                bodyPartCnt = 0
                found = findModelItemsWithSpecificClassName(config.ANNOTATION_UPPER_BODY_TOKEN, parentModelItem, 2)
                bodyPartCnt += 1 if found else 0
                shouldDisplayUpperColor = True if bodyPartCnt > 0 else False
                # print "bodyPartCnt = {} shouldDisplayUpperColor = {}".format(bodyPartCnt, shouldDisplayUpperColor)
            else:
                shouldDisplayUpperColor = True
            
            # set check status as per the first scene_item in selected_scene_items
            self._labeltool._mainwindow.property_editor4.enableCheckboxGroup(config.ANNOTATION_UPPER_CLOTH_TOKEN, True)
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_UPPER_CLOTH_TOKEN, False)
            ucloth = selected_scene_items[0]._model_item.get(config.ANNOTATION_UPPER_CLOTH_TOKEN, None)
            # print "selected_scene_items[0]._model_item = {} ucloth = {}\n".format(selected_scene_items[0]._model_item, ucloth)
            ucloth = ucloth if ucloth else config.TAG_UNSET_TOKEN
            self._labeltool._mainwindow.property_editor4.setCheckedCheckbox(config.ANNOTATION_UPPER_CLOTH_TOKEN, ucloth, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor4.enableCheckbox(config.ANNOTATION_UPPER_CLOTH_TOKEN, config.TAG_UNSET_TOKEN, False)

            self._labeltool._mainwindow.property_editor4.enableCheckboxGroup(config.ANNOTATION_UPPER_TEXTURE_TOKEN, True)
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_UPPER_TEXTURE_TOKEN, False)
            ucloth = selected_scene_items[0]._model_item.get(config.ANNOTATION_UPPER_TEXTURE_TOKEN, None)
            # print "selected_scene_items[0]._model_item = {} ucloth = {}\n".format(selected_scene_items[0]._model_item, ucloth)
            ucloth = ucloth if ucloth else config.TAG_UNSET_TOKEN
            self._labeltool._mainwindow.property_editor4.setCheckedCheckbox(config.ANNOTATION_UPPER_TEXTURE_TOKEN, ucloth, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor4.enableCheckbox(config.ANNOTATION_UPPER_TEXTURE_TOKEN, config.TAG_UNSET_TOKEN, False)

                
        elif not any([(i == config.ANNOTATION_UPPER_BODY_TOKEN) for i in lc]):
            shouldDisplayUpperColor = False
            
        if not shouldDisplayUpperColor:
            self._labeltool._mainwindow.property_editor4.enableCheckboxGroup(config.ANNOTATION_UPPER_COLOR_TOKEN, False)
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_UPPER_COLOR_TOKEN, False)
            self._labeltool._mainwindow.property_editor4.setCheckedCheckbox(config.ANNOTATION_UPPER_CLOTH_TOKEN, config.TAG_UNSET_TOKEN, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor4.enableCheckbox(config.ANNOTATION_UPPER_CLOTH_TOKEN, config.TAG_UNSET_TOKEN, False)
            self._labeltool._mainwindow.property_editor4.enableCheckboxGroup(config.ANNOTATION_UPPER_CLOTH_TOKEN, False)
 
            self._labeltool._mainwindow.property_editor4.setCheckedCheckbox(config.ANNOTATION_UPPER_TEXTURE_TOKEN, config.TAG_UNSET_TOKEN, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor4.enableCheckbox(config.ANNOTATION_UPPER_TEXTURE_TOKEN, config.TAG_UNSET_TOKEN, False)
            self._labeltool._mainwindow.property_editor4.enableCheckboxGroup(config.ANNOTATION_UPPER_TEXTURE_TOKEN, False)

 
        if any([j == config.ANNOTATION_LOWER_BODY_TOKEN for i in lc for j in config.ALLOWED_DISPLAY_OBJECTS_AND_ATTRIBUTE_STICKERS.get(i, [])] ):
            
            if config.BODY_COLOR_MUST_ATTACH_TO_BODY_PART:
                bodyPartCnt = 0
                bodyPartCnt += 1 if findModelItemsWithSpecificClassName(config.ANNOTATION_LOWER_BODY_TOKEN, parentModelItem, 2) else 0
                shouldDisplayLowerColor = True if bodyPartCnt > 0 else False
            else:
                shouldDisplayLowerColor = True
            
            # set check status as per the first scene_item in selected_scene_items
            self._labeltool._mainwindow.property_editor4.enableCheckboxGroup(config.ANNOTATION_LOWER_CLOTH_TOKEN, True)
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_LOWER_CLOTH_TOKEN, False)
            lcloth = selected_scene_items[0]._model_item.get(config.ANNOTATION_LOWER_CLOTH_TOKEN, None)
            lcloth = lcloth if lcloth else config.TAG_UNSET_TOKEN
            self._labeltool._mainwindow.property_editor4.setCheckedCheckbox(config.ANNOTATION_LOWER_CLOTH_TOKEN, lcloth, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor4.enableCheckbox(config.ANNOTATION_LOWER_CLOTH_TOKEN, config.TAG_UNSET_TOKEN, False)

        elif not any([(i == config.ANNOTATION_LOWER_BODY_TOKEN) for i in lc]):
            shouldDisplayLowerColor = False
           
        if not shouldDisplayLowerColor:
            self._labeltool._mainwindow.property_editor4.enableCheckboxGroup(config.ANNOTATION_LOWER_COLOR_TOKEN, False)
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_LOWER_COLOR_TOKEN, False)
            self._labeltool._mainwindow.property_editor4.setCheckedCheckbox(config.ANNOTATION_LOWER_CLOTH_TOKEN, config.TAG_UNSET_TOKEN, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor4.enableCheckbox(config.ANNOTATION_LOWER_CLOTH_TOKEN, config.TAG_UNSET_TOKEN, False)
            self._labeltool._mainwindow.property_editor4.enableCheckboxGroup(config.ANNOTATION_LOWER_CLOTH_TOKEN, False)

 
        if any([(i == config.ANNOTATION_PEDESTRAIN_TOKEN) or (i == config.ANNOTATION_PERSONBIKE_TOKEN) for i in lc]):
            
            # shouldDisplayUpperColor = True
            # shouldDisplayLowerColor = any([(i == config.ANNOTATION_PEDESTRAIN_TOKEN) for i in lc])
            
            # ------------ set person's attributes checkboxs -------------------
            # Note that, i will set check status as per the first scene_item in selected_scene_items
            # ------------------------------------------------------------------
            LOG.info("editSelectedItems : set checked status for checkedbox in [Pedestrain, PersonBike]...")
            self._labeltool._mainwindow.property_editor5.enableCheckboxGroup(config.ANNOTATION_GENDER_TOKEN,    True)
            self._labeltool._mainwindow.property_editor5.enableCheckboxGroup(config.ANNOTATION_AGE_TOKEN,       True)
            self._labeltool._mainwindow.property_editor5.enableCheckboxGroup(config.ANNOTATION_ANGLE_TOKEN,      True)
            self._labeltool._mainwindow.property_editor5.enableCheckboxGroup(config.ANNOTATION_HAIR_STYLE_TOKEN, True)
 
            self._labeltool._mainwindow.property_editor5.setCheckedGroup(config.ANNOTATION_GENDER_TOKEN, False)
            gender = selected_scene_items[0]._model_item.get(config.ANNOTATION_GENDER_TOKEN, None)
            # LOG.info("gender = {}".format(gender))
            gender = gender if gender else config.TAG_UNSET_TOKEN
            self._labeltool._mainwindow.property_editor5.setCheckedCheckbox(config.ANNOTATION_GENDER_TOKEN, gender, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor5.enableCheckbox(config.ANNOTATION_GENDER_TOKEN, config.TAG_UNSET_TOKEN, False)

            self._labeltool._mainwindow.property_editor5.setCheckedGroup(config.ANNOTATION_AGE_TOKEN, False)
            age = selected_scene_items[0]._model_item.get(config.ANNOTATION_AGE_TOKEN, None)
            # LOG.info("age = {}".format(age))
            age = age if age else config.TAG_UNSET_TOKEN
            self._labeltool._mainwindow.property_editor5.setCheckedCheckbox(config.ANNOTATION_AGE_TOKEN, age, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor5.enableCheckbox(config.ANNOTATION_AGE_TOKEN, config.TAG_UNSET_TOKEN, False)

            self._labeltool._mainwindow.property_editor5.setCheckedGroup(config.ANNOTATION_ANGLE_TOKEN, False)
            angle = selected_scene_items[0]._model_item.get(config.ANNOTATION_ANGLE_TOKEN, None)
            # LOG.info("angle = {}".format(angle))
            angle = angle if angle else config.TAG_UNSET_TOKEN
            self._labeltool._mainwindow.property_editor5.setCheckedCheckbox(config.ANNOTATION_ANGLE_TOKEN, angle, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor5.enableCheckbox(config.ANNOTATION_ANGLE_TOKEN, config.TAG_UNSET_TOKEN, False)

            self._labeltool._mainwindow.property_editor5.setCheckedGroup(config.ANNOTATION_HAIR_STYLE_TOKEN, False)
            hstyle = selected_scene_items[0]._model_item.get(config.ANNOTATION_HAIR_STYLE_TOKEN, None)
            # LOG.info("hstyle = {}".format(hstyle))
            hstyle = hstyle if hstyle else config.TAG_UNSET_TOKEN
            self._labeltool._mainwindow.property_editor5.setCheckedCheckbox(config.ANNOTATION_HAIR_STYLE_TOKEN, hstyle, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor5.enableCheckbox(config.ANNOTATION_HAIR_STYLE_TOKEN, config.TAG_UNSET_TOKEN, False)
                
        else:
            # ------------ set person's attributes checkboxs -------------------
            self._labeltool._mainwindow.property_editor5.setCheckedCheckbox(config.ANNOTATION_GENDER_TOKEN,     config.TAG_UNSET_TOKEN, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor5.enableCheckbox(config.ANNOTATION_GENDER_TOKEN,         config.TAG_UNSET_TOKEN, False)
            self._labeltool._mainwindow.property_editor5.enableCheckboxGroup(config.ANNOTATION_GENDER_TOKEN,     False)
            self._labeltool._mainwindow.property_editor5.setCheckedCheckbox(config.ANNOTATION_AGE_TOKEN,        config.TAG_UNSET_TOKEN, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor5.enableCheckbox(config.ANNOTATION_AGE_TOKEN,            config.TAG_UNSET_TOKEN, False)
            self._labeltool._mainwindow.property_editor5.enableCheckboxGroup(config.ANNOTATION_AGE_TOKEN,        False)
            self._labeltool._mainwindow.property_editor5.setCheckedCheckbox(config.ANNOTATION_ANGLE_TOKEN,      config.TAG_UNSET_TOKEN, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor5.enableCheckbox(config.ANNOTATION_ANGLE_TOKEN,          config.TAG_UNSET_TOKEN, False)
            self._labeltool._mainwindow.property_editor5.enableCheckboxGroup(config.ANNOTATION_ANGLE_TOKEN,      False)
            self._labeltool._mainwindow.property_editor5.setCheckedCheckbox(config.ANNOTATION_HAIR_STYLE_TOKEN, config.TAG_UNSET_TOKEN, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.property_editor5.enableCheckbox(config.ANNOTATION_HAIR_STYLE_TOKEN,     config.TAG_UNSET_TOKEN, False)
            self._labeltool._mainwindow.property_editor5.enableCheckboxGroup(config.ANNOTATION_HAIR_STYLE_TOKEN, False)

 
        if self._labeltool._mainwindow.property_editor6:
            if any([i == config.ANNOTATION_VEHICLE_TOKEN for i in lc]):
                self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckboxGroup(config.ANNOTATION_VEHICLE_COLOR_TOKEN, True)
                self._labeltool._mainwindow.property_editor6.attrAreaWidget.setCheckedGroup(config.ANNOTATION_VEHICLE_COLOR_TOKEN, False)
                dummy, rgbTagListOfList, colorAttrNameList = parentModelItem.parseColorAttrs(useMyLabelName = True)
                if colorAttrNameList:
                    for kc in xrange(len(colorAttrNameList)):
                        self._labeltool._mainwindow.property_editor6.attrAreaWidget.setCheckedCheckboxs(colorAttrNameList[kc], rgbTagListOfList[kc], True)
                else:
                    self._labeltool._mainwindow.property_editor6.attrAreaWidget.setCheckedCheckbox(config.ANNOTATION_VEHICLE_COLOR_TOKEN, config.TAG_UNSET_TOKEN, True)
                if not config.ENABLE_SELECT_UNSET_FIELD:
                    self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckbox(config.ANNOTATION_VEHICLE_COLOR_TOKEN, config.TAG_UNSET_TOKEN, False)

                
                self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckboxGroup(config.ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN, True)
                type = selected_scene_items[0]._model_item.get(config.ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN, None)
                type = type if type else config.TAG_UNSET_TOKEN
                self._labeltool._mainwindow.property_editor6.attrAreaWidget.setCheckedCheckbox(config.ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN, type, True)
                if not config.ENABLE_SELECT_UNSET_FIELD:
                    self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckbox(config.ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN, config.TAG_UNSET_TOKEN, False)            
             
                self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckboxGroup(config.ANNOTATION_VEHICLE_ANGLE_TOKEN, True)
                type = selected_scene_items[0]._model_item.get(config.ANNOTATION_VEHICLE_ANGLE_TOKEN, None)
                type = type if type else config.TAG_UNSET_TOKEN
                self._labeltool._mainwindow.property_editor6.attrAreaWidget.setCheckedCheckbox(config.ANNOTATION_VEHICLE_ANGLE_TOKEN, type, True)
                if not config.ENABLE_SELECT_UNSET_FIELD:
                    self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckbox(config.ANNOTATION_VEHICLE_ANGLE_TOKEN, config.TAG_UNSET_TOKEN, False)            

            else:
                self._labeltool._mainwindow.property_editor6.attrAreaWidget.setCheckedCheckbox(config.ANNOTATION_VEHICLE_COLOR_TOKEN, config.TAG_UNSET_TOKEN, True)
                if not config.ENABLE_SELECT_UNSET_FIELD:
                    self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckbox(config.ANNOTATION_VEHICLE_COLOR_TOKEN, config.TAG_UNSET_TOKEN, False)            
                self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckboxGroup(config.ANNOTATION_VEHICLE_COLOR_TOKEN, False)
                  
                self._labeltool._mainwindow.property_editor6.attrAreaWidget.setCheckedCheckbox(config.ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN, config.TAG_UNSET_TOKEN, True)
                if not config.ENABLE_SELECT_UNSET_FIELD:
                    self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckbox(config.ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN, config.TAG_UNSET_TOKEN, False)            
                self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckboxGroup(config.ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN, False)

                self._labeltool._mainwindow.property_editor6.attrAreaWidget.setCheckedCheckbox(config.ANNOTATION_VEHICLE_ANGLE_TOKEN, config.TAG_UNSET_TOKEN, True)
                if not config.ENABLE_SELECT_UNSET_FIELD:
                    self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckbox(config.ANNOTATION_VEHICLE_ANGLE_TOKEN, config.TAG_UNSET_TOKEN, False)            
                self._labeltool._mainwindow.property_editor6.attrAreaWidget.enableCheckboxGroup(config.ANNOTATION_VEHICLE_ANGLE_TOKEN, False)


        if any([i == config.ANNOTATION_PERSONBIKE_TOKEN for i in lc]):
            self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.enableCheckboxGroup(config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN, True)
          
            # ------------ set plate type checkboxs -------------------
            self._labeltool._mainwindow.personbike_pannel.propertyEditorWidget.enableCheckboxGroup(config.ANNOTATION_PLATE_WIDGET_TOKEN, True)
            platetype = None
            checkboxsNameList = self._labeltool._mainwindow.personbike_pannel.propertyEditorWidget.getCheckboxsName(config.ANNOTATION_PLATE_WIDGET_TOKEN)
            found = None
            for a in checkboxsNameList:
                found = findModelItemsWithSpecificClassName(a, parentModelItem, 5)
                if found:
                    break
            platetype = found[0][0]['class'] if found and found[0] and found[0][0] else None
            if platetype:
                self._labeltool._mainwindow.personbike_pannel.propertyEditorWidget.setCheckedCheckbox(config.ANNOTATION_PLATE_WIDGET_TOKEN, platetype, True)
            
            # ------------ set personbike type checkboxs -------------------
            type = selected_scene_items[0]._model_item.get(config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN, None)
            type = type if type else config.TAG_UNSET_TOKEN
            self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.setCheckedCheckbox(config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN, type, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.enableCheckbox(config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN, config.TAG_UNSET_TOKEN, False)
        else:
            # ------------ set personbike type checkboxs -------------------
            self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.setCheckedCheckbox(config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN, config.TAG_UNSET_TOKEN, True)
            if not config.ENABLE_SELECT_UNSET_FIELD:
                self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.enableCheckbox(config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN, config.TAG_UNSET_TOKEN, False)
            
            self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.enableCheckboxGroup(config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN, False)
            self._labeltool._mainwindow.personbike_pannel.propertyEditorWidget.enableCheckboxGroup('plate', False)

        # ------------------------------------------------        
        # set uppercolor 
        # ------------------------------------------------        
        if shouldDisplayUpperColor:
            self._labeltool._mainwindow.property_editor4.enableCheckboxGroup(config.ANNOTATION_UPPER_COLOR_TOKEN, True)
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_UPPER_COLOR_TOKEN, False)
            rgbTagListOfList = None
            colorAttrNameList = None
            if (lc[0] == config.ANNOTATION_PEDESTRAIN_TOKEN) or (lc[0] == config.ANNOTATION_PERSONBIKE_TOKEN):
                dummy, rgbTagListOfList, colorAttrNameList = parentModelItem.parseColorAttrs(useMyLabelName = True)
                # print "colorAttrNameList = {} rgbTagListOfList = {}".format(colorAttrNameList, rgbTagListOfList)
            else:
                foundModelItemsAndIterativeLevelsNum = findModelItemsWithSpecificClassName(config.ANNOTATION_UPPER_BODY_TOKEN, selected_scene_items[0].modelItem())
                if foundModelItemsAndIterativeLevelsNum:
                    dummy, rgbTagListOfList, colorAttrNameList = foundModelItemsAndIterativeLevelsNum[0][0].parseColorAttrs()

            if colorAttrNameList:
                for kc in xrange(len(colorAttrNameList)):
                    self._labeltool._mainwindow.property_editor4.setCheckedCheckboxs(colorAttrNameList[kc], rgbTagListOfList[kc], True)
                
        # ------------------------------------------------        
        # set lowercolor 
        # ------------------------------------------------        
        if shouldDisplayLowerColor:
            self._labeltool._mainwindow.property_editor4.enableCheckboxGroup(config.ANNOTATION_LOWER_COLOR_TOKEN, True)
            self._labeltool._mainwindow.property_editor4.setCheckedGroup(config.ANNOTATION_LOWER_COLOR_TOKEN, False)
            rgbTagListOfList = None
            colorAttrNameList = None
            if lc[0] == config.ANNOTATION_PEDESTRAIN_TOKEN:
                dummy, rgbTagListOfList, colorAttrNameList = parentModelItem.parseColorAttrs(useMyLabelName = True)
            else:
                foundModelItemsAndIterativeLevelsNum = findModelItemsWithSpecificClassName(config.ANNOTATION_LOWER_BODY_TOKEN, selected_scene_items[0].modelItem())
                if foundModelItemsAndIterativeLevelsNum:
                    dummy, rgbTagListOfList, colorAttrNameList = foundModelItemsAndIterativeLevelsNum[0][0].parseColorAttrs()

            if colorAttrNameList:
                for kc in xrange(len(colorAttrNameList)):
                    self._labeltool._mainwindow.property_editor4.setCheckedCheckboxs(colorAttrNameList[kc], rgbTagListOfList[kc], True)


        # ---------------------
        # determine whether need display helmet color
        # ---------------------
        shouldDisplayHelmetColor = False
        if any([j == config.ANNOTATION_HELMET_WIDGET_TOKEN or j == config.ANNOTATION_HELMET_COLOR_TOKEN  for i in lc for j in config.ALLOWED_DISPLAY_OBJECTS_AND_ATTRIBUTE_STICKERS.get(i, [])] ) or \
           any([(i == config.ANNOTATION_PERSONBIKE_TOKEN) for i in lc]):
            shouldDisplayHelmetColor = True
 
        # ---------------------
        # display helmet color
        # ---------------------
        if shouldDisplayHelmetColor:
            self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.enableCheckboxGroup(config.ANNOTATION_HELMET_COLOR_TOKEN, True)
            self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.setCheckedGroup(config.ANNOTATION_HELMET_COLOR_TOKEN, False)
            rgbTagListOfList = None
            colorAttrNameList = None
            
            helmetModelItem = None
            for item in selected_scene_items:
                if not item: break
                if ( item.get_label_class() == config.ANNOTATION_HELMET_WIDGET_TOKEN):
                    helmetModelItem = item.modelItem()
            
            if not helmetModelItem:
                foundModelItemsAndIterativeLevelsNum = findModelItemsWithSpecificClassName(config.ANNOTATION_HELMET_WIDGET_TOKEN, parentModelItem)
                if foundModelItemsAndIterativeLevelsNum:
                    helmetModelItem = foundModelItemsAndIterativeLevelsNum[0][0]

            if helmetModelItem:
                dummy, rgbTagListOfList, dummy2 = helmetModelItem.parseHelmetColorAttrs()

            if rgbTagListOfList:
                for kc in xrange(len(rgbTagListOfList)):
                    self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.setCheckedCheckbox(config.ANNOTATION_HELMET_COLOR_TOKEN, rgbTagListOfList[kc], True)
            else:
                self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.setCheckedCheckbox(config.ANNOTATION_HELMET_COLOR_TOKEN, config.TAG_UNSET_TOKEN, True)
        else:
            self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.enableCheckboxGroup(config.ANNOTATION_HELMET_COLOR_TOKEN, False)
            self._labeltool._mainwindow.personbike_pannel.attrAreaWidget.setCheckedCheckbox(config.ANNOTATION_HELMET_COLOR_TOKEN, config.TAG_UNSET_TOKEN, True)


        # ---------------------
        # display obj type
        # ---------------------
        if any([(i == config.ANNOTATION_PEDESTRAIN_TOKEN) or (i == config.ANNOTATION_PERSONBIKE_TOKEN) or (i == config.ANNOTATION_VEHICLE_TOKEN) for i in lc]):
            # ------------ set obj type checkboxs -------------------    
            self._labeltool._mainwindow.property_editor1.propertyEditorWidget.enableCheckboxGroup(config.ANNOTATION_OBJTYPE_WIDGET_TOKEN, True)
            type = selected_scene_items[0]._model_item.get_label_class()
            if type: # type = type if type else config.TAG_UNSET_TOKEN
                self._labeltool._mainwindow.property_editor1.propertyEditorWidget.setCheckedCheckbox(config.ANNOTATION_OBJTYPE_WIDGET_TOKEN, type, True)
            # if not config.ENABLE_SELECT_UNSET_FIELD:
            #    self._labeltool._mainwindow.property_editor1.propertyEditorWidget.enableCheckbox(config.ANNOTATION_OBJTYPE_WIDGET_TOKEN, config.TAG_UNSET_TOKEN, False)
        else:            
            # ------------ set obj type checkboxs -------------------    
            # self._labeltool._mainwindow.property_editor1.propertyEditorWidget.setCheckedCheckbox(config.ANNOTATION_OBJTYPE_WIDGET_TOKEN, config.TAG_UNSET_TOKEN, True)
            # if not config.ENABLE_SELECT_UNSET_FIELD:
            #    self._labeltool._mainwindow.property_editor1.propertyEditorWidget.enableCheckbox(config.ANNOTATION_OBJTYPE_WIDGET_TOKEN, config.TAG_UNSET_TOKEN, False)
            
            self._labeltool._mainwindow.property_editor1.propertyEditorWidget.enableCheckboxGroup(config.ANNOTATION_OBJTYPE_WIDGET_TOKEN, False)

	return


                
    # =====================================================================================================
    # zx comment: when any items drawn on image is selected or deselected, this function will be called!
    # =====================================================================================================
    def editSelectedItems(self):
        selected_scene_items = self.selectedItems()
        
        if len(selected_scene_items) > 0 :   # if self._inserter is None or len(selected_scene_items) > 0:

            annotationModelItems = [item.modelItem() for item in selected_scene_items]
            label_classes = self.get_label_classes(annotationModelItems)
            # LOG.info("AnnotaionScene.editSelectedItems ... len(selected_scene_items) {} selected_scene_items {} annotationModelItems {} label_classes {} ...".format(len(selected_scene_items), selected_scene_items, annotationModelItems, label_classes))
            # LOG.info("label_classses = {}".format(set([item[config.METADATA_LABELCLASS_TOKEN] for item in annotationModelItems if config.METADATA_LABELCLASS_TOKEN in item])))

            
            # for edit in self._labeltool.propertyeditors():
            #     if edit is None:
            #	      continue
            #     edit.startEditMode(annotationModelItems)
            
            for edit in self._labeltool.propertyeditors():
                if edit:
                    if any([i in edit.getSupportedInserters() for i in label_classes]):
                        edit.startEditMode(annotationModelItems)
        
        else:
            if config.ENABLE_TOP_OBJECT_MODE or config.ENABLE_EXIT_INSERT_MODE_AFTER_SWTICHING_IMG:
                self._labeltool._mainwindow.property_editor1.attrAreaWidget.setCheckedAllGroups(False)
                self._labeltool._mainwindow.property_editor2.setCheckedAll(False)
                self._labeltool._mainwindow.property_editor3.setCheckedAll(False)
                if self._labeltool._mainwindow.property_editor6:
                    self._labeltool._mainwindow.property_editor6.attrAreaWidget.setCheckedAllGroups(False)
                    
                 
            
        # zx: enable or disable attr widgets
        self.setWidgetState(selected_scene_items)
            
        
        # update _selectedDisplayItemsList
        lc = [item.get_label_class() for item in selected_scene_items ]
        LOG.info("selected_scene_items_number = {}".format(len(selected_scene_items)))
        if len(selected_scene_items) == 1:
            # there is one inserter is selected. we record it	
            self._selectedDisplayItemsList.append((lc[0], selected_scene_items[0].modelItem()))
            LOG.info("selectedDisplayedItemsList = {}".format(self._selectedDisplayItemsList))

            width = -1
            height = -1
            if ( isinstance(selected_scene_items[0], RectItem) ):

                rect = getQRectFFromModelItem(selected_scene_items[0]._model_item)
                width = rect.width()   if rect else -1
                height = rect.height() if rect else -1
            elif ( isinstance(selected_scene_items[0], LineItem) ):
                line = getQLineFFromModelItem(selected_scene_items[0]._model_item)
                width = abs(line.x2() - line.x1())
                height = abs(line.y2() - line.y1())
            elif ( isinstance(selected_scene_items[0], PolygonItemInserter) ):
                if selected_scene_items[0]._itemPos:
                    brect = selected_scene_items[0]._itemPos.boundingRect()
                    width = brect.width()
                    height = brect.height()

            self.itemIsInsertedOrSelected.emit(width, height, 3)
 
        else:
            # all selected inserters is deselected
            self._selectedDisplayItemsList = [] 
            LOG.info("selectedDisplayedItemsList = {}".format(self._selectedDisplayItemsList))
        
        self._labeltool.setConnectLabelMode(enabled = self._labeltool._enableAutoConnectLabelMode)
        self._labeltool._mainwindow.statisticNdisplaySelectedObjsCnt()

    #
    # key event handlers
    #______________________________________________________________________________________________________
    def selectNextItem(self, reverse=False):
        # disable inserting
        # TODO: forward this to the ButtonArea
        self._inserter = None

        # set focus to the view, so that subsequent keyboard events are forwarded to the scene
        if len(self.views()) > 0:
            self.views()[0].setFocus(True)

        # get the current selected item if there is any
        selected_item = None
        found = True
        if len(self.selectedItems()) > 0:
            selected_item = self.selectedItems()[0]
            selected_item.setSelected(False)
            found = False

        items = [item for item in self.items()
                 if item.flags() & QGraphicsItem.ItemIsSelectable] * 2
        if reverse:
            items.reverse()

        for item in items:
            if item is selected_item:
                found = True
                continue

            if found and item is not selected_item:
                item.setSelected(True)
                break

    def selectAllItems(self):
        for item in self.items():
            item.setSelected(True)

    def keyPressEvent(self, event):
        LOG.debug("keyPressEvent %s" % event)

        if self._model is None or self._image_item is None:
            event.ignore()
            return

        if self._inserter is not None:
            # insert mode
            self._inserter.keyPressEvent(event, self._image_item)
        else:
            # edit mode
            if event.key() == Qt.Key_Delete:
                self.deleteSelectedItems()
                event.accept()

            elif event.key() == Qt.Key_Escape:
                # deselect all selected items
                for item in self.selectedItems():
                    item.setSelected(False)
                event.accept()

            elif len(self.selectedItems()) > 0:
                for item in self.selectedItems():
                    item.keyPressEvent(event)

        QGraphicsScene.keyPressEvent(self, event)

    #
    # slots for signals from the model
    # this is the implemenation of the scene as a view of the model
    #______________________________________________________________________________________________________
    def dataChanged(self, indexFrom, indexTo):
        if self._image_item is None:  #or self._image_item.index() != indexFrom.parent().parent():
            return

        item = self.itemFromIndex(indexFrom.parent())
        if item is not None:
            item.dataChanged()
            
        if config.ENABLE_STATISTIC_OBJ_INFO:
            self._labeltool._mainwindow.objViewModeInfoWidget.update(GET_ANNOTATION(self._objViewModeTopModelItem) if self._objViewModeTopModelItem else None)
        
        modelitem = self._model.itemFromIndex(indexFrom)
        if modelitem:
            rect = getQRectFFromModelItem(modelitem)
            if rect:
                width = rect.width()   if rect else -1
                height = rect.height() if rect else -1
            else:
                line = getQLineFFromModelItem(modelitem)
                if line:
                    width = abs(line.x2() - line.x1())
                    height = abs(line.y2() - line.y1())
                else:
                    width = -1
                    height = -1
            self.itemIsInsertedOrSelected.emit(width, height, 3)
  
    # zx999
    # ================================================================================
    # zx comment: When some graphic items was added on the image, this function will be called    
    # ================================================================================
    def rowsInserted(self, index, first, last):
        LOG.info("AnnotationScene: rowsInserted(index = {}, first = {}, last = {})....".format(index, first, last))
        # if self._image_item is None or self._image_item.index() != index:
        if self._image_item is None:
            return

        LOG.info("AnnotationScene: rowsInserted(index = {}, first = {}, last = {}) call insertChildItems....".format(index, first, last))
        modelitem = self._model.itemFromIndex(index)
        if modelitem is None:
            return
        LOG.info("modelitem inserted = {} ".format(modelitem.get_label_class()))
        if self._sceneViewMode == config.IMG_VIEW_MODE:
            sceneRect = None
        elif self._sceneViewMode == config.OBJ_VIEW_MODE:
            # if 0
            # zx fix bug @ 20170215
            # modelitem = self._objViewModeTopModelItem
            # if modelitem is None: return
            # endif
            # rect = getQRectFFromModelItem(modelitem)
            # LOG.info("modelitem.rect = {} ".format(rect))
            sceneRect = self._objViewModeSceneRectWRTImg
            
        self.insertChildItems(modelitem, sceneRect, first, last, isInsertingNewItems = True)

        if config.ENABLE_STATISTIC_OBJ_INFO:
            self._labeltool._mainwindow.objViewModeInfoWidget.update(GET_ANNOTATION(self._objViewModeTopModelItem) if self._objViewModeTopModelItem else None)

        return


    def rowsAboutToBeRemoved(self, index, first, last):
        LOG.info("rowsAboutToBeRemoved(first = {}, last = {})...".format(first, last))
        
        if self._image_item is None or self._image_item.index() != index:
            return

        for row in range(first, last+1):
            items = self.itemsFromIndex(index.child(row, 0))
            LOG.info("rowsAboutToBeRemoved(row = {}, rows[0].Name = {})...".format(row, items[0].get_label_class())) 
            for item in items:
                # if the item has a parent item, do not delete it
                # we assume, that the parent shares the same model index
                # and thus removing the parent will also remove the child
                if item.parentItem() is not None:
                    continue
                self.removeItem(item)
                if item._model_item == self._objViewModeTopModelItem:
                    LOG.info("rowsAboutToBeRemoved ..find matched item ..")
                    self.update_objViewModeTopModelItemRowIdxInParent(delta = -1, clearItem = True) 
                    # self._objViewModeTopModelItem = None
                # else:
                #    self.update_objViewModeTopModelItemRowIdxInParent(delta = 0) 
                   
        if config.ENABLE_STATISTIC_OBJ_INFO:
            self._labeltool._mainwindow.objViewModeInfoWidget.update(GET_ANNOTATION(self._objViewModeTopModelItem) if self._objViewModeTopModelItem else None)


    def rowsRemoved(self, index, first, last):

        LOG.info("rowsRemoved(first = {}, last = {})...".format(first, last))

        if config.ENABLE_STATISTIC_OBJ_INFO:
            self._labeltool._mainwindow.objViewModeInfoWidget.update(GET_ANNOTATION(self._objViewModeTopModelItem) if self._objViewModeTopModelItem else None)

        pass


    def itemFromIndex(self, index):
        for item in self.items():
            # some graphics items will not have an index method,
            # we just skip these
            if hasattr(item, 'index') and item.index() == index:
                return item
        return None

    def itemsFromIndex(self, index):
        items = []
        for item in self.items():
            # some graphics items will not have an index method,
            # we just skip these
            if hasattr(item, 'index') and item.index() == index:
                items.append(item)
        return items

    #______________________________________________________________________________________________________
    #
    # message handling and displaying
    #______________________________________________________________________________________________________
    def setMessage(self, message):
        if self._message is not None:
            self.clearMessage()

        if message is None or message == "":
            return

        self._message = message.replace('\n', '<br />')
        self._message_text_item = QGraphicsTextItem()
        self._message_text_item.setHtml(self._message)
        self._message_text_item.setPos(20, 20)
        self.invalidate(QRectF(), QGraphicsScene.ForegroundLayer)

    def clearMessage(self):
        if self._message is not None:
            self._message_text_item = None
            self._message = None
            self.invalidate(QRectF(), QGraphicsScene.ForegroundLayer)

    def drawForeground(self, painter, rect):
        QGraphicsScene.drawForeground(self, painter, rect)

        if self._message is not None:
            assert self._message_text_item is not None

            painter.setTransform(QTransform())
            painter.setBrush(QColor('lightGray'))
            painter.setPen(QPen(QBrush(QColor('black')), 2))

            br = self._message_text_item.boundingRect()

            painter.drawRoundedRect(QRectF(10, 10, br.width()+20, br.height()+20), 10.0, 10.0)
            painter.setTransform(QTransform.fromTranslate(20, 20))
            painter.setPen(QPen(QColor('black'), 1))

            self._message_text_item.paint(painter, QStyleOptionGraphicsItem(), None)


    def checkModelItemValidity(self, clsNameOfThisModelItem, qRectOrQPointOfThisModelItem, parentModelItem, image_item, enablePopupMsgBox = True, enableEmitStatusMsg = False, enableCountingThisModelItem = False):
        clsNameOfChild = clsNameOfThisModelItem
        _tp = parentModelItem if parentModelItem is not None else image_item
        clsNameOfParent = _tp.get_label_class() if hasattr(_tp, 'get_label_class') else config.GUI_IMAGE_TEXT
        (isAllowed, isBoundedInParent, rectBoundary, allowedParentsClsName, allowedChildNum) = self.validateRelationshipWithParent(parentModelItem, clsNameOfParent, clsNameOfChild)
        
        if rectBoundary:
            isContained = rectBoundary.contains(qRectOrQPointOfThisModelItem) if qRectOrQPointOfThisModelItem else True
        else:
            isContained = False
         
        LOG.debug("@@@@@@@@@ isAllowed = {} isContained = {} isBoundedInParent = {} rectBoundary = {} ".format( isAllowed, isContained, isBoundedInParent, rectBoundary ))
            
        LOG.info("clsNameOfChild = {} clsNameOfParent = {} isAllowed = {} isContained = {} allowedParentsClsName = {} _enableAutoConnectLabelMode = {} len(self._selectedDisplayItemsList) = {}".format(
            clsNameOfChild, clsNameOfParent, isAllowed, isContained, allowedParentsClsName, self._labeltool._enableAutoConnectLabelMode, len(self._selectedDisplayItemsList)))

        displayTextOfChild = config.getSpecificLabelInfo(clsNameOfChild, config.METADATA_DISPLAYTEXT_TOKEN)
        displayTextOfParent = config.getSpecificLabelInfo(clsNameOfParent,
                                                          config.METADATA_DISPLAYTEXT_TOKEN) if clsNameOfParent != config.GUI_IMAGE_TEXT else  config.GUI_IMAGE_TEXT
        if (not isAllowed) or (isBoundedInParent and (not isContained)):

            if (not isAllowed):    
                
                if (not self._labeltool._enableAutoConnectLabelMode) and (self._selectedDisplayItemsList is not None) and (len(self._selectedDisplayItemsList) == 1):
                    msg = config.GUI_INSERT_ANNOTATION_NOT_ALLOWED_TIP.format(displayTextOfChild, displayTextOfParent)
                else:
                    allowedParentDesc = ''
                    for i in allowedParentsClsName:
                        allowedParentDesc = (allowedParentDesc + config.GUI_CONCATINATION_TEXT) if allowedParentDesc else allowedParentDesc
                        displayTextOfAllowedParent = config.getSpecificLabelInfo(i, config.METADATA_DISPLAYTEXT_TOKEN)
                        displayTextOfAllowedParent = displayTextOfAllowedParent if displayTextOfAllowedParent else config.GUI_IMAGE_TEXT
                        allowedParentDesc += "'" + displayTextOfAllowedParent + "'"
                
                    msg = config.GUI_INSERT_ANNOTATION_NOT_ALLOWED_TIP2.format(displayTextOfChild, allowedParentDesc, displayTextOfParent)
                
            elif (isBoundedInParent and (not isContained)):
                msg = config.GUI_INSERT_ANNOTATION_NOT_IN_BOUNDARY_TIP.format(displayTextOfChild, displayTextOfParent)
            
            if enableEmitStatusMsg:
                self._labeltool.statusMessage.emit(msg, config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS) 
                
            if enablePopupMsgBox:
                QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)

            return False, rectBoundary
        
        _existentChildItems = findModelItemsWithSpecificClassName(clsNameOfThisModelItem, parentModelItem)
        LOG.debug("len(_existentChildItems) = {} allowedChildNum = {}".format(len(_existentChildItems), allowedChildNum))
        if ( (_existentChildItems is not None) and ((len(_existentChildItems) + 1 if enableCountingThisModelItem else 0) > allowedChildNum) and (allowedChildNum >= 0)):
            msg = config.GUI_INSERT_ANNOTATION_EXCEED_ALLOWED_NUM_TIP.format(displayTextOfParent, allowedChildNum, displayTextOfChild, len(_existentChildItems), displayTextOfChild)
            if enableEmitStatusMsg:
                self._labeltool.statusMessage.emit(msg, config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS) 
                
            if enablePopupMsgBox:
                QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)

            return False, rectBoundary
 
            
        return True, rectBoundary    