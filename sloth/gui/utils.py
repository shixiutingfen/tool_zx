# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

from PyQt4.QtCore import QSize
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import Qt, QString
from PyQt4.Qt import QColor
from sloth.conf import config
import logging
import math
from PyQt4.QtGui import QDesktopWidget

LOG = logging.getLogger(config.LOG_FILE_NAME)

# This is really really ugly, but the QDockWidget for some reason does not notice when
# its child widget becomes smaller...
# Therefore we manually set its minimum size when our own minimum size changes
class MyVBoxLayout(QVBoxLayout):
    def __init__(self, parent=None):
        QVBoxLayout.__init__(self, parent)
        self._last_size = QSize(0, 0)

    def setGeometry(self, r):
        QVBoxLayout.setGeometry(self, r)
        try:
            wid = self.parentWidget().parentWidget()

            new_size = self.minimumSize()
            if new_size == self._last_size: return
            self._last_size = new_size

            twid = wid.titleBarWidget()
            if twid is not None:
                theight = twid.sizeHint().height()
            else:
                theight = 0

            new_size += QSize(0, theight)
            wid.setMinimumSize(new_size)

        except Exception:
            pass


def set_qobj_stylesheet(widgetObj, widgetClassTypeStr, widgetBackgroundColor = None, widgetTextColor = None, widgetBackgroundColorWhenChecked= None, widgetTextColorWhenChecked = None, margin_pixels = 4, padding_pixels = 4, min_width_pixels = 36):

    bkgColor, txtColor = "", ""
    bkgColorPressed, txtColorPressed = "", ""
    
    (_widgetBackgroundColor, dummy)            = parseHexColorAlpha(widgetBackgroundColor           ) if widgetBackgroundColor            is not None else (None, None)
    (_widgetTextColor, dummy)                  = parseHexColorAlpha(widgetTextColor                 ) if widgetTextColor                  is not None else (None, None)
    (_widgetBackgroundColorWhenChecked, dummy) = parseHexColorAlpha(widgetBackgroundColorWhenChecked) if widgetBackgroundColorWhenChecked is not None else (None, None)
    (_widgetTextColorWhenChecked, dummy)       = parseHexColorAlpha(widgetTextColorWhenChecked      ) if widgetTextColorWhenChecked       is not None else (None, None)

    # print "_widgetBackgroundColor {} _widgetTextColor {} _widgetBackgroundColorWhenChecked {} _widgetTextColorWhenChecked {}".format(
    #        _widgetBackgroundColor, _widgetTextColor, _widgetBackgroundColorWhenChecked, _widgetTextColorWhenChecked )
    
    if _widgetBackgroundColor is not None and _widgetBackgroundColor != "":
        bkgColor = "background-color: {}; ".format(_widgetBackgroundColor)
        
    if _widgetTextColor is not None and _widgetTextColor != "":
        txtColor = "color: {}; ".format(_widgetTextColor)

    if _widgetBackgroundColorWhenChecked is not None and _widgetBackgroundColorWhenChecked != "":
        bkgColorPressed = "background-color: {}; ".format(_widgetBackgroundColorWhenChecked)
        
    if _widgetTextColorWhenChecked is not None and _widgetTextColorWhenChecked != "":
        txtColorPressed = "color: {}; ".format(_widgetTextColorWhenChecked)

    font, border = "", ""

    font  = "bold font: 14px; "
    border = "border-width: 4px;  border-color: gray; "
    margin = "margin-left: {}px;  margin-right: {}px; margin-top: {}px; min-width: {}px; padding: {}px; ".format(margin_pixels, margin_pixels, margin_pixels, min_width_pixels, padding_pixels)
    desc  = font
    desc += border
    desc += margin

    borderstyle = "border-style: {}; "  
            
    # print '[ZXD] {} {{ {} }}'.format(widgetClassTypeStr, desc)
    if desc != "":
        str = '{}:checked  {{ {} {} {} {} }}  {}{{ {} {} {} {} }} '.format(
        widgetClassTypeStr, desc,  bkgColorPressed,  txtColorPressed,   borderstyle.format('groove'),
        widgetClassTypeStr, desc,  bkgColor,         txtColor,          borderstyle.format('groove')
        )
        # LOG.debug("set_qobj_stylesheet ... {}".format(str))
        # print ("set_qobj_stylesheet ... {}".format(str))
        widgetObj.setStyleSheet(str)
        
    return desc

