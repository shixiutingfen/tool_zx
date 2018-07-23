# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"
import logging
from PyQt4.Qt import *
import datetime
from sloth.conf import config
from sloth.gui import utils
from sloth.annotations.model import GET_ANNOTATION, getQRectFFromModelItem, getQPointFFromModelItem, convertQRectFToModelItemKeyValues, convertQPointFToModelItemKeyValues
from sloth.gui.utils import ROUND_VALUE
import copy

LOG = logging.getLogger(config.LOG_FILE_NAME)


# convenience functions for creating hotkey functions
class cycleValue:
    def __init__(self, itemkey, valuelist):
        self.itemkey = itemkey
        self.valuelist = valuelist

    def __call__(self, item):
        if isinstance(self.itemkey, IgnorePrefix):
            key = self.itemkey.value
        else:
            key = item.prefix() + self.itemkey

        if len(self.valuelist) > 0:
            oldvalue = item._model_item.get(key, None)
            if oldvalue is None:
                nextindex = 0
            else:
                try:
                    nextindex = self.valuelist.index(oldvalue) + 1
                    nextindex %= len(self.valuelist)
                except ValueError:
                    nextindex = 0
            newvalue = self.valuelist[nextindex]
            if newvalue is None:
                if oldvalue is not None:
                    item._model_item.delete(key)
            else:
                item._model_item[key] = self.valuelist[nextindex]
            item.dataChanged()


def setValue(itemkey, newvalue):
    return lambda self: _setValue(self, itemkey, newvalue)


def _setValue(self, itemkey, newvalue):
    if isinstance(itemkey, IgnorePrefix):
        itemkey = itemkey.value
    else:
        itemkey = self.prefix() + itemkey
    oldvalue = self._model_item.get(itemkey, None)
    if newvalue is None:
        if oldvalue is not None:
            self._model_item.delete(itemkey)
    elif newvalue != oldvalue:
        self._model_item[itemkey] = newvalue
    self.dataChanged()


class IgnorePrefix:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class BaseItem(QAbstractGraphicsShapeItem):
    """
    Base class for visualization items.
    """

    cycleValuesOnKeypress = {}
    hotkeys = {}
    defaultAutoTextKeys = []

    def get_label_class(self):
        lc = None
        if self._model_item is not None:
            lc = self._model_item.get_label_class()
            return lc
        return lc

    def get_label_displaytext(self):
        lc = None
        if self._model_item is not None:
            lc = self._model_item.get_label_displaytext()
            return lc
        return lc
             
    def get_annotation(self):
        if self._model_item is not None:
            return self._model_item.getAnnotations(recursive = False) 
        return None
             
    def set_imgsz(self, sz):
        self._imgsz = sz


    def set_rectBoundaryWRTScene(self, qRrectF):
        self._QRectBoundary = qRrectF
                     
    def __init__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        """
        Creates a visualization item.
        """
        QAbstractGraphicsShapeItem.__init__(self, parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemSendsGeometryChanges |
                      QGraphicsItem.ItemSendsScenePositionChanges)

        self._model_item = model_item
        if self._model_item is not None:
            self._model_item.model().dataChanged.connect(self.onDataChanged)

        # initialize members
        self._prefix = prefix
        self._auto_text_keys = self.defaultAutoTextKeys[:]
        self._text = ""
        self._text_bg_brush = None
        self._text_item = QGraphicsTextItem(self)
        self._text_item.setPos(0, 0)
        self._text_item.setAcceptHoverEvents(False)
        self._text_item.setFlags(QGraphicsItem.ItemIgnoresTransformations)
        self._text_item.setHtml(self._compile_text())
        self._valid = True
        
        self._idName = idName
        self._signalObj = signalObj
        self._sceneRect = sceneRect
        self._QRectBoundary = None
        self._attrAnnoMode = config.ANNOTATION_BBOX_ANNOMODE_TOKEN
        self._needDrawDisplayText = False
        self._drawDisplayText = None
        
        # print "idname {} _sceneRect {}".format(self._idName, sceneRect)

        if len(self.cycleValuesOnKeypress) > 0:
            logging.warning("cycleValueOnKeypress is deprecated and will be removed in the future. " +
                            "Set BaseItem.hotkeys instead with cycleValue()")

        self.setDefaultColor()
        return

    def setDefaultColor(self):
        self._displayQColor = Qt.yellow     # default display color if this item has not been set with displayColor configuration
        if self._model_item is not None:
            c = self._model_item.getColor()
            # print "self._model_item.getColor() = {}".format(c)
            if c is not None:
                self._displayQColor = c
        self.setColor(self._displayQColor)
        return
 

    def onDataChanged(self, indexFrom, indexTo):
        # FIXME why is this not updated, when changed graphically via attribute box ?
        #print "onDataChanged", self._model_item.index(), indexFrom, indexTo, indexFrom.parent()
        if indexFrom == self._model_item.index():
            self.setColor(self._displayQColor)
            # print "hit"
            # self._text_item.setHtml(self._compile_text())

    def modelItem(self):
        """
        Returns the model item of this items.
        """
        return self._model_item

    def index(self):
        """
        Returns the index of this item.
        """
        return self._model_item.index()

    def prefix(self):
        """
        Returns the key prefix of the item.
        """
        return self._prefix

    def setPen(self, penColor, penWidth = config.DEFAULT_BOX_LINE_WIDTH):
        pen = QPen(penColor, penWidth)  # convert to QPen if argument is a QColor
        QAbstractGraphicsShapeItem.setPen(self, pen)
        self._text_item.setDefaultTextColor(pen.color())

    def setText(self, text=""):
        """
        Sets a text to be displayed on this item.
        """
        self._text = text
        self._text_item.setHtml(self._compile_text())

    def text(self):
        return self._text

    def setTextBackgroundBrush(self, brush=None):
        """
        Sets the brush to be used to fill the background region
        behind the text. Set to None to not draw a background
        (leave transparent).
        """
        self._text_bg_brush = brush

    def textBackgroundBrush(self):
        """
        Returns the background brush for the text region.
        """
        return self._text_bg_brush

    def setAutoTextKeys(self, keys=None):
        """
        Sets the keys for which the values from the annotations
        are displayed automatically as text.
        """
        self._auto_text_keys = keys or []
        self._text_item.setHtml(self._compile_text())

    def autoTextKeys(self):
        """
        Returns the list of keys for which the values from
        the annotations are displayed as text automatically.
        """
        return self._auto_text_keys

    def isValid(self):
        """
        Return whether this graphics item is valid, i.e. has
        a matching, valid model item connected to it.  An item is
        by default valid, will only be set invalid on failure.
        """
        return self._valid

    def setValid(self, val):
        self._valid = val

    def _compile_text(self):
        text_lines = []
        if self._text != "" and self._text is not None:
            text_lines.append(self._text)
        for key in self._auto_text_keys:
            text_lines.append("%s: %s" % \
                    (key, self._model_item.get(key, "")))
        return '<br/>'.join(text_lines)

    def dataChanged(self):
        self.dataChange()
        self._text_item.setHtml(self._compile_text())
        self.update()

    def dataChange(self):
        pass

    def updateModel(self, ann=None):
        if ann is not None:
            self._model_item.update(ann)

    def boundingRect(self):
        return QRectF(0, 0, 0, 0)

    def setColor(self, color):
        self.setPen(color) 
        self.setBrush(color)
        self.update()

    def paint(self, painter, option, widget=None):
        pass

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            # print "itemChange call updateModel ..."
            self.updateModel()
        return QAbstractGraphicsShapeItem.itemChange(self, change, value)

    def keyPressEvent(self, event):
        """
        This handles the value cycling as defined in cycleValuesOnKeypress.
        """
        if str(event.text()) in self.cycleValuesOnKeypress:
            itemkey, valuelist = self.cycleValuesOnKeypress[str(event.text())]
            if isinstance(itemkey, IgnorePrefix):
                itemkey = itemkey.value
            else:
                itemkey = self.prefix() + itemkey
            if len(valuelist) > 0:
                oldvalue = self._model_item.get(itemkey, None)
                if oldvalue is None:
                    nextindex = 0
                else:
                    try:
                        nextindex = valuelist.index(oldvalue) + 1
                        nextindex %= len(valuelist)
                    except ValueError:
                        nextindex = 0
                newvalue = valuelist[nextindex]
                if newvalue is None:
                    if oldvalue is not None:
                        self._model_item.delete(itemkey)
                else:
                    self._model_item[itemkey] = valuelist[nextindex]
                self.dataChanged()
                event.accept()
        elif str(event.text()) in self.hotkeys:
            self.hotkeys[str(event.text())](self)
            event.accept()
            
    def updateInfo(self, displayText, displayColor):
        self._drawDisplayText = displayText
        self._displayQColor = utils.colorStrToQtColor(displayColor) if (self._attrAnnoMode == config.ANNOTATION_BBOX_ANNOMODE_TOKEN) else self._displayQColor      
        self.setColor(self._displayQColor) 
        self.update()
        return
            
    def calcObjDrawDisplayText(self, thisItemLabelName, thisItemAnnotationInfo):
        self._drawDisplayText = None
        tmp = thisItemAnnotationInfo.get(config.METADATA_DRAW_DISPLAYTEXT_TOKEN, None)
        overAttr = config.OVERIDE_ATTRS_DICT.get(thisItemLabelName, None)
        if overAttr:
            tmp = config.getSpecificLabelInfo(overAttr, config.METADATA_DRAW_DISPLAYTEXT_TOKEN)
        if not tmp: tmp = config.getSpecificLabelInfo(thisItemLabelName, config.METADATA_DRAW_DISPLAYTEXT_TOKEN)
        if tmp: self._needDrawDisplayText = tmp     
        
        if True: # if self._needDrawDisplayText:
            self._drawDisplayText = thisItemAnnotationInfo.get(config.METADATA_DISPLAYTEXT_TOKEN, None)
            if not self._drawDisplayText:
                self._drawDisplayText = config.getSpecificLabelInfo(thisItemLabelName, config.METADATA_DISPLAYTEXT_TOKEN)

        # print u"calcObjDrawDisplayText: thisItemLabelName = {} _drawDisplayText = {}".format(thisItemLabelName, self._drawDisplayText)
        return


    def calcAttrOverideDrawDisplayText(self, thisItemLabelName, thisItemAnnotationInfo):
        attrsTupleOfTuple = config.OBJ_TO_CHILDOBJ_AND_ATTR_DICT.get(thisItemLabelName, None)
        if (attrsTupleOfTuple is not None):
            for attrTuple in attrsTupleOfTuple:
                if (attrTuple[1] != 0):   continue # 0 means attribute
                attrName = attrTuple[0]
                attrOption = self._model_item.get(attrName, None)
                # print u"calcAttrOverideDrawDisplayText: thisItemLabelName = {} attrName = {} attrOption = {}".format(thisItemLabelName, attrName, attrOption)
                overAttr = config.OVERIDE_ATTRS_DICT.get(thisItemLabelName, None)
                if overAttr and (attrName == overAttr):
                    if attrOption is None: attrDisplayText = None
                    else:                  attrDisplayText = config.getLabelText(attrOption) 
                    tmpmode = config.getSpecificLabelInfo(attrName, "annotatemode")
                    # print u"calcAttrOverideDrawDisplayText: thisItemLabelName = {} attrName = {} getannotationmode = {}".format(thisItemLabelName, attrName, tmpmode)
                    self._attrAnnoMode = tmpmode.lower() if tmpmode else self._attrAnnoMode

                    self._drawDisplayText = attrDisplayText if (self._attrAnnoMode == config.ANNOTATION_BBOX_ANNOMODE_TOKEN) else self._drawDisplayText
                else:
                    if attrOption is None: continue
                
        # print u"calcAttrOverideDrawDisplayText: thisItemLabelName = {} _attrAnnoMode = {} _drawDisplayText = {}".format(thisItemLabelName, self._attrAnnoMode, self._drawDisplayText)
        
        return     
           
                
    def calcObjDisplayColor(self, thisItemLabelName, thisItemAnnotationInfo):
        colorstr = thisItemAnnotationInfo.get(config.METADATA_DISPLAYCOLOR_TOKEN, None)
        if colorstr is None:
            colorstr = config.getSpecificLabelInfo(thisItemLabelName, config.METADATA_DISPLAYCOLOR_TOKEN)
        if colorstr:
            self._displayQColor, dummy = utils.getColorDesc(colorstr, True)
        return
     
    def calcAttrOverideDisplayColor(self, thisItemLabelName, thisItemAnnotationInfo):   
        attrsTupleOfTuple = config.OBJ_TO_CHILDOBJ_AND_ATTR_DICT.get(thisItemLabelName, None)
        if (attrsTupleOfTuple is not None):
            for attrTuple in attrsTupleOfTuple:
                if (attrTuple[1] != 0):   continue # 0 means attribute
                attrName = attrTuple[0]
                attrOption = self._model_item.get(attrName, None)
                if attrOption is None:
                    continue
                attrDisplayColor = config.getLabelColor(attrOption) 
                self._attrAnnoMode = config.getSpecificLabelInfo(attrName, "annotatemode")
                self._attrAnnoMode = self._attrAnnoMode.lower() if self._attrAnnoMode else config.ANNOTATION_ATTR_ANNOMODE_TOKEN               
                self._displayQColor = utils.colorStrToQtColor(attrDisplayColor) if (self._attrAnnoMode == config.ANNOTATION_BBOX_ANNOMODE_TOKEN) else self._displayQColor
        # print u"calcAttrOverideDisplayColor: thisItemLabelName = {} _attrAnnoMode = {}".format(thisItemLabelName, self._attrAnnoMode)    
        return
                



