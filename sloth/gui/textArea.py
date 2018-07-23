# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from sloth.gui.floatinglayout import FloatingLayout
import logging
from sloth.conf import config
from sloth.gui import utils
from sloth.gui.utils import MyVBoxLayout
from sloth.annotations.model import getFace5PointsFromModelItemOrAnnotation
             

LOG = logging.getLogger(config.LOG_FILE_NAME)
UNSET_VALUE  = u'-'

class TextAreaWidget(QWidget):
                
    def __init__(self, displayName = None, parent=None):
        QWidget.__init__(self, parent)

        self.vlayout = QVBoxLayout() #QVBoxLayout()
        # self.vlayout.setAlignment(Qt.AlignTop)
        # self.vlayout.setSpacing(4)
        # self.vlayout.setMargin(4)
        # self.vlayout.setContentsMargins(0, 0, 0, 44)
        
        self.textWidget = QTextEdit('')
        self.vlayout.addWidget(self.textWidget)
        # self.vlayout.addStretch(1)
        self.textWidget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.setLayout(self.vlayout)
        
        self.objCnt = 0
        return
    
    def update(self, objAnnotation):
        if objAnnotation is None:
            desc = ''
        else:    
            self.objCnt = 0
            desc = self.parseAnnotation(objAnnotation)
            
        self.textWidget.setPlainText(desc)
        return
        
    
    def parseAnnotation(self, objAnnotation):
        desc = ''  
        clsName   = objAnnotation.get(config.METADATA_LABELCLASS_TOKEN  , None)
        x         = objAnnotation.get(config.METADATA_POS_X_TOKEN       , None)
        y         = objAnnotation.get(config.METADATA_POS_Y_TOKEN       , None)
        width     = objAnnotation.get(config.METADATA_SIZE_WIDTH_TOKEN  , None)
        height    = objAnnotation.get(config.METADATA_SIZE_HEIGHT_TOKEN , None)
        age       = objAnnotation.get(config.ANNOTATION_AGE_TOKEN       , None)
        gender    = objAnnotation.get(config.ANNOTATION_GENDER_TOKEN    , None)
        angle     = objAnnotation.get(config.ANNOTATION_ANGLE_TOKEN     , None)
        hairstyle = objAnnotation.get(config.ANNOTATION_HAIR_STYLE_TOKEN, None)
        desc_umbrella        = ""
        desc_backpack        = ""
        desc_carryingbag     = ""
        desc_hat             = ""
        desc_mask            = ""
        desc_glasses         = ""
        desc_luggage         = ""
        desc_head_pos        = ""
        desc_uppercolor      = ""
        desc_upper_pos       = ""
        desc_umbrella_pos    = ""
        desc_backpack_pos    = ""
        desc_carryingbag_pos = ""
        desc_hat_pos         = ""
        desc_mask_pos        = ""
        desc_glasses_pos     = ""
        desc_luggage_pos     = ""
        desc_lowercolor      = ""
        desc_lower_pos       = ""
        desc_face_pos        = ""
        desc_face5Points_pos = ""
        
        if  ( clsName == config.ANNOTATION_PEDESTRAIN_TOKEN ) or  ( clsName == config.ANNOTATION_PERSONBIKE_TOKEN ) :
            desc_umbrella        = u'打伞\t: {}\n'.format(u'否')
            desc_backpack        = u'背包\t: {}\n'.format(u'否')
            desc_carryingbag     = u'手拎物\t: {}\n'.format(u'否')
            desc_hat             = u'戴帽\t: {}\n'.format(u'否')
            desc_mask            = u'口罩\t: {}\n'.format(u'否')
            desc_glasses         = u'眼镜\t: {}\n'.format(u'否')
            desc_luggage         = u'拉杆箱\t: {}\n'.format(u'否')
            desc_head_pos        = u"头部位置\t: ({}, {})\t({}, {})\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
            desc_uppercolor      = u"上衣颜色\t: {} {} {}\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
            desc_upper_pos       = u"上身位置\t: ({}, {})\t({}, {})\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
            desc_umbrella_pos    = u"雨伞位置\t: ({}, {})\t({}, {})\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
            desc_backpack_pos    = u"背包位置\t: ({}, {})\t({}, {})\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
            desc_carryingbag_pos = u"手拎物位置\t: ({}, {})\t({}, {})\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
            desc_hat_pos         = u"帽子位置\t: ({}, {})\t({}, {})\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
            desc_mask_pos        = u"口罩位置\t: ({}, {})\t({}, {})\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
            desc_glasses_pos     = u"眼镜位置\t: ({}, {})\t({}, {})\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
            desc_luggage_pos     = u"拉杆箱位置\t: ({}, {})\t({}, {})\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
        if  ( clsName == config.ANNOTATION_PEDESTRAIN_TOKEN ):
            desc_lowercolor      = u"下衣颜色\t: {}\t{}\t{}\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
            desc_lower_pos       = u"下身位置\t: ({}, {})\t({}, {})\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
        if  ( clsName == config.ANNOTATION_HEAD_TOKEN ) :
            desc_face_pos        = u"脸部位置\t: ({}, {})\t({}, {})\n".format(UNSET_VALUE, UNSET_VALUE, UNSET_VALUE, UNSET_VALUE)
        if  ( clsName == config.ANNOTATION_FACE_TOKEN ) :
            desc_face5Points_pos = u"脸部5点位置\t: {}\t({}, {})\t{}\t({}, {})\t{}\t({}, {})\t{}\t({}, {})\t{}\t({}, {})\n".format(
            config.GUI_LEFT_EYE_CENTER_WIDGET_DISPLAYTEXT   , UNSET_VALUE, UNSET_VALUE,
            config.GUI_RIGHT_EYE_CENTER_WIDGET_DISPLAYTEXT  , UNSET_VALUE, UNSET_VALUE,
            config.GUI_NOSE_TIP_WIDGET_DISPLAYTEXT          , UNSET_VALUE, UNSET_VALUE,
            config.GUI_LEFT_MOUTH_CORNER_WIDGET_DISPLAYTEXT , UNSET_VALUE, UNSET_VALUE,
            config.GUI_RIGHT_MOUTH_CORNER_WIDGET_DISPLAYTEXT, UNSET_VALUE, UNSET_VALUE)            
        desc_subobj = ''
        
        clsDisplayText = config.getSpecificLabelInfo(clsName, config.METADATA_DISPLAYTEXT_TOKEN)
        if (clsName == config.ANNOTATION_PEDESTRAIN_TOKEN) or (clsName == config.ANNOTATION_PERSONBIKE_TOKEN):
            desc += u'===================== 物体 {} ===================\n'.format(self.objCnt)
            self.objCnt += 1
            # print "1 objcnt = {} clsName = {}".format(self.objCnt, clsName)
            desc += u"{}位置\t{}: ({}, {})\t({}, {})\n".format(clsDisplayText, '', int(x), int(y), int(width), int(height))
            desc += u"{}\t：{}\n".format(config.GUI_GENDER_WIDGET_DISPLAYTEXT,     config.getLabelText( gender  ) if gender    is not None else UNSET_VALUE )
            desc += u"{}\t：{}\n".format(config.GUI_AGE_WIDGET_DISPLAYTEXT,        config.getLabelText(age      ) if age       is not None else UNSET_VALUE )
            desc += u"{}\t：{}\n".format(config.GUI_ANGLE_WIDGET_DISPLAYTEXT,      config.getLabelText(angle    ) if angle     is not None else UNSET_VALUE )
            desc += u"{}\t：{}\n".format(config.GUI_HAIR_STYLE_WIDGET_DISPLAYTEXT, config.getLabelText(hairstyle) if hairstyle is not None else UNSET_VALUE )
        elif clsName == config.ANNOTATION_VEHICLE_TOKEN:
            desc += u'============ 物体 {} ==========\n'.format(self.objCnt)
            self.objCnt += 1
            desc += u"{}位置\t{}: ({}, {})\t({}, {})\n".format(clsDisplayText, '', int(x), int(y), int(width), int(height))
            rgb0Value = objAnnotation.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '0',    None)
            rgb1Value = objAnnotation.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '1',    None) if rgb0Value is not None else None
            rgb2Value = objAnnotation.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '2',    None) if rgb1Value is not None else None
            rgb0Tag   = objAnnotation.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '0Tag', None)
            rgb1Tag   = objAnnotation.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '1Tag', None) if rgb0Tag is not None else None
            rgb2Tag   = objAnnotation.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '2Tag', None) if rgb1Tag is not None else None
            desc += u"车身颜色\t: {}\t{}\t{}\n".format(
                config.getColorGroupSpecificLabelInfo(config.ANNOTATION_VEHICLE_COLOR_TOKEN,  rgb0Tag) if rgb0Tag is not None else UNSET_VALUE,
                config.getColorGroupSpecificLabelInfo(config.ANNOTATION_VEHICLE_COLOR_TOKEN,  rgb1Tag) if rgb1Tag is not None else UNSET_VALUE,
                config.getColorGroupSpecificLabelInfo(config.ANNOTATION_VEHICLE_COLOR_TOKEN,  rgb2Tag) if rgb2Tag is not None else UNSET_VALUE )
        else:
            desc += u"{}位置\t{}: ({}, {})\t({}, {})\n".format(clsDisplayText,  '', int(x) if x else -1, int(y) if y else -1, int(width) if width else -1, int(height) if height else -1)
            
        subObjAnnotationsList = objAnnotation.get(config.CHILD_ITEM_CLASS_TOKEN , None)
        
        if subObjAnnotationsList is not None:
    
            for subObjAnnotation in subObjAnnotationsList:
                subclsName = subObjAnnotation.get(config.METADATA_LABELCLASS_TOKEN  , None)
                # print "subclsName = {} subObjAnnotation = {}".format(subclsName, subObjAnnotation)
                
                if subclsName == config.ANNOTATION_UPPER_BODY_TOKEN:
                    rgb0Value = subObjAnnotation.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '0',    None)
                    rgb1Value = subObjAnnotation.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '1',    None) if rgb0Value is not None else None
                    rgb2Value = subObjAnnotation.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '2',    None) if rgb1Value is not None else None
                    rgb0Tag   = subObjAnnotation.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '0Tag', None)
                    rgb1Tag   = subObjAnnotation.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '1Tag', None) if rgb0Tag is not None else None
                    rgb2Tag   = subObjAnnotation.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '2Tag', None) if rgb1Tag is not None else None
                    desc_uppercolor = u"上衣颜色\t: {}\t{}\t{}\n".format(
                        config.getColorGroupSpecificLabelInfo(config.ANNOTATION_UPPER_COLOR_TOKEN,  rgb0Tag) if rgb0Tag is not None else UNSET_VALUE,
                        config.getColorGroupSpecificLabelInfo(config.ANNOTATION_UPPER_COLOR_TOKEN,  rgb1Tag) if rgb1Tag is not None else UNSET_VALUE,
                        config.getColorGroupSpecificLabelInfo(config.ANNOTATION_UPPER_COLOR_TOKEN,  rgb2Tag) if rgb2Tag is not None else UNSET_VALUE )
                
                    desc_upper_pos = self.parseAnnotation(subObjAnnotation)
                                
                elif subclsName == config.ANNOTATION_LOWER_BODY_TOKEN:
                    rgb0Value = subObjAnnotation.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '0',    None)
                    rgb1Value = subObjAnnotation.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '1',    None) if rgb0Value is not None else None
                    rgb2Value = subObjAnnotation.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '2',    None) if rgb1Value is not None else None
                    rgb0Tag   = subObjAnnotation.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '0Tag', None)
                    rgb1Tag   = subObjAnnotation.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '1Tag', None) if rgb0Tag is not None else None
                    rgb2Tag   = subObjAnnotation.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '2Tag', None) if rgb1Tag is not None else None
                    desc_lowercolor = u"下衣颜色\t: {}\t{}\t{}\n".format(
                        config.getColorGroupSpecificLabelInfo(config.ANNOTATION_LOWER_COLOR_TOKEN,  rgb0Tag) if rgb0Tag is not None else UNSET_VALUE,
                        config.getColorGroupSpecificLabelInfo(config.ANNOTATION_LOWER_COLOR_TOKEN,  rgb1Tag) if rgb1Tag is not None else UNSET_VALUE,
                        config.getColorGroupSpecificLabelInfo(config.ANNOTATION_LOWER_COLOR_TOKEN,  rgb2Tag) if rgb2Tag is not None else UNSET_VALUE )
                    desc_lower_pos = self.parseAnnotation(subObjAnnotation)
            
                elif subclsName == config.ANNOTATION_UMBRELLA_TOKEN:
                    desc_umbrella = u'打伞\t: {}\n'.format(u'是')
                    desc_umbrella_pos = self.parseAnnotation(subObjAnnotation)
                elif subclsName == config.ANNOTATION_BACKPACK_WIDGET_TOKEN:
                    desc_backpack = u'背包\t: {}\n'.format(u'是')
                    desc_backpack_pos = self.parseAnnotation(subObjAnnotation)    
                elif subclsName == config.ANNOTATION_CARRINGBAG_WIDGET_TOKEN:
                    desc_carryingbag = u'手拎物\t: {}\n'.format(u'是')
                    desc_carryingbag_pos = self.parseAnnotation(subObjAnnotation)  
                elif subclsName == config.ANNOTATION_HAT_WIDGET_TOKEN:
                    desc_hat = u'戴帽\t: {}\n'.format(u'是')
                    desc_hat_pos = self.parseAnnotation(subObjAnnotation)      
                elif subclsName == config.ANNOTATION_MASK_WIDGET_TOKEN:
                    desc_mask = u'口罩\t: {}\n'.format(u'是')
                    desc_mask_pos = self.parseAnnotation(subObjAnnotation)       
                elif subclsName == config.ANNOTATION_GLASSES_WIDGET_TOKEN:
                    desc_glasses = u'眼镜\t: {}\n'.format(u'是')
                    desc_glasses_pos = self.parseAnnotation(subObjAnnotation) 
                elif subclsName == config.ANNOTATION_LUGGAGE_WIDGET_TOKEN:
                    desc_luggage = u'拉杆箱\t: {}\n'.format(u'是')
                    desc_luggage_pos = self.parseAnnotation(subObjAnnotation) 
                elif subclsName == config.ANNOTATION_FACE_TOKEN:
                    desc_face_pos = self.parseAnnotation(subObjAnnotation)
                
                elif subclsName == config.ANNOTATION_FACE5POINTS_TOKEN:
                    (lec, rec, lmc, rmc, nt) = getFace5PointsFromModelItemOrAnnotation(subObjAnnotation)
                    desc_face5Points_pos = u"{}\n\t- {}\t({}, {})\n\t- {}\t({}, {})\n\t- {}\t({}, {})\n\t- {}\t({}, {})\n\t- {}\t({}, {})\n".format(
                        config.GUI_FACE5POINTS_WIDGET_DISPLAYTEXT,
                        config.GUI_LEFT_EYE_CENTER_WIDGET_DISPLAYTEXT, int(lec.x()) if lec else UNSET_VALUE,
                        int(lec.y()) if lec else UNSET_VALUE,
                        config.GUI_RIGHT_EYE_CENTER_WIDGET_DISPLAYTEXT, int(rec.y()) if rec else UNSET_VALUE,
                        int(rec.y()) if rec else UNSET_VALUE,
                        config.GUI_NOSE_TIP_WIDGET_DISPLAYTEXT, int(nt.x()) if nt  else UNSET_VALUE,
                        int(nt.y()) if nt  else UNSET_VALUE,
                        config.GUI_LEFT_MOUTH_CORNER_WIDGET_DISPLAYTEXT, int(lmc.x()) if lmc else UNSET_VALUE,
                        int(lmc.y()) if lmc else UNSET_VALUE,
                        config.GUI_RIGHT_MOUTH_CORNER_WIDGET_DISPLAYTEXT, int(rmc.x()) if rmc else UNSET_VALUE,
                        int(rmc.y()) if rmc else UNSET_VALUE)
                
                elif subclsName == config.ANNOTATION_HEAD_TOKEN:
                    desc_head_pos = self.parseAnnotation(subObjAnnotation)
                    
                else:
                    # print "3 subclsName = {} subObjAnnotation = {}".format(subclsName, subObjAnnotation)
                    desc_subobj += self.parseAnnotation(subObjAnnotation)
                
        # if  ( clsName == config.ANNOTATION_PEDESTRAIN_TOKEN ) or  ( clsName == config.ANNOTATION_PERSONBIKE_TOKEN ) or  ( clsName == config.ANNOTATION_VEHICLE_TOKEN ):
        if True:
            desc += desc_uppercolor  
            desc += desc_lowercolor
            desc += desc_umbrella 
            desc += desc_backpack
            desc += desc_carryingbag
            desc += desc_hat
            desc += desc_mask
            desc += desc_glasses
            desc += desc_luggage
            # desc += u'------------------------------\n'
            desc += desc_upper_pos
            desc += desc_lower_pos
            desc += desc_head_pos
            desc += desc_face_pos
            desc += desc_face5Points_pos
            desc += desc_umbrella_pos
            desc += desc_backpack_pos
            desc += desc_carryingbag_pos
            desc += desc_hat_pos
            desc += desc_mask_pos
            desc += desc_glasses_pos
            desc += desc_luggage_pos
            desc += desc_subobj        
        

        return desc