def update_qobj_displayColor(widgetObj, widgetClassTypeStr, widgetBackgroundColor = None, widgetTextColor = None, widgetBackgroundColorWhenChecked= None, widgetTextColorWhenChecked = None):

    bkgColor, txtColor = "", ""
    bkgColorPressed, txtColorPressed = "", ""
    
    (_widgetBackgroundColor, dummy)            = parseHexColorAlpha(widgetBackgroundColor           ) if widgetBackgroundColor            is not None else (None, None)
    (_widgetTextColor, dummy)                  = parseHexColorAlpha(widgetTextColor                 ) if widgetTextColor                  is not None else (None, None)
    (_widgetBackgroundColorWhenChecked, dummy) = parseHexColorAlpha(widgetBackgroundColorWhenChecked) if widgetBackgroundColorWhenChecked is not None else (None, None)
    (_widgetTextColorWhenChecked, dummy)       = parseHexColorAlpha(widgetTextColorWhenChecked      ) if widgetTextColorWhenChecked       is not None else (None, None)

    str =""
    hasColor = False
    if _widgetBackgroundColor is not None and _widgetBackgroundColor != "":
        bkgColor = "background-color: {}; ".format(_widgetBackgroundColor)
        hasColor = True
        
    if _widgetTextColor is not None and _widgetTextColor != "":
        txtColor = "color: {}; ".format(_widgetTextColor)
        hasColor = True

    if _widgetBackgroundColorWhenChecked is not None and _widgetBackgroundColorWhenChecked != "":
        bkgColorPressed = "background-color: {}; ".format(_widgetBackgroundColorWhenChecked)
        hasColor = True
        
    if _widgetTextColorWhenChecked is not None and _widgetTextColorWhenChecked != "":
        txtColorPressed = "color: {}; ".format(_widgetTextColorWhenChecked)
        hasColor = True

    if hasColor:
        str = '{}:checked  {{ {} {} }}  {}{{ {} {} }} '.format(
        widgetClassTypeStr, bkgColorPressed,  txtColorPressed,
        widgetClassTypeStr, bkgColor,         txtColor
        )
        
        print ("update_qobj_displayColor ... {}".format(str))
        widgetObj.setStyleSheet(str)
        
    return str


# =======================================================================================
# INPUT:
# - colorTag. string. e.g.: "red", "green", ...
# OUTPUT:
# - qtColor. corresponding QT color constant.
# - colorHexDesc. a string of color's hex RGB value prefixed with "#". i.e.: "#RRGGBB" or hex RGBA value prefixed with "#", i.e.: "#RRGGBBAA"
# =======================================================================================
def getColorDesc(_colorTag, outputAlpha = False):

    if _colorTag is None:
        return QColor(Qt.yellow), "#FFFF00"
        
    colorTag = _colorTag.lower()
    if(colorTag == "red"):
        qtColor = QColor(Qt.red)
    elif(colorTag =="green"):
        qtColor = QColor(Qt.green)
    elif(colorTag=="blue"):
        qtColor = QColor(Qt.blue)
    elif(colorTag=="cyan"):
        qtColor = QColor(Qt.cyan)
    elif(colorTag=="darkGray"):
        qtColor = QColor(Qt.darkGray)
    elif(colorTag=="magenta"):
        qtColor = QColor(Qt.magenta)
    elif(colorTag[0]=="#"):
        colorHexDesc = colorTag
        qtColor = hexColorStrToQtColor(colorTag, outputAlpha)
    else:
        qtColor = QColor(Qt.yellow)
        colorHexDesc = "#FFFF00"
   
    if qtColor is not None:
        colorHexDesc = "#%02x%02x%02x" % (  qtColor.red(), qtColor.green(), qtColor.blue())
        

    # LOG.info("qtColor = {}, colorHexDesc = {}".format(qtColor, colorHexDesc))
    return qtColor, colorHexDesc
    

# =======================================================================================
# INPUT:
# - hexColorStr : a string of color's hex RGB value prefixed with "#". i.e.: "#RRGGBB" or hex RGBA value prefixed with "#", i.e.: "#RRGGBBAA"
# OUTPUT:
# - qtColor. corresponding QT color constant.
# =======================================================================================
def parseHexColorAlpha(hexColorStr):
    if (hexColorStr is None): 
        return "#FFFF00"
    t = len(hexColorStr)
    if (t > 7):
        return hexColorStr[0:7], int(hexColorStr[7:9])
    elif (t == 7):
        return hexColorStr, 255
        