class PointItem(BaseItem):
    """
    Visualization item for points.
    """
    def __init__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        BaseItem.__init__(self, idName, signalObj, model_item, sceneRect, prefix, parent)

        labelName = model_item.get_label_class()
        # LOG.info(u"CREATE PointItem with model_item {} prefix {} parent {}".format(model_item, prefix, parent))
        # LOG.info(u"CREATE PointItem model_item.get_label_class={} get_label_displaytext ={}".format(labelName, model_item.get_label_displaytext()))
        # LOG.info(u"self._model_item.getLabelText={}".format(self._model_item.getLabelText()))
        self._radius = 2
        self._point = None
        anno = self._model_item.getAnnotations(recursive = False)  
        LOG.debug("before update: PointItem._model_item.getAnnotations() = {} sceneRect = {}".format(anno, sceneRect))

        self.updatePoint(self.dataToPoint(self._model_item))

        anno = self._model_item.getAnnotations(recursive = False)  
        LOG.debug("afer update: PointItem._model_item.getAnnotations() = {}".format(anno))
        
        self._needFill = anno.get(config.METADATA_FILL_TOKEN, None)
        if self._needFill is None:
            self._needFill = config.getSpecificLabelInfo(labelName, config.METADATA_FILL_TOKEN)
        self._needFill = self._needFill if self._needFill is not None else False

        
        # -------------------------------------------------------------
        # determine Rect's draw text
        # -------------------------------------------------------------
        self.calcObjDrawDisplayText(labelName, anno)
        self.calcAttrOverideDrawDisplayText(labelName, anno)

        # -------------------------------------------------------------
        # determine Rect's display color
        # -------------------------------------------------------------
        self.calcObjDisplayColor(labelName, anno)
        self.calcAttrOverideDisplayColor(labelName, anno)
        self.setColor(self._displayQColor)
        
        # LOG.debug("PointItem init: rect {} model_item {} _needFillRect {} _drawDisplayText {} _displayQColor {} ".format(self._rect, model_item, self._needFillRect, self._drawDisplayText, self._displayQColor))
        return

        
        
    def setRadius(self, radius):
        self.prepareGeometryChange()
        self._radius = radius
        self.update()

    def radius(self):
        return self._radius

    def __call__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        pointitem = PointItem(idName, signalObj, model_item, sceneRect, prefix, parent)
        pointitem.setPen(self.pen())
        pointitem.setBrush(self.brush())
        pointitem.setRadius(self._radius)
        return pointitem

    def dataToPoint(self, model_item):
        if model_item is None:
            return

        try:
            point = getQPointFFromModelItem(model_item, self.prefix())
            anchor = QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft()
            # print "point = {} anchor = {} diff = {}".format(point, anchor, point - anchor)
            return (point - anchor)
        except KeyError as e:
            LOG.debug("PointItem: Could not find expected key in item: "
                      + str(e) + ". Check your config!")
            self.setValid(False)
            return QPointF()


    def updatePoint(self, point):
        if point == self._point:
            return

        self.prepareGeometryChange()
        self._point = point
        self.setPos(self._point)


    # ========================================================================================== 
    # zx comment: Here is the key function which really determine this annotation content in json file
    # ========================================================================================== 
    def updateModel(self, needEmitDataChanged = True):
        
        self._point = self.scenePos()
        # LOG.info("RectItem.updateModel... self._point = {} self._model_item.getAnnotations = {} ".format(self._point, self._model_item.getAnnotations()))
        
        modeldesc = convertQPointFToModelItemKeyValues(self.scenePos() + (QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft()), self.prefix())
           
        # LOG.info("RectItem.updateModel... modeldesc = {} ".format(modeldesc))
        
        self._model_item.update(modeldesc, needEmitDataChanged)

    def boundingRect(self):
        r = self._radius
        return QRectF(-r, -r, 2 * r, 2 * r)

    def drawText(self, painter, labelQRect, labelRectQColor, labelText):
        # draw labels with vertically center aligned
        br = self.boundingRect
        painter.setPen(Qt.black)
        font = QFont('Decorative', weight=QFont.Bold)
        pixel_size = max(1, br.height()*0.6)
        font.setPixelSize(pixel_size)
        painter.setFont(font)
        painter.drawText(br, labelText)



    def paint(self, painter, option, widget=None):
        BaseItem.paint(self, painter, option, widget)

        if self._needDrawDisplayText and self._drawDisplayText:
            self.drawText(painter, self.labelRect(), QColor(self._model_item.getColor()), self._model_item.getLabelText())

        pen = self.pen()
        if self.isSelected():
            pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        
        if self._needFill:
            painter.setBrush(self._displayQColor)

        painter.drawEllipse(self.boundingRect())
        
    def dataChange(self):
        point = self.dataToPoint(self._model_item)
        self.updatePoint(point)


    def keyPressEvent(self, event):
        BaseItem.keyPressEvent(self, event)
        step = 1
        if event.modifiers() & Qt.ShiftModifier:
            step = 5
        ds = {Qt.Key_Left:  (-step, 0),
              Qt.Key_Right: (step, 0),
              Qt.Key_Up:    (0, -step),
              Qt.Key_Down:  (0, step)
             }.get(event.key(), None)
        if ds is not None:
            self.moveBy(*ds)
            self.updateModel()
            event.accept()
            
            
class RectItem(BaseItem):

    def initAttrStickers(self):
        self._attr_stickers = {}  #dict. format: { attribute_name : {displayorder : { 'displaycolor': '#ffffff', 'tag' : tagname, 'displaytext" : displaytext }, ... }, ... } 
        self.initColorAttrStickers()
        self.initExclusiveAttrsStickers()
 
 
    def initColorAttrStickers(self):
        # print "{}, self._model_item = {}".format(self._idName, GET_ANNOTATION(self._model_item))
        rgbValueListOfList, rgbTagListOfList, attrNameOfList = self._model_item.parseColorAttrs(useMyLabelName = False)
        # print "{}, rgbValueListOfList = {} rgbTagListOfList = {} attrNameOfList = {}".format(self._idName, rgbValueListOfList, rgbTagListOfList, attrNameOfList)

        if rgbValueListOfList:
            for j in xrange(len(rgbValueListOfList)):
                displayOrder = 0
                _stickers = {}
                attrName = attrNameOfList[j]
                rgbValueList = rgbValueListOfList[j]
                rgbTagList = rgbTagListOfList[j]
                
                for i in xrange(len(rgbValueList)):
                    if rgbValueList[i] is not None:
                        if ( rgbTagList[i] == config.TAG_UNSET_TOKEN):
                            continue
                        elem = {}
                        elem[config.METADATA_DISPLAYCOLOR_TOKEN] = rgbValueList[i]
                        elem[config.METADATA_ATTR_VALUE_TOKEN]   = rgbTagList[i]
                        elem[config.METADATA_DISPLAYTEXT_TOKEN]  = rgbTagList[i]
                        _stickers[displayOrder] = elem
                        displayOrder += 1
                self._attr_stickers[attrName] = _stickers
                 
        # print ("{}, self._attr_stickers = {}".format(self._idName, self._attr_stickers))
        # print "{}, self._model_item = {}".format(self._idName, GET_ANNOTATION(self._model_item))
        return


    def initExclusiveAttrsStickers(self):
        labelClass = self._model_item.get_label_class()

        attrsTupleOfTuple = config.OBJ_TO_CHILDOBJ_AND_ATTR_DICT.get(labelClass, None)
        LOG.info("initExclusiveAttrsStickers... RectItem {} thisItemLabelClass = {} attrs = {}".format(self._idName,
                                                                                                       labelClass,
                                                                                                       attrsTupleOfTuple))

        if attrsTupleOfTuple is None: return
        for attrTuple in attrsTupleOfTuple:
            if (attrTuple is not None) and (attrTuple[1] == 0) and (attrTuple[0] not in config.COLOR_ATTRS_TUPLE):   # 0 means attribute
                attrName = attrTuple[0]
                attrOption = self._model_item.get(attrName, None)
                # LOG.info(u"initExclusiveAttrsStickers .. thisItemLabelClass = {} attrName = {}  attrOption = {} config.getLabelText(attrOption) {} {}".format(
                #   labelClass, attrName, attrOption, config.getLabelText(attrOption) , config.getLabelColor(attrOption) ))
                if attrOption is None:
                    continue
                elem = {}
                _stickers = {}
                elem[config.METADATA_ATTR_VALUE_TOKEN]  = attrOption
                elem[config.METADATA_DISPLAYTEXT_TOKEN] = config.getLabelText(attrOption)
                elem[config.METADATA_DISPLAYCOLOR_TOKEN]= config.getLabelColor(attrOption)
                
                tmpannomode = config.getSpecificLabelInfo(attrName, "annotatemode")
                order = -1 if tmpannomode == config.ANNOTATION_BBOX_ANNOMODE_TOKEN else 0
                _stickers[order] = elem 
                
                self._attr_stickers[attrName] = _stickers
                LOG.debug ("initExclusiveAttrsStickers... RectItem {} self._attr_stickers[ {} ] = {}".format(self._idName, attrName, _stickers))



    def __init__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        BaseItem.__init__(self, idName, signalObj, model_item, sceneRect, prefix, parent)

        labelName = model_item.get_label_class()
        # LOG.info(u"CREATE RectItem with model_item {} prefix {} parent {}".format(model_item, prefix, parent))
        # LOG.info(u"CREATE RectItem model_item.get_label_class={} get_label_displaytext ={}".format(labelName, model_item.get_label_displaytext()))
        # LOG.info(u"self._model_item.getLabelText={}".format(self._model_item.getLabelText()))
        self._rect = None
        self._resize = False
        self._resize_start = None
        self._resize_start_rect = None
        self._upper_half_clicked = None
        self._left_half_clicked = None
        self._isSelectedValidate = False
        self.initAttrStickers()
        
        self._last_attr_stickers_dict = {}
        self._updateRect(self._dataToRect(self._model_item))

        anno = self._model_item.getAnnotations(recursive = False)  # zx mod @ 20161202. it is unnecessary to get all children's annotations here
        LOG.debug("RectItem._model_item.getAnnotations() = {}".format(anno))
        
        self._needFillRect = anno.get(config.METADATA_FILL_TOKEN, None)
        if self._needFillRect is None:
            self._needFillRect = config.getSpecificLabelInfo(labelName, config.METADATA_FILL_TOKEN)
        self._needFillRect = self._needFillRect if self._needFillRect is not None else False

        # if this item is a item new created, thus annotatemode doesn't occur in anno
        
        # -------------------------------------------------------------
        # determine Rect's draw text
        # -------------------------------------------------------------
        # print "RectItem {} init 1... annomode = {} anno {}....".format(idName, self._attrAnnoMode, GET_ANNOTATION(model_item))
        
        self.calcObjDrawDisplayText(labelName, anno)
        self.calcAttrOverideDrawDisplayText(labelName, anno)

        # print "RectItem {} init 2... annomode = {} anno {}....".format(idName, self._attrAnnoMode, GET_ANNOTATION(model_item))
        # -------------------------------------------------------------
        # determine Rect's display color
        # -------------------------------------------------------------
        self.calcObjDisplayColor(labelName, anno)
        # print "RectItem {} init 3... annomode = {} anno {}....".format(idName, self._attrAnnoMode, GET_ANNOTATION(model_item))

        
        self.calcAttrOverideDisplayColor(labelName, anno)
        # print "RectItem {} init 4... annomode = {} anno {}....".format(idName, self._attrAnnoMode, GET_ANNOTATION(model_item))
        self.setColor(self._displayQColor)
        
        # print u"RectItem {} init 5... needDrawDisplayText {} attrAnnoMode {} drawDisplayText {} displayQColor {}".format(
        #        idName, self._needDrawDisplayText, self._attrAnnoMode, self._drawDisplayText, self._displayQColor)
        
        # LOG.debug("RectItem init: rect {} model_item {} _needFillRect {} _drawDisplayText {} _displayQColor {} ".format(self._rect, model_item, self._needFillRect, self._drawDisplayText, self._displayQColor))
        return
 
 
        
    def addAttrStickers(self, attrClassName, checkedWidgetsOptionList, clearFirst = True ):
        # LOG.info("RectItem.addAttrStickers({}, {}, {})... _last_attr_stickers_dict = {} ...".format(attrClassName, checkedWidgetsOptionList, clearFirst, self._last_attr_stickers_dict))

        commonColor = [] #[ [config.METADATA_DISPLAYCOLOR_TOKEN, displayOrder], ... ]
        needEmitDataChanged = True
        for attr_name, attr in checkedWidgetsOptionList.items():
        
            if clearFirst:
                self._attr_stickers[attr_name] = {}   # dict

            for desc in attr:
                if attr_name not in self._last_attr_stickers_dict:
                    continue

                displayColor = desc.get(config.COLOR_ATTR_RGB_VALUE_TOKEN, None)
                if displayColor is None:
                    displayColor = desc.get(config.METADATA_DISPLAYCOLOR_TOKEN, None)
                if displayColor is None:
                    continue   

                for _displayColor, _displayOrder in self._last_attr_stickers_dict[attr_name].iteritems():
                    if displayColor == _displayColor:
                        commonColor.append([displayColor, _displayOrder])
             
            self._last_attr_stickers_dict[attr_name] = {} # dict

               
            # sort 'commonColor' list by displayOrder field of each element in this list in asc order
            commonColor.sort(key=lambda obj: obj[1], reverse=False)
            # LOG.info("sort: commonColor = {}".format(commonColor))
            # update displayOrder for commonColor list
            idx = 0
            for k, i in enumerate(commonColor):
                i[1] = idx
                idx += 1

            # LOG.info("update: commonColor = {}".format(commonColor))
        
            if clearFirst:
                self._last_attr_stickers_dict = {} # dict

            _stickers = {}
            
            # print u"zxzx ... {} addAttrStickers self._attrAnnoMode = {}".format(self._idName, self._attrAnnoMode) 
            for desc in attr:
                displayColor = desc.get(config.COLOR_ATTR_RGB_VALUE_TOKEN, None)
                if displayColor is None:
                    displayColor = desc.get(config.METADATA_DISPLAYCOLOR_TOKEN, None)
                if displayColor is None:
                    LOG.info("desc get color {} failed".format(desc, config.METADATA_DISPLAYCOLOR_TOKEN))
                    continue   
                
                attrName = desc.get(config.METADATA_ATTR_VALUE_TOKEN, None)
                if attrName is None:
                    attrName = desc.get(config.METADATA_ATTR_VALUE_TOKEN, None)
                if attrName is None:
                    continue 
                    
                displayText = desc.get(config.METADATA_DISPLAYTEXT_TOKEN, None)
                if displayText is None:
                    displayText = attrName

                labelInfo = config._class_configInfo.get(attrClassName, None)

                tmpannomode = config.getSpecificLabelInfo(attrClassName, "annotatemode")
                self._attrAnnoMode = tmpannomode
                
                # if self._attrAnnoMode == config.ANNOTATION_ATTR_ANNOMODE_TOKEN:
                if True:
                    displayOrder = -1
                    for k, i in enumerate(commonColor):
                        if i[0] == displayColor:
                            displayOrder = i[1]
                    
                    if displayOrder < 0:
                        displayOrder = idx
                        idx += 1
                if self._attrAnnoMode == config.ANNOTATION_BBOX_ANNOMODE_TOKEN:
                # else:
                    # Note that, I use displayOrder == -1 to denote this attribute should be annotated with overloaded mode(i.e.: control the object's bbox color)
                    displayOrder = 0 # -1 
                    self._displayQColor   = utils.colorStrToQtColor(displayColor) if displayColor else Qt.yellow  # re-set this item's display color
                    self._drawDisplayText = displayText if displayText != config.TAG_UNSET_DISPLAYTEXT else None  # re-set this item's display text
                    # print u"addAttrStickers: _drawDisplayText = {}".format(self._drawDisplayText)
                    
                elem = {}
                elem[config.METADATA_DISPLAYCOLOR_TOKEN]= displayColor
                elem[config.METADATA_ATTR_VALUE_TOKEN]  = attrName
                elem[config.METADATA_DISPLAYTEXT_TOKEN] = displayText

                _stickers[displayOrder] = elem
                if attr_name not in self._last_attr_stickers_dict.keys():
                    self._last_attr_stickers_dict[attr_name] = {}
                self._last_attr_stickers_dict[attr_name][displayColor] = displayOrder  # dict. dict.key = RGB str; dict.val = displayOrder

            if (not attr) and (attr is not None): 
                anno = self._model_item.getAnnotations(recursive = False) 
                # self.calcObjDrawDisplayText(self._idName, anno)
                self._drawDisplayText = None
                self.calcObjDisplayColor(self._idName, anno)
                print "addattrsticker: setColor {}".format(self._displayQColor)
                self.setColor(self._displayQColor)
                
            self._attr_stickers[attr_name] = _stickers


        # print ("RectItem {}.addAttrStickers ...self._attr_stickers {} ...".format(self._idName, self._attr_stickers))
        # print "before update: displayQColor = {} {} {}".format(self.pen().color().red(), self.pen().color().green(), self.pen().color().blue() )
 
        self.updateModel(needEmitDataChanged) # update model
        # print "before exit: displayQColor = {} {} {}".format(self.pen().color().red(), self.pen().color().green(), self.pen().color().blue() )

        self.update()      # this function will trigger paint()
        # print "exit: displayQColor = {} {} {}".format(self.pen().color().red(), self.pen().color().green(), self.pen().color().blue() )
  
        return
  
    
    def __call__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        item = RectItem(idName, signalObj, model_item, sceneRect, prefix, parent)
        item.setPen(self.pen())
        item.setBrush(self.brush())
        # print "call: displayQColor = {} {} {}".format(self.pen().color().red(), self.pen().color().green(), self.pen().color().blue() )

        return item

    def _dataToRect(self, model_item):
        if model_item is None:
            return QRectF()

        try:
            rect = getQRectFFromModelItem(model_item, self.prefix())
            # print "rect = {} translate = {}".format(rect.topLeft(), QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft())
            return rect.translated(-QPointF(0, 0) if self._sceneRect is None else -self._sceneRect.topLeft())
        except KeyError as e:
            LOG.debug("RectItem: Could not find expected key in item: "
                      + str(e) + ". Check your config!")
            self.setValid(False)
            return QRectF()

    def _updateRect(self, rect):
        if rect == self._rect:
            return

        self.prepareGeometryChange()
        self._rect = rect
        self.setPos(rect.topLeft())
        

    # ========================================================================================== 
    # zx comment: Here is the key function which really determine this annotation's content in json file
    # it will update annotationScene's modelItem
    # ========================================================================================== 
    def updateModel(self, needEmitDataChanged = True):
        
        self._rect = QRectF(self.scenePos(), self._rect.size())
        # LOG.info("RectItem.updateModel... self._rect = {} self._model_item.getAnnotations = {} ".format(self._rect, self._model_item.getAnnotations()))
        
        modeldesc = convertQRectFToModelItemKeyValues(QRectF(self.scenePos() + (QPointF(0, 0) if self._sceneRect is None else self._sceneRect.topLeft()), self._rect.size()), self.prefix())
           
        # print ("RectItem {} updateModel 1...  _attr_stickers = {} model_item = {}".format(self._idName, self._attr_stickers, GET_ANNOTATION(self._model_item)))
             
        if self._attr_stickers is not None:
            RGBdesc = {}
            for type, dictval in self._attr_stickers.items():
            
                allowedColorNum = config.MAX_UPPER_COLOR_NUMBER if type == config.ANNOTATION_UPPER_COLOR_TOKEN else config.MAX_LOWER_COLOR_NUMBER if type == config.ANNOTATION_LOWER_COLOR_TOKEN else \
                      config.MAX_VEHICLE_COLOR_NUMBER if type == config.ANNOTATION_VEHICLE_COLOR_TOKEN else config.MAX_CHECKED_OPTIONS_NUMBER if type == config.ANNOTATION_HELMET_COLOR_TOKEN else 0
                # print "==== type = {} allowedColorNum = {}".format(type, allowedColorNum)
                if (allowedColorNum > 1) or (type in [config.ANNOTATION_UPPER_COLOR_TOKEN, config.ANNOTATION_LOWER_COLOR_TOKEN, config.ANNOTATION_VEHICLE_COLOR_TOKEN]):
                    for k in xrange(allowedColorNum):
                        self._model_item.__delitem__(self.prefix() + type + str(k))
                        self._model_item.__delitem__(self.prefix() + type + str(k) + 'Tag')
                elif (allowedColorNum == 1):
                    self._model_item.__delitem__(self.prefix() + type)
                    self._model_item.__delitem__(self.prefix() + type + 'Tag')    
                # else:
                #    raise RuntimeError("There are more than {} colors for {}! This is not supported currently!".format(allowedColorNum, type) )
                   
                # print ("RectItem {} updateModel 2 for {} ...  _attr_stickers = {} model_item = {}".format(self._idName, type, self._attr_stickers, GET_ANNOTATION(self._model_item)))
                
                # LOG.info("_attr_stickers type {} dictval {}".format(type, dictval))
                
                for displayOrder, val in dictval.items():
                    attrValTxt = val.get(config.METADATA_ATTR_VALUE_TOKEN, None)
                    addtionalAttrValTxt = val.get(config.METADATA_DISPLAYCOLOR_TOKEN, None)
                    modelkey = type
                        
                    # LOG.info("RectItem.updateModel...  type {} displayOrder {} attrValTxt {} addtionalAttrValTxt {}".format(type, displayOrder, attrValTxt, addtionalAttrValTxt))
                    
                    if (allowedColorNum > 1) or (type in config.NON_EXCLUSIVE_ATTRS_TAG_LIST):
                
                        RGBdesc.update({self.prefix() + modelkey + str(displayOrder)         : addtionalAttrValTxt})
                        RGBdesc.update({self.prefix() + modelkey + str(displayOrder) + "Tag" : attrValTxt})
                        # LOG.info("self.prefix()= {} modelkey = {} str(displayOrder) = {}".format(self.prefix(), modelkey, str(displayOrder)))

                    else:
                        if (allowedColorNum == 1):
                            RGBdesc.update({self.prefix() + modelkey         : addtionalAttrValTxt})
                            RGBdesc.update({self.prefix() + modelkey + "Tag" : attrValTxt})  
                        else:
                            RGBdesc.update({self.prefix() + modelkey         : attrValTxt})
                        LOG.info("self.prefix() + modelkey  = {} ".format(self.prefix() + modelkey))
                        # since other attributes can have only at most one value, thus just pick up the first value
                        if len(dictval) > 1:
                            raise RuntimeError("Error: Attr '{}' have more than one options : {}".format(attrValTxt, dictval))
                        break
                       	
                if len(RGBdesc) > 0:
                	modeldesc.update(RGBdesc)
                	
                
                # LOG.info("RGBdesc = {}".format(RGBdesc))
                    
        # LOG.info("RectItem.updateModel... modeldesc = {} ".format(modeldesc))
        self._model_item.update(modeldesc, needEmitDataChanged)
        return
        
    def boundingRect(self):
        return QRectF(QPointF(0, 0), self._rect.size())

    def labelRect(self):
        labelRectPos = config.OBJ_LABEL_RECT_POS_DICT.get(self._idName, None)
        labelRectPos = labelRectPos if labelRectPos else (0, 0.5, 1, 0.1)
        return QRectF(QPointF(labelRectPos[0], self._rect.size().height()*labelRectPos[1]), QSizeF(self._rect.size().width()*labelRectPos[2],self._rect.size().height()*labelRectPos[3])) 
        # return QRectF(QPointF(0, self._rect.size().height()*0.5), QSizeF(self._rect.size().width(),self._rect.size().height()*0.1))

    def drawText(self, painter, labelQRect, _labelRectQColor, labelText):
      
        # draw labels with vertically center aligned
        if not labelText:
            return
        labelRectQColor = copy.deepcopy(_labelRectQColor)
        if (self._drawDisplayText == config.TAG_UNSET_DISPLAYTEXT):
            return
        labelRectQColor.setAlpha(config.DEFAULT_LABELTEXT_BKGCOLOR_ALPHA)
        # print "labelRectQColor = {} {} {}".format(labelRectQColor.red(), labelRectQColor.green(), labelRectQColor.blue())
        painter.fillRect(labelQRect, labelRectQColor)
        painter.setPen(Qt.black)
        font = QFont('Decorative', weight=QFont.Bold)
        pixel_size = max(1, labelQRect.height()*0.6)
        font.setPixelSize(pixel_size)
        painter.setFont(font) 
        # print u"RectItem {} drawText {} @ {}...".format(self._idName, labelText, labelQRect)
        painter.drawText(labelQRect, Qt.AlignCenter, labelText)

    def calcDisplayPos(self, rectW, rectH, displayRatioX, displayRatioY, displayAttrIdName):
        x, y = int(rectW*displayRatioX), int(rectH*displayRatioY)
        b = min(x, y)
        x = x if b == x else (int)((float)(b) * displayRatioX / displayRatioY)
        y = y if b == y else (int)((float)(b) * displayRatioY / displayRatioX)
        displayWidth  = min(x, 256)
        displayHeight = min(y, 256)
        displayStartPos = config.ATTRIBUTE_STICKER_DEFAULT_DISPLAY_POS_INFO_IN_OBJ.get(displayAttrIdName, (0, 0, 0, 1))
        displayStartPosX = displayStartPos[0]
        displayStartPosY = displayStartPos[1]
        elayout          = displayStartPos[2]
        ilayout          = displayStartPos[3]
        # print "{}: pos {} {} {} {}".format(displayAttrIdName, displayStartPosX, displayStartPosY, elayout, ilayout)

        if (displayStartPosX < 0):
            stepX = -displayWidth if elayout == 1 else 0
        else:
            stepX = displayWidth  if elayout == 1 else 0                
        displayStartPosX = ROUND_VALUE(displayStartPosX * displayWidth, 0, rectW)
        
        if (displayStartPosY < 0):
            stepY = -displayHeight if elayout == 0 else 0
        else:
            stepY = displayHeight  if elayout == 0 else 0
        displayStartPosY = ROUND_VALUE(displayStartPosY * displayHeight, 0, rectH)
        # print "{}: pos {} {} {} {}".format(displayAttrIdName, displayStartPosX, displayStartPosY, elayout, ilayout)
        return displayStartPosX, displayStartPosY, displayWidth, displayHeight, stepX, stepY, elayout, ilayout

	"""
    def updateSpeicialAttrDisplayPos(self, rectW, rectH, displayWidth, displayHeight, displayAttrIdName):
        _stepY = None
        _stepX = None
        specialPosInfoDict = config.SPECIFIC_ATTR_STICKER_DISPLAY_POS_INFO_IN_OBJ.get(self._idName, None)
        specialPosInfo = specialPosInfoDict.get(type, None) if specialPosInfoDict else None
        if specialPosInfo:
            _PosX   = specialPosInfo[0]
            _PosY   = specialPosInfo[1]
            _layout = specialPosInfo[2]
            if (_PosX < 0):
                _stepX = -displayWidth if _layout == 1 else 0
            else:
                _stepX = displayWidth  if _layout == 1 else 0                
            _PosX = ROUND_VALUE(_PosX * displayWidth, 0, rectW)
            
            if (_PosY < 0):
                _stepY = -displayHeight if _layout == 0 else 0
            else:
                _stepY = displayHeight  if _layout == 0 else 0
            _PosY = ROUND_VALUE(_PosY * displayHeight, 0, rectH)
            return _PosX, _PosY, _stepX, _stepY, _layout
        
        return None, None, None, None, None
    """      
    
    def paintAttrStickers(self, painter):
        rw = self._rect.size().width() 
        rh = self._rect.size().height()
        if (rw <= 0) or (rh <= 0):
            return

        attr_stickers = [(key, config.ATTRIBUTE_STICKER_DISPLAY_ORDER.get(key, -2), val) for key, val in self._attr_stickers.items() ]
        attr_stickers = sorted(attr_stickers, key=lambda d: d[1], reverse=0)

        displayPosX, displayPosY = 0, 0
        first = True
        # print "\n"
        for item in attr_stickers:
            type = item[0]
            order = item[1]
            dictval = item[2]
            if type == config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN:
                continue

            if not dictval:
                continue
			    
            if type not in config.COLOR_ATTRS_TUPLE:
                displayStartPosX, displayStartPosY, displayWidth, displayHeight, stepX, stepY, elayout, ilayout = self.calcDisplayPos(rw, rh, 0.25, 0.25, type)
            else:
                displayStartPosX, displayStartPosY, displayWidth, displayHeight, stepX, stepY, elayout, ilayout = self.calcDisplayPos(rw, rh, 0.25, 0.25, type)
            if first:
                displayPosX = displayStartPosX
                displayPosY = displayStartPosY
                first = False
            # print "{}: posx {} posy {} elayout {} ilayout {}".format(type, displayPosX, displayPosY, elayout, ilayout)

            x = displayPosX if elayout == 1 else displayStartPosX
            y = displayPosY if elayout == 0 else displayStartPosY
            # print "{}: x {} y {} stepx {} stepy {}".format(type, x, y, stepX, stepY)
            w, h = displayWidth, displayHeight
            

            for displayOrder, val in dictval.items():
                # print "{}: displayOrder {}".format(type, displayOrder)
                if ( displayOrder == -1):
                    # print "displayOrder = {} type = {}".format(displayOrder, type)
                    continue

                displayText = val.get(config.METADATA_DISPLAYTEXT_TOKEN, 'Err')
                displayColor = val.get(config.METADATA_DISPLAYCOLOR_TOKEN, None)
                displayQtColor = utils.colorTagToQtColor(displayColor, True) # QColor(displayColor if displayColor is not None else Qt.yellow)
                # print u"displayText = {} displayQtColor = {} {} {}".format(displayText, displayQtColor.red(), displayQtColor.green(), displayQtColor.blue())

                if type in config.COLOR_ATTRS_TUPLE:
                    sticker_rect = QRectF(QPointF(x, y), QSizeF(w, h))
                    painter.fillRect(sticker_rect, displayQtColor)
                else:
                    if (displayText == config.TAG_UNSET_DISPLAYTEXT):
                        continue
                    text_rect = QRectF(QPointF(x, y), QSizeF(w, h))
                    self.drawText(painter, text_rect, displayQtColor, displayText)

                l = ilayout 
                
                x = x + (0 if l == 0 else w)
                y = y + (h if l == 0 else 0)
                    
               
            displayPosX += stepX # stepX
            displayPosX  = ROUND_VALUE(displayPosX, 0, rw)
            displayPosY += h     # stepY
            displayPosY  = ROUND_VALUE(displayPosY, 0, rh)

        return
    
                 
    def paint(self, painter, option, widget = None):
        boundingRect = self.boundingRect()
        if (boundingRect.width() < 0 or boundingRect.height() < 0):
            return
            
        BaseItem.paint(self, painter, option, widget)

        # ------------------------------------       
        # begin to draw stickers
        # ------------------------------------     
        # print u"needDrawDisplayText {} self._drawDisplayText {}".format(self._needDrawDisplayText, self._drawDisplayText)
        if self._needDrawDisplayText and self._drawDisplayText:
            self.drawText(painter, self.labelRect(), self._displayQColor, self._drawDisplayText)

       
        # ------------------------------------       
        # begin to draw bbox
        # ------------------------------------     
        pen = self.pen()
        if self.isSelected():
            pen.setStyle(Qt.DashLine)
        painter.setPen(pen)

        if self._needFillRect:
            painter.fillRect(boundingRect, self._displayQColor)
        
        painter.drawRect(boundingRect)
            
        
        # ------------------------------------       
        # begin to draw stickers
        # ------------------------------------     
        if self._attr_stickers is None: return
        self.paintAttrStickers(painter)

        return
                
                        
    def dataChange(self):
        rect = self._dataToRect(self._model_item)
        self._updateRect(rect)

    def validateIsSelected(self, event):
         # hl = min(max(self._rect.height()/8, 16), self._rect.height()/4)
         # wl = min(max(self._rect.width() /8, 16), self._rect.width() /4)
         hl = self._rect.height()/2 - 1
         wl = self._rect.width() /2 - 1
         
         if ( abs(event.scenePos().y() - self._rect.y()) <= hl and
              abs(event.scenePos().x() - self._rect.x()) <= wl ):
             return True

         if ( abs(event.scenePos().y() - self._rect.y() - self._rect.height()) < hl and
              abs(event.scenePos().x() - self._rect.x() - self._rect.width() ) < wl ):
             return True

         if ( abs(event.scenePos().y() - self._rect.y() - self._rect.height()) <  hl and
              abs(event.scenePos().x() - self._rect.x())                       <= wl ):
             return True                                                           
                                                                                   
         if ( abs(event.scenePos().y() - self._rect.y())                       <= hl and
              abs(event.scenePos().x() - self._rect.x() - self._rect.width() ) <  wl ):
             return True
             
         return False
                                 
    def mousePressEvent(self, event):
        self._isSelectedValidate = False
        if not self.validateIsSelected(event): return
        self._isSelectedValidate = True
        # print "Item {}: got mouse press event! event {} Pos {} RightClick {} isSelected {}".format(
        # self._idName, event, event.scenePos(), "Yes" if event.button() & Qt.RightButton else "No", self.isSelected())
        #if event.modifiers() & Qt.ControlModifier != 0:
        if event.button() & Qt.RightButton != 0:
           
            self._resize = True
            self._resize_start = event.scenePos()
            self._resize_start_rect = QRectF(self._rect)
            self._upper_half_clicked = (event.scenePos().y() < self._resize_start_rect.center().y())
            self._left_half_clicked  = (event.scenePos().x() < self._resize_start_rect.center().x())
            event.accept()
        else:
            self._resize_start = event.scenePos()
            self._resize_start_rect = QRectF(self._rect)
            BaseItem.mousePressEvent(self, event)
            event.accept()
            
    def validateRect(self, x, y, w, h):
        rect = QRectF(x, y, w, h)
        if self._QRectBoundary is not None:
            rect = rect.intersected(self._QRectBoundary)

        rect.translated(self._sceneRect.topLeft() if self._sceneRect else QPointF(0, 0))      
        imgrect = QRectF(0, 0, self._imgsz[0], self._imgsz[1])
        rect = rect.intersected(imgrect)
        
        # rect = rect.translated(-QPointF(0, 0) if self._sceneRect is None else -self._sceneRect.topLeft())
        return rect
        
         
    def mouseMoveEvent(self, event):
        if not self._isSelectedValidate: return
        if ( config.ENABLE_TOP_OBJECT_MODE and (self._idName == config.DEFAULT_TOP_OBJECT)): return
        
        # print "Item {}: got mouse move event! Resize {}".format(self._idName, "Yes" if self._resize else "No")

        if self._resize:
            diff = event.scenePos() - self._resize_start
            if self._left_half_clicked:
                x = self._resize_start_rect.x() + diff.x()
                w = self._resize_start_rect.width() - diff.x()
            else:
                x = self._resize_start_rect.x()
                w = self._resize_start_rect.width() + diff.x()

            if self._upper_half_clicked:
                y = self._resize_start_rect.y() + diff.y()
                h = self._resize_start_rect.height() - diff.y()
            else:
                y = self._resize_start_rect.y()
                h = self._resize_start_rect.height() + diff.y()

            # img_sz =  self._imgsz

            rect = self.validateRect(x, y, w, h)

            self._updateRect(rect)
            self.updateModel()
            event.accept()
        else:
            # BaseItem.mouseMoveEvent(self, event)
            diff = event.scenePos() - self._resize_start

            x = self._resize_start_rect.x() + diff.x()
            w = self._resize_start_rect.width()
            y = self._resize_start_rect.y() + diff.y()
            h = self._resize_start_rect.height()
                            
            rect = self.validateRect(x, y, w, h)

            self._updateRect(rect)
            self.updateModel()
            event.accept()

        return

    def mouseReleaseEvent(self, event):
        if not self._isSelectedValidate: return
        self._isSelectedValidate = False
        
        if self._signalObj:
            if (self._rect.width() < config.GUI_RECT_MIN_WIDTH) or (self._rect.height() < config.GUI_RECT_MIN_HEIGHT):
                self._signalObj.emit(self.parentItem(), self)
        
        if self._resize:
            self._resize = False
            event.accept()
        else:
            BaseItem.mouseReleaseEvent(self, event)
            event.accept()

    def keyPressEvent(self, event):
        BaseItem.keyPressEvent(self, event)
        step = 1
        if event.modifiers() & Qt.ShiftModifier:
            step = 5
        ds = {Qt.Key_Left:  (-step, 0),
              Qt.Key_Right: (step, 0),
              Qt.Key_Up:    (0, -step),
              Qt.Key_Down:  (0, step),
             }.get(event.key(), None)
        if ds is not None:
            if event.modifiers() & Qt.ControlModifier:
                rect = self._rect.adjusted(*((0, 0) + ds))
            else:
                rect = self._rect.adjusted(*(ds + ds))
            self._updateRect(rect)
            self.updateModel()
            event.accept()