def hexColorStrToQtColor(hexColorStr, outputAlpha = False):
    if hexColorStr is None: 
        return QColor(Qt.yellow) 
    t = len(hexColorStr)
    if (t != 7) and (t != 9):
        return QColor(Qt.yellow) 

    if outputAlpha:
        return QColor(int('0x' + hexColorStr[1:3], 16), int('0x' + hexColorStr[3:5], 16), int('0x' + hexColorStr[5:7], 16), int('0x' + 'ff' if hexColorStr[7:9] == '' else hexColorStr[7:9], 16) )
    else:
        # print "int('0x' + hexColorStr[1:3], 16) {}, int('0x' + hexColorStr[3:5], 16) {}, int('0x' + hexColorStr[5:7], 16) {}".format(int('0x' + hexColorStr[1:3], 16), int('0x' + hexColorStr[3:5], 16), int('0x' + hexColorStr[5:7], 16))
        return QColor(int('0x' + hexColorStr[1:3], 16), int('0x' + hexColorStr[3:5], 16), int('0x' + hexColorStr[5:7], 16) )

    
def hexColorStrToRGBA(hexColorStr):
    if hexColorStr is None: 
        return (255, 255, 0, 0)
    t = len(hexColorStr)
    if (t != 7) and (t != 9):
        return (255, 255, 0, 0)
    return (int('0x' + hexColorStr[1:3], 16), int('0x' + hexColorStr[3:5], 16), int('0x' + hexColorStr[5:7], 16), int('0x' + 'ff' if hexColorStr[7:9] == '' else hexColorStr[7:9], 16) )
    
    
def colorTagToQtColor(_colorTag, outputAlpha = False):
    
    if _colorTag is None:
        return QColor(Qt.yellow)
        
    colorTag = _colorTag.lower()

    
    if(colorTag == "red"):
        qtColor = QColor(Qt.red)
    elif(colorTag =="green"):
        qtColor = QColor(Qt.green)
    elif(colorTag=="blue"):
        qtColor = QColor(Qt.blue)
    elif(colorTag=="cyan"):
        qtColor = QColor(Qt.cyan)
    elif(colorTag=="darkGray"):
        qtColor = QColor(Qt.darkGray)
    elif(colorTag=="magenta"):
        qtColor = QColor(Qt.magenta)
    elif(colorTag=="yellow"):
        return QColor(Qt.yellow)
    elif(colorTag[0]=="#"):
        qtColor = hexColorStrToQtColor(colorTag, outputAlpha)
    else:
        qtColor = QColor(Qt.yellow)
    return qtColor
    
    
def colorStrToQtColor(colorStr, outputAlpha = False):   
    if colorStr is None:
        return QColor(Qt.yellow)
        
    if colorStr[0] == '#':
        return hexColorStrToQtColor(colorStr, outputAlpha)
    else:
        return colorTagToQtColor(colorStr, outputAlpha)  

  
    
def statisticPedestrainObjInfo(cur_img):
    info = {}
    i = config.ANNOTATION_PEDESTRAIN_TOKEN
    # LOG.info("cur_img.getAnnotations() = {}".format(cur_img.getAnnotations()))
    info, dummy = iterativeStatisticObjInfo(cur_img, config.METADATA_LABELCLASS_TOKEN, i, info)
    
    str = "P{}|{}|{}|{} U{}|{}|{} L{}|{}|{} H{} ".format(
            info.get(config.ANNOTATION_PEDESTRAIN_TOKEN     , '0'),
            info.get(config.ANNOTATION_GENDER_TOKEN         , '0'), 
            info.get(config.ANNOTATION_AGE_TOKEN            , '0'), 
            info.get(config.ANNOTATION_ANGLE_TOKEN          , '0'),
            info.get(config.ANNOTATION_UPPER_BODY_TOKEN     , '0'), 
            info.get(config.ANNOTATION_UPPER_COLOR_TOKEN+'0', '0'), 
            info.get(config.ANNOTATION_UPPER_CLOTH_TOKEN    , '0'), 
            info.get(config.ANNOTATION_LOWER_BODY_TOKEN     , '0'), 
            info.get(config.ANNOTATION_LOWER_COLOR_TOKEN+'0', '0'), 
            info.get(config.ANNOTATION_LOWER_CLOTH_TOKEN    , '0'), 
            info.get(config.ANNOTATION_HEAD_TOKEN           , '0') 
            )
    return str, info                      
                       
        