class MultiPointItem(BaseItem):
    def __init__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="pointlist", parent=None):
        BaseItem.__init__(self, idName, signalObj, model_item, sceneRect, prefix, parent)

        # make it non-movable for now
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges |
                      QGraphicsItem.ItemSendsScenePositionChanges)
        self._points = None

        self._updatePoints(self._dataToPoints(self._model_item))
        # LOG.debug("Constructed points %s for model item %s" % self._points, model_item))

    def __call__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        item = MultiPointItem(idName, signalObj, model_item, sceneRect, prefix, parent)
        item.setPen(self.pen())
        item.setBrush(self.brush())
        return item

    def _dataToPoints(self, model_item):
        if model_item is None:
            return []

        try:
            return model_item[self.prefix()]
        except KeyError as e:
            LOG.debug("MultiPointItem: Could not find expected key in item: "
                      + str(e) + ". Check your config!")
            self.setValid(False)
            return QRectF()

    def _updatePoints(self, points):
        if points == self._points:
            return

        self.prepareGeometryChange()
        self._points = points
        self.setPos(QPointF(0, 0))

    def boundingRect(self):
        xmin = min(self._points[::2])
        xmax = max(self._points[::2])
        ymin = min(self._points[1::2])
        ymax = max(self._points[1::2])
        return QRectF(xmin, ymin, xmax - xmin, ymax - ymin)

    def paint(self, painter, option, widget=None):
        BaseItem.paint(self, painter, option, widget)

        pen = self.pen()
        if self.isSelected():
            pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        for k in range(len(self._points)/2):
            x, y = self._points[2*k:2*k+2]
            painter.drawEllipse(QRectF(x-1, y-1, 2, 2))

    def dataChange(self):
        points = self._dataToPoints(self._model_item)
        self._updateRect(points)


class GroupItem(BaseItem):
    items = []

    def __init__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        self._children = []
        BaseItem.__init__(self, idName, signalObj, model_item, sceneRect, prefix, parent)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)

        self.createChildren()

    def createChildren(self):
        for callable_, prefix in self.items:
            child = callable_(self._idName, self._signalObj, self._model_item, self._sceneRect, prefix, self)
            self._children.append(child)

    def setColor(self, *args, **kwargs):
        for c in self._children:
            c.setColor(*args, **kwargs)
        BaseItem.setColor(self, *args, **kwargs)

    def boundingRect(self):
        br = QRectF()
        for item in self.childItems():
            if item is self._text_item:
                continue
            br |= item.mapRectToParent(item.boundingRect())
        return br


class OccludablePointItem(PointItem):
    hotkeys = {
        'o': cycleValue('occluded', [True, False])
    }

    def __init__(self, *args, **kwargs):
        PointItem.__init__(self, *args, **kwargs)
        self.updateColor()

    def dataChange(self):
        PointItem.dataChange(self)
        self.updateColor()

    # def updateColor(self):
    #     key = self.prefix() + 'occluded'
    #     if key in self.get_annotation():
    #         occluded = self._model_item[key]
    #         self.setColor(Qt.red if occluded else Qt.yellow)
     
    def updateColor(self):
        if self._model_item is not None:
            c = self._model_item.getColor()
            
            key = self.prefix() + 'occluded'
            occluded = False
            if key in self.get_annotation():
                occluded = self._model_item[key]
            
            color = Qt.yellow if c is None else c
            self.setColor(Qt.red if occluded else color)