def iterativeStatisticObjInfo(cur_img, parentStartToken, startToken, info):
    # LOG.info("1 : parentStartToken = {} startToken = {} {} ".format(startToken, parentStartToken, info))

    if startToken in config.OBJ_TO_CHILDOBJ_AND_ATTR_DICT.keys():
        info[startToken] = cur_img.getSpecificLabelsNum(parentStartToken, startToken)
        # LOG.info("2 : parentStartToken = {} startToken = {} info[{}] = {}".format(parentStartToken, startToken, startToken, info[startToken]))
        parentstartToken = startToken
        for i in config.OBJ_TO_CHILDOBJ_AND_ATTR_DICT[startToken]:
            co = i[0]
            # LOG.info("3: parentStartToken = {} startToken = {} co = {} dict = {}".format(parentStartToken, startToken, co, config.OBJ_TO_CHILDOBJ_AND_ATTR_DICT[startToken]))
            if co in config.OBJ_TO_CHILDOBJ_AND_ATTR_DICT.keys():
                # co is a non-leaf node
                info, dummy = iterativeStatisticObjInfo(cur_img, parentstartToken, co, info)
                # LOG.info("4: parentStartToken = {} startToken = {} co = {} => parentStartToken = {}".format(parentStartToken, startToken, co,  dummy))
            else:
                # co is a leaf node
                j = co
                j += '0' if co==config.ANNOTATION_UPPER_COLOR_TOKEN or co==config.ANNOTATION_LOWER_COLOR_TOKEN or co == config.ANNOTATION_VEHICLE_COLOR_TOKEN else ''
                info[j] = cur_img.getSpecificLabelsNum(j, None)
                # LOG.info("5 : parentStartToken = {} startToken = {} info[{}] = {}".format(parentStartToken, startToken, j, info[j]))
    return info, parentstartToken


def statisticPersonBikeObjInfo(cur_img):
    info = {}
    i = config.ANNOTATION_PERSONBIKE_TOKEN
    # LOG.info("cur_img.getAnnotations() = {}".format(cur_img.getAnnotations()))
    info, dummy = iterativeStatisticObjInfo(cur_img, config.METADATA_LABELCLASS_TOKEN, i, info)
    str = "B{} U{}|{}|{} H{}".format(
        info.get(config.ANNOTATION_PERSONBIKE_TOKEN,     '0'),
        info.get(config.ANNOTATION_UPPER_BODY_TOKEN,     '0'),  
        info.get(config.ANNOTATION_UPPER_COLOR_TOKEN+'0','0'),
        info.get(config.ANNOTATION_UPPER_CLOTH_TOKEN,    '0'),  
        info.get(config.ANNOTATION_HEAD_TOKEN,           '0'),  
        info.get(config.ANNOTATION_GENDER_TOKEN,         '0'),  
        info.get(config.ANNOTATION_AGE_TOKEN,            '0'),  
        info.get(config.ANNOTATION_ANGLE_TOKEN,          '0') 
        )    
    return str, info                      


def statisticVehicleObjInfo(cur_img):
    info = {}
    i = config.ANNOTATION_VEHICLE_TOKEN
    # LOG.info("cur_img.getAnnotations() = {}".format(cur_img.getAnnotations()))
    info, dummy = iterativeStatisticObjInfo(cur_img, config.METADATA_LABELCLASS_TOKEN, i, info)
    str = "V{}|{}".format(
        info.get(config.ANNOTATION_VEHICLE_TOKEN,          '0'),
        info.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN,    '0')
        )    
    return str, info               
    
    
def delUnusedAnnotation(annotations):
    if type(annotations) is not dict and type(annotations) is not list:
        return

    # print "type(annotations) = {} {}".format(type(annotations), annotations)
    if annotations:
        for a in annotations:
            # print "type(a) = {} {}".format(type(a), a)
            if type(a) is dict:
                for i in config.UNSAVED_METADATAS_IN_ANNOTATION_SET:
                    if i in a.keys():
                        LOG.info(u"del a[{}]={} from {}".format(i, a[i], a))
                        del a[i]
        
                for akey, aval in a.items():
                    delUnusedAnnotation(aval)
            else:
                delUnusedAnnotation(a)
                        
    return
    
    
def ROUND_VALUE(_x, leftBoundaryInclusive, rightBoundaryExclusive):
    x = _x
    remain = (x - rightBoundaryExclusive) % (rightBoundaryExclusive - leftBoundaryInclusive) 
    if remain < 0:
        result = remain + rightBoundaryExclusive  
    else:
        result = remain + leftBoundaryInclusive
    return result
        
        

def centerGuiWidget(widget):
    qr = widget.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    widget.move(qr.topLeft())
 

def toUTFStr(fname):
    if fname is None:
        return None 
    if isinstance(fname, unicode):
        fnameutf = fname
    elif isinstance(fname, QString):
        try:
            fnameutf = str(fname)
        except:
            fnameutf = unicode(fname)
    else:
        fnameutf = fname.decode('gbk')    
    
    return fnameutf        