class IDRectItem(RectItem):
    hotkeys = dict(
        [('i',    cycleValue(IgnorePrefix('id'), range(36)))] +
        [(str(i), cycleValue(IgnorePrefix('id'), [i])) for i in range(10)] +
        [(chr(i-10+65).lower(), cycleValue(IgnorePrefix('id'), [i])) for i in range(10, 36)]
    )
    defaultAutoTextKeys = ['id']


class BBoxFaceItem(GroupItem):
    items = [
        (IDRectItem,          config.ANNOTATION_LABELLING_BBOX_TOKEN),
        (OccludablePointItem, config.ANNOTATION_LEFT_EYE_CENTER_TOKEN),
        (OccludablePointItem, config.ANNOTATION_RIGHT_EYE_CENTER_TOKEN),
        (OccludablePointItem, config.ANNOTATION_MOUTH_CENTER_TOKEN),
    ]


class ControlItem(QGraphicsItem):
    def __init__(self, parent=None):
        QGraphicsItem.__init__(self, parent)

        # always have the same size
        self.setFlags(QGraphicsItem.ItemIgnoresTransformations)

    def paint(self, painter, option, widget=None):
        color = QColor('black')
        color.setAlpha(200)
        painter.fillRect(self.boundingRect(), color)


class NPointFacePointItem(QGraphicsEllipseItem):
    def __init__(self, landmark, *args, **kwargs):
        self._landmark = landmark
        QGraphicsEllipseItem.__init__(self, *args, **kwargs)
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemSendsGeometryChanges |
                      QGraphicsItem.ItemSendsScenePositionChanges)

    def landmark(self):
        return self._landmark

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            parent = self.parentItem()
            if parent is not None:
                parent.landmarkChanged(self, value)
        return QAbstractGraphicsShapeItem.itemChange(self, change, value)

    def setColor(self, color):
        self.setPen(color)
        self.setBrush(color)
        self.update()

class NPointFaceItem(GroupItem):
    items = [
        # Eyebrows
        (OccludablePointItem, "lboc"),   # left eyebrow outer center
        (OccludablePointItem, "lbu75"),  # left eyebrow upper contour 75%
        (OccludablePointItem, "lbu50"),  # left eyebrow upper contour 50%
        (OccludablePointItem, "lbu25"),  # left eyebrow upper contour 25%
        (OccludablePointItem, "lbic"),   # left eyebrow inner center

        (OccludablePointItem, "rbic"),   # right eyebrow inner center
        (OccludablePointItem, "rbu25"),  # right eyebrow upper contour 25%
        (OccludablePointItem, "rbu50"),  # right eyebrow upper contour 50%
        (OccludablePointItem, "rbu75"),  # right eyebrow upper contour 75%
        (OccludablePointItem, "rboc"),   # right eyebrow outer center

        # Eyes
        (OccludablePointItem, "leoc"),   # left eye outer center
        (OccludablePointItem, "leu67"),  # left eye upper countour 67%
        (OccludablePointItem, "leu33"),  # left eye upper countour 33%
        (OccludablePointItem, "leic"),   # left eye inner center
        (OccludablePointItem, "lel33"),  # left eye lower countour 33%
        (OccludablePointItem, "lel67"),  # left eye lower countour 67%
 
        (OccludablePointItem, "reic"),   # right eye inner center
        (OccludablePointItem, "reu33"),  # right eye upper countour 33%
        (OccludablePointItem, "reu67"),  # right eye upper countour 67%
        (OccludablePointItem, "reoc"),   # right eye outer center
        (OccludablePointItem, "rel67"),  # right eye lower countour 67%
        (OccludablePointItem, "rel33"),  # right eye lower countour 33%  
 
        (OccludablePointItem, "lec"),    # left eye center
       (OccludablePointItem, "rec"),     # right eye center

        # Nose
        (OccludablePointItem, "nr100"),  # nose ridge 100%
        (OccludablePointItem, "nr67"),   # nose ridge 67%
        (OccludablePointItem, "nr33"),   # nose ridge 33%
        (OccludablePointItem, "nt"),     # nose tip

        (OccludablePointItem, "nl"),     # nose left
        (OccludablePointItem, "nbl50"),  # nose base left 50%
        (OccludablePointItem, "nc"),     # nose center
        (OccludablePointItem, "nbr50"),  # nose base right 50%
        (OccludablePointItem, "nr"),     # nose right

        # Mouth
        (OccludablePointItem, "mollc"),
        (OccludablePointItem, "moltl67"),
        (OccludablePointItem, "moltl33"),
        (OccludablePointItem, "moltc"),
        (OccludablePointItem, "moltr33"),
        (OccludablePointItem, "moltr67"),
        (OccludablePointItem, "molrc"),
        (OccludablePointItem, "molbr67"),
        (OccludablePointItem, "molbr33"),
        (OccludablePointItem, "molbc"),
        (OccludablePointItem, "molbl33"),
        (OccludablePointItem, "molbl67"),
        (OccludablePointItem, "millc"),
        (OccludablePointItem, "miltl50"),
        (OccludablePointItem, "miltc"),
        (OccludablePointItem, "miltr50"),
        (OccludablePointItem, "milrc"),
        (OccludablePointItem, "milbr50"),
        (OccludablePointItem, "milbc"),
        (OccludablePointItem, "milbl50"),

        # Mouth (legacy)
        (OccludablePointItem, "ulc"),  # upper lip center
        (OccludablePointItem, "llc"),  # lower lip center
        (OccludablePointItem, "mc"),   # mouth center
        (OccludablePointItem, "lmc"),  # left mouth corner
        (OccludablePointItem, "rmc"),  # right mouth corner

        # Ears
        (OccludablePointItem, "le"),   # left ear
        (OccludablePointItem, "re"),   # right ear

        # Chin
        (OccludablePointItem, "cc"),   # chin center
    ]

    def __init__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        LOG.info("create NPointFaceItem ... model_item = {} anno = {}".format(model_item, model_item.getAnnotations(recursive = False)))
        GroupItem.__init__(self, idName, signalObj, model_item, sceneRect, prefix, parent)


    def createChildren(self):
        anno = self.get_annotation()
        for callable_, prefix in self.items:
            if prefix + 'x' in anno and prefix + 'y' in anno:
                # LOG.debug("prefix = {}".format(prefix))
                child = callable_(self._idName, self._signalObj, self._model_item, self._sceneRect, prefix, self)
                if hasattr(child, 'setToolTip'):
                    child.setToolTip(prefix)
                self._children.append(child)

    def boundingRect(self):
        qRectF = getQRectFFromModelItem(self._model_item)
        if qRectF is not None:
            return qRectF
        else:
            br = GroupItem.boundingRect(self)
            offset = 0.2 * br.height()
            return br.adjusted(-offset, -offset, +offset, +offset)

    def paint(self, painter, option, widget=None):
        GroupItem.paint(self, painter, option, widget)

        pen = self.pen()
        if self.isSelected():
            pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(self.boundingRect())

class PolygonItem(BaseItem):
    def __init__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        BaseItem.__init__(self, idName, signalObj, model_item, sceneRect, prefix, parent)

        # Make it non-movable for now
        self.setFlags(QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges |
                      QGraphicsItem.ItemSendsScenePositionChanges)
        self._polygon = None

        self._updatePolygon(self._dataToPolygon(self._model_item))

        anno = self._model_item.getAnnotations(recursive=False)
        labelName = model_item.get_label_class()
        self._needFillPolygon = anno.get(config.METADATA_FILL_TOKEN, None)
        if self._needFillPolygon is None:
            self._needFillPolygon = config.getSpecificLabelInfo(labelName, config.METADATA_FILL_TOKEN)
        self._needFillPolygon = self._needFillPolygon if self._needFillPolygon is not None else False
            
        # -------------------------------------------------------------
        # determine Polygon's draw text
        # -------------------------------------------------------------
        self.calcObjDrawDisplayText(labelName, anno)
        self.calcAttrOverideDrawDisplayText(labelName, anno)

        # -------------------------------------------------------------
        # determine Polygon's display color
        # -------------------------------------------------------------
        self.calcObjDisplayColor(labelName, anno)
        self.calcAttrOverideDisplayColor(labelName, anno)

        # LOG.debug (u"PolygonItem init: name {} model_item {} _needFillPolygon {} _drawDisplayText {} _displayQColor {} {} {} ".format(self._idName, model_item, self._needFillPolygon, self._drawDisplayText, self._displayQColor.red(), self._displayQColor.green(), self._displayQColor.blue()))
        # LOG.debug("Constructed polygon %s for model item %s" % (self._polygon, model_item))
        return

    def __call__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        item = PolygonItem(idName, signalObj, model_item, sceneRect, prefix, parent)
        # item.setPen(self.pen())
        # item.setBrush(self.brush())
        self.setColor(self._displayQColor)
        return item

    def _dataToPolygon(self, model_item):
        if model_item is None:
            return QPolygonF()

        try:
            polygon = QPolygonF()
            xn = [float(x) for x in model_item["xn"].split(";")]
            yn = [float(y) for y in model_item["yn"].split(";")]
            for x, y in zip(xn, yn):
                polygon.append(QPointF(x, y))

            # for i in polygon:
            #    LOG.debug( "_dataToPolygon: before transliate ({}, {}) ".format(i.x(), i.y()))

            polygon = polygon.translated(-QPointF(0, 0) if self._sceneRect is None else -self._sceneRect.topLeft())
            # for i in polygon:
            #    LOG.debug( "_dataToPolygon: after transliate ({}, {}) ".format(i.x(), i.y()))

            return polygon

        except KeyError as e:
            LOG.debug("PolygonItem: Could not find expected key in item: "
                      + str(e) + ". Check your config!")
            self.setValid(False)
            return QPolygonF()

    def _updatePolygon(self, polygon):
        if polygon == self._polygon:
            return

        self.prepareGeometryChange()
        self._polygon = polygon
        self.setPos(QPointF(0, 0))

    def boundingRect(self):
        xn = [p.x() for p in self._polygon]
        yn = [p.y() for p in self._polygon]
        xmin = min(xn)
        xmax = max(xn)
        ymin = min(yn)
        ymax = max(yn)
        return QRectF(xmin, ymin, xmax - xmin, ymax - ymin)

    def paint(self, painter, option, widget=None):
        BaseItem.paint(self, painter, option, widget)

        pen = self.pen()
        if self.isSelected():
            pen.setStyle(Qt.DashLine)
        painter.setPen(pen)

        for k in range(-1, len(self._polygon)-1):
            p1 = self._polygon[k]
            p2 = self._polygon[k+1]
            painter.drawLine(p1, p2)

    def dataChange(self):
        polygon = self._dataToPolygon(self._model_item)
        self._updatePolygon(polygon)


class LineItem(BaseItem):
    def __init__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        BaseItem.__init__(self, idName, signalObj, model_item, sceneRect, prefix, parent)

        self._line = None
        self._resize = False
        self._resize_start = None
        self._resize_start_line = None
        self._upper_half_clicked = None
        self._lower_half_clicked = None
        self._updateLine(self._dataToLine(self._model_item))
        # LOG.debug("Constructed line %s for model item %s" % (self._line, model_item))

    def __call__(self, idName, signalObj, model_item=None, sceneRect = None, prefix="", parent=None):
        item = LineItem(idName, signalObj, model_item, sceneRect, prefix, parent)
        item.setPen(self.pen())
        item.setBrush(self.brush())
        return item

        
    def _dataToLine(self, model_item):
        if model_item is None:
            return QLineF()

        try:
            return QLineF(float(model_item[self.prefix() + 'x0']),
                          float(model_item[self.prefix() + 'y0']),
                          float(model_item[self.prefix() + 'x1']),
                          float(model_item[self.prefix() + 'y1']))
        except KeyError as e:
            LOG.debug("LineItem: Could not find expected key in item: "
                      + str(e) + ". Check your config!")
            print "LineItem: Could not find expected key in item: ",  str(e),  ". Check your config!"
            self.setValid(False)
            return QLineF()

    def _updateLine(self, line):
        if line == self._line:
            return

        self.prepareGeometryChange()
        self._line = line
        self.setPos(line.p1())

    def updateModel(self):
        self._line = QLineF(self.scenePos(), QPointF(self.scenePos().x(), self.scenePos().y() + (self._line.p2().y() - self._line.p1().y())))
        self._model_item.update({
            self.prefix() + 'x0':      float(self._line.p1().x()),
            self.prefix() + 'y0':      float(self._line.p1().y()),
            self.prefix() + 'x1':      float(self._line.p2().x()),
            self.prefix() + 'y1':      float(self._line.p2().y()),
        })


    def boundingRect(self):
        penWidth = self.pen().widthF() * 4
        ed = self._line.p2().y() - self._line.p1().y()
        return QRectF(QPointF(-penWidth/2, 0), QPointF(penWidth/2, ed))

    def paint(self, painter, option, widget=None):
        BaseItem.paint(self, painter, option, widget)

        pen = self.pen()
        if self.isSelected():
            pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        penWidth = self.pen().widthF()
        linex = self.boundingRect().topLeft().x() + penWidth/2
        painter.drawLine(QLineF(linex, self.boundingRect().top(), linex, self.boundingRect().bottom()))


    def dataChange(self):
        line = self._dataToLine(self._model_item)
        self._updateLine(line)

    def mousePressEvent(self, event):
        # LOG.info("LineItem.mousePressEvent line  ...")
        #if event.modifiers() & Qt.ControlModifier != 0:
        if event.button() & Qt.RightButton != 0:
            self._resize = True
            self._resize_start = event.scenePos()
            self._resize_start_line = QLineF(self._line)
            center = [(self._resize_start_line.p1().x() + self._resize_start_line.p2().x()) / 2,
                      (self._resize_start_line.p1().y() + self._resize_start_line.p2().y()) / 2]
            self._upper_half_clicked = (event.scenePos().y() < center[1])
            self._lower_half_clicked = (event.scenePos().y() > center[1])
            event.accept()
        else:
            BaseItem.mousePressEvent(self, event)
            event.accept()

    def mouseMoveEvent(self, event):
        # LOG.info("LineItem.mouseMoveEvent self._resize {} self._upper_half_clicked {} self._lower_half_clicked {}...".format(self._resize, self._upper_half_clicked, self._lower_half_clicked))
        if self._resize:
            diff = event.scenePos() - self._resize_start
            if self._upper_half_clicked:
                x = self._resize_start_line.x1() + diff.x()
                w = self._resize_start_line.dx() - diff.x()
            else:
                x = self._resize_start_line.x1()
                w = self._resize_start_line.dx() + diff.x()

            if self._upper_half_clicked:
                y = self._resize_start_line.y1() + diff.y()
                h = self._resize_start_line.dy() - diff.y()
            else:
                y = self._resize_start_line.y1()
                h = self._resize_start_line.dy() + diff.y()

            img_sz =  self._imgsz

            if(x<0): x = 0
            if(y<0): y = 0
            if(x>img_sz[0]-1):
                x = img_sz[0]-1
            if(y>img_sz[1]-1):
                y = img_sz[1]-1

            if(x+w > img_sz[0]):
                w = img_sz[0]-1 - x
            if(y+h > img_sz[1]):
                h = img_sz[1]-1 - y

            # rect = QLineF(QPointF(x, y), QPointF(x+w, y+h)).translated (-QPointF(0, 0) if self._sceneRect is None else -self._sceneRect.topLeft())
            rect = QLineF(QPointF(x, y), QPointF(x+w, y+h))

            self._updateLine(rect)
            self.updateModel()
            event.accept()
        else:
            BaseItem.mouseMoveEvent(self, event)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self._resize:
            self._resize = False
            event.accept()
        else:
            BaseItem.mouseReleaseEvent(self, event)
            event.accept()

    def keyPressEvent(self, event):
        BaseItem.keyPressEvent(self, event)
        step = 1.0
        if event.modifiers() & Qt.ShiftModifier:
            step = 5.0
        ds = {Qt.Key_Left:  (-step, 0),
              Qt.Key_Right: (step, 0),
              Qt.Key_Up:    (0, -step),
              Qt.Key_Down:  (0, step),
             }.get(event.key(), None)
        if ds is not None:
            if event.modifiers() & Qt.ControlModifier:
                line = self._line.setP2(self._line.x2 + ds[0], self._line.p2().y + ds[1])
                # print "adjust p2 {} => {}".format(self._line().p2(), line.p2())
            else:
                line = self._line.translated(ds[0], ds[1])
            self._updateLine(line)
            self.updateModel()
            event.accept()
