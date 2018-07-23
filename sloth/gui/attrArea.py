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
import cv2

# const
popupWidgetsInfo_pushButtonWidget_idx                   = 0               
popupWidgetsInfo_menuWidget_idx                         = 1               
popupWidgetsInfo_actionsWidgetList_idx                  = 2               
popupWidgetsInfo_actionsNameList_idx                    = 3               
popupWidgetsInfo_actionsTextList_idx                    = 4 
popupWidgetsInfo_actionsColorList_idx                   = 5 
popupWidgetsInfo_actionsWidgetStyleSheet_idx            = 6 
            
               
checkedWidgetsAttrDescList_checkedWidget_idx            = 0               
checkedWidgetsAttrDescList_checkedWidgetText_idx        = 1   
checkedWidgetsAttrDescList_checkedWidgetColor_idx       = 2             
checkedWidgetsAttrDescList_checkedWidgetStyleSheet_idx  = 3               
checkedWidgetsAttrDescList_checkedWidgetPopupParentWidget_idx = 4               

LOG = logging.getLogger(config.LOG_FILE_NAME)



class CheckboxListWidget(QGroupBox):
    
    def enableAll(self, enabled = True):
        for cbn, cbw in self.checkboxWidgetsInfo.items():
            cbw[0].setEnabled(enabled)

    def enable(self, checkBoxName, checked = True):
        cb = self.checkboxWidgetsInfo.get(checkBoxName, None)
        if cb is not None:
            cb[0].setEnabled(checked)
     
    # set all checkboxs' check status                    		
    def setCheckedAll(self, checked = True):
        for cbn, cbw in self.checkboxWidgetsInfo.items():
            cbw[0].setChecked(checked)

        if not checked:
            self._checked_checkbox_widgets = []

    # set one single specific checkbox's check status             
    def setCheckedCheckbox(self, checkBoxName, checked = True):
        cb = self.checkboxWidgetsInfo.get(checkBoxName, None)
        if cb is not None:
            checkboxWidget = cb [0]
            # LOG.info("{} CheckboxListWidget.setCheckedCheckbox for checkboxname {}  checked {} ..".format(self.idName, checkBoxName, checked))
            checkboxWidget.setChecked(checked)

    # set some specific checkboxs' check status            
    def setCheckedCheckboxs(self, checkBoxNamesList, checked = True):
        self._checked_checkbox_widgets = []
        if checkBoxNamesList is None:
            return
        for cbn in checkBoxNamesList:
            cw = self.checkboxWidgetsInfo.get(cbn, None)
            # LOG.info("{} self.checkboxWidgetsInfo = {} checkBoxNamesList = {}..".format(self.idName, self.checkboxWidgetsInfo, checkBoxNamesList))
            # LOG.info("{} CheckboxListWidget.setCheckedCheckboxs :  cbn {} cw {}..".format(self.idName, cbn, cw))
            if cw is not None:
                checkboxWidget = cw[0]
                # LOG.info("{} CheckboxListWidget.setCheckedCheckboxs for checkboxname {}  checked {} ..".format(self.idName, checkboxWidget, checked))
                checkboxWidget.setChecked(checked)
                if checked:
                    self._checked_checkbox_widgets.append(checkboxWidget)
            	    
        return self._checked_checkbox_widgets
        

                   
    def setMaxCheckedNum(self, num):
        self._maxCheckedNum = num
        
    def setMaxSeperateWidgetNum(self, num):
        self._maxSeperateWidgetNum = num
         
    def __init__(self, checkboxGroupName, checkboxGroupText, isExclusive, checkGroupDescListTuple, checkboxStateChangedSignal, thisGroup_maxCheckedNum = 100, thisGroup_maxSeperateWidgetNum = 100, parent = None):
        QGroupBox.__init__(self, checkboxGroupText, parent)
        qss = "QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; color : red; font-weight:bold; }"
        self.setStyleSheet(qss)
        
        self.flayout = FloatingLayout()
        self.flayout.setSpacing(40)
        self.flayout.setMargin(4)
 
        self.groupName = str(checkboxGroupName)
        
        self.checkGroupDescListTuple = checkGroupDescListTuple
        self.checkboxStateChangedSignal = checkboxStateChangedSignal

        self.checkbox_group = QButtonGroup()
        self.checkbox_group.setExclusive(isExclusive)
        self.isExclusive = isExclusive
        
        self.checkboxWidgetsInfo = {}  # dict. checkboxWidgetsInfo[checkboxName] = [checkboxWidget, checkboxText, checkboxColor, checkboxStyleSheet]
        self.popupWidgetsInfo = {}  # dict. popupWidgetsInfo[popupbutton_name] = [*, *, * , * , *]

        self._maxCheckedNum = thisGroup_maxCheckedNum
        self._maxSeperateWidgetNum = thisGroup_maxSeperateWidgetNum
        
        self._checked_checkbox_widgets = []

        # create all checkboxes in this group 
        optCnt = 0
        defaultCheckboxName = None
        firstCheckboxName = None
        for checkboxOption in checkGroupDescListTuple:

            thisCheckboxName = checkboxOption[config.METADATA_ATTR_VALUE_TOKEN]
            thisCheckboxText = checkboxOption[config.METADATA_DISPLAYTEXT_TOKEN]
            thisCheckboxIsDefault = checkboxOption.get(config.METADATA_IS_DEFAULT_TOKEN, False)
            defaultCheckboxName = thisCheckboxName if thisCheckboxIsDefault else defaultCheckboxName
            firstCheckboxName = thisCheckboxName if firstCheckboxName is None else firstCheckboxName
            
            if ( checkboxGroupName == config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN ) or  ( checkboxGroupName == config.ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN ):
                checkboxWidgetMinWidthInPixels = 52
            else:
                checkboxWidgetMinWidthInPixels = 38
            

            # get widget display color
            _thisCheckboxBkgColor = None
            _thisCheckboxBkgColorChecked = checkboxOption.get(config.COLOR_ATTR_RGB_VALUE_TOKEN, None)
            if _thisCheckboxBkgColorChecked:
                _thisCheckboxBkgColor = _thisCheckboxBkgColorChecked
            else:
                _thisCheckboxBkgColorChecked = checkboxOption.get(config.METADATA_DISPLAYCOLOR_TOKEN, None)
			
            # print u"thisCheckboxName = {} thisCheckboxText = {} _thisCheckboxBkgColor = {} _thisCheckboxBkgColorChecked = {}".format(
			# thisCheckboxName, thisCheckboxText, _thisCheckboxBkgColor, _thisCheckboxBkgColorChecked)
            
            thisCheckboxBkgColor = None
            if _thisCheckboxBkgColor:     
                dummy, thisCheckboxBkgColor = utils.getColorDesc(_thisCheckboxBkgColor)
            
            thisCheckboxBkgColorChecked = None
            if _thisCheckboxBkgColorChecked:
                dummy, thisCheckboxBkgColorChecked = utils.getColorDesc(_thisCheckboxBkgColorChecked)
            
            # calc widget text color
            # thisCheckboxBkgColorChecked string pattern: #123456
            txtColorChecked = None
            if thisCheckboxBkgColorChecked is not None:
                import math
                rgba = utils.hexColorStrToRGBA(thisCheckboxBkgColorChecked)
                distance = math.sqrt((rgba[0]-255)**2 + (rgba[1]-255)**2 + (rgba[2]-255)**2)
                txtColorChecked = '#ffffff' if distance > config.GUI_COLOR_TAG_TEXT_BLACKWHITE_TOGGLE_THRESHOLD else '#000000'
        	
            txtColor = txtColorChecked if checkboxGroupName == config.ANNOTATION_UPPER_COLOR_TOKEN or checkboxGroupName == config.ANNOTATION_LOWER_COLOR_TOKEN or checkboxGroupName == config.ANNOTATION_VEHICLE_COLOR_TOKEN else None


            # add widget to this group    
            if optCnt < thisGroup_maxSeperateWidgetNum:
                self.add_checkbox(thisCheckboxName, thisCheckboxText, thisCheckboxBkgColor, txtColor, thisCheckboxBkgColorChecked, txtColorChecked, checkboxWidgetMinWidthInPixels)
            else:
                self.add_popup_button(config.GUI_MORE_WIDGET_DISPLAYTEXT, thisCheckboxName, thisCheckboxText, popupbutton_background_color = "#808080",
                popupbutton_text_color = "#ffffff", checkbox_background_color = thisCheckboxBkgColor, checkbox_text_color = txtColor)

            optCnt += 1
        
        self._defaultCheckboxName = firstCheckboxName if defaultCheckboxName is None else defaultCheckboxName
        # print "CheckboxListWidget {}: defaultCheckboxName {}".format(self.groupName, self._defaultCheckboxName)
        
        # if self.groupName == "helmetcolor":
        #     unsetwidgetInfo = self.checkboxWidgetsInfo.get(config.TAG_UNSET_TOKEN, None)
        #     if unsetwidgetInfo: unsetwidgetInfo[0].hide()
                
        # thisGroupWidget.add_checkbox("Unset", u"Unset")
        self.setLayout(self.flayout)
        return
    
    
    def create_checkbox(self, checkbox_name, checkbox_text, checkbox_background_color = None, checkbox_text_color = None, checkbox_background_color_checked = None, checkbox_text_color_checked = None, widget_minWidthInPixels = 36):
        checkboxWidget = QCheckBox(checkbox_text)

        # print "checkbox_background_color {} checkbox_text_color {} checkbox_background_color_checked {} checkbox_text_color_checked {}".format(
        #        checkbox_background_color, checkbox_text_color, checkbox_background_color_checked, checkbox_text_color_checked)
        
        desc = utils.set_qobj_stylesheet(checkboxWidget, 'QCheckBox', checkbox_background_color, checkbox_text_color, checkbox_background_color_checked, checkbox_text_color_checked, min_width_pixels = widget_minWidthInPixels)
        checkboxWidget.setCheckable(True)
        checkboxWidget.clicked.connect(self.onClickedWidget)
        
        return checkboxWidget, desc
  
    def add_popup_button(self, popup_button_name, checkbox_name, checkbox_text, popupbutton_background_color = None, popupbutton_text_color = None, checkbox_background_color = None, checkbox_text_color = None):
        # LOG.info(u"create_popup_button with popup_button_name = {} checkbox_name = {} checkbox_text = {} checkbox_background_color = {} checkbox_text_color = {}".format( \
        #    popup_button_name, checkbox_name, checkbox_text, checkbox_background_color, checkbox_text_color))
        
        popWidgetsInfo = self.popupWidgetsInfo.get(popup_button_name, None)
        if popWidgetsInfo is None:
            pbWidget = QPushButton(popup_button_name)
            # LOG.info(u"popupbutton_background_color {} popupbutton_text_colr {}".format(popupbutton_background_color, popupbutton_text_color))
            utils.set_qobj_stylesheet(pbWidget, 'QPushButton', popupbutton_background_color, popupbutton_text_color, popupbutton_background_color, popupbutton_text_color)
            self.flayout.addWidget(pbWidget)

            if pbWidget is None:
                print "Create QPushButton with name {} failed!".format(popup_button_name)
                return
            mnWidget = QMenu(pbWidget)
            if mnWidget is None:
                print "Create QMenu attached with QPushButton of name {} failed!".format(popup_button_name)
                return
            pbWidget.setMenu(mnWidget)
            actsWidgetList = []   
            actsNameList = [] 
            actsTextList = [] 
            actsColorList = []
            actsStyleSheetList = []
        else:
            pbWidget           = popWidgetsInfo[popupWidgetsInfo_pushButtonWidget_idx]
            mnWidget           = popWidgetsInfo[popupWidgetsInfo_menuWidget_idx]
            actsWidgetList     = popWidgetsInfo[popupWidgetsInfo_actionsWidgetList_idx]
            actsNameList       = popWidgetsInfo[popupWidgetsInfo_actionsNameList_idx]
            actsTextList       = popWidgetsInfo[popupWidgetsInfo_actionsTextList_idx]
            actsColorList      = popWidgetsInfo[popupWidgetsInfo_actionsColorList_idx]
            actsStyleSheetList = popWidgetsInfo[popupWidgetsInfo_actionsWidgetStyleSheet_idx]

        actWidgetAction = QWidgetAction(mnWidget)
        actWidget = QWidget()
        actLayout = QVBoxLayout()
        actLayout.setMargin(2)
        actLayout.setSpacing(2)

        actBtnWidget = QCheckBox(checkbox_text)
        # for these widgets inside QWidgetAction, spacing and margin are controlled by actLayout.setMargin() and actLayout.setSpacing()
        utils.set_qobj_stylesheet(actBtnWidget, 'QCheckBox', checkbox_background_color, checkbox_text_color, checkbox_background_color, checkbox_text_color, margin_pixels = 0, padding_pixels=0)
        actLayout.addWidget(actBtnWidget)
        actWidget.setLayout(actLayout)
        actWidgetAction.setDefaultWidget(actWidget)
        mnWidget.addAction(actWidgetAction)

        desc = None
        actBtnWidget.setCheckable(True)
        actBtnWidget.clicked.connect(self.onClickedWidget)
        actsWidgetList.append(actBtnWidget)
        
        actsNameList.append(checkbox_name)
        actsTextList.append(checkbox_text)
        actsColorList.append(checkbox_background_color)
        actsStyleSheetList.append(desc)

        if popWidgetsInfo is None:
            popWidgetsInfo = [None, None, None, None, None, None, None]

        popWidgetsInfo[popupWidgetsInfo_pushButtonWidget_idx] = pbWidget
        popWidgetsInfo[popupWidgetsInfo_menuWidget_idx] = mnWidget
        popWidgetsInfo[popupWidgetsInfo_actionsWidgetList_idx] = actsWidgetList
        popWidgetsInfo[popupWidgetsInfo_actionsNameList_idx] = actsNameList
        popWidgetsInfo[popupWidgetsInfo_actionsTextList_idx] = actsTextList
        popWidgetsInfo[popupWidgetsInfo_actionsColorList_idx] = actsColorList
        popWidgetsInfo[popupWidgetsInfo_actionsWidgetStyleSheet_idx] = actsStyleSheetList
        
        self.popupWidgetsInfo[popup_button_name] = popWidgetsInfo

        return

    def add_checkbox(self, checkbox_name, checkbox_text, background_color = None, text_color = None, background_color_checked = None, text_color_checked = None, widget_minWidthInPixels = 36):
        checkboxWidget, checkboxStyleSheet = self.create_checkbox(checkbox_name, checkbox_text, background_color, text_color, background_color_checked, text_color_checked, widget_minWidthInPixels = widget_minWidthInPixels)
        self.checkboxWidgetsInfo[checkbox_name] = [checkboxWidget, checkbox_text, background_color_checked, checkboxStyleSheet]
        self.flayout.addWidget(checkboxWidget)
        self.checkbox_group.addButton(checkboxWidget)
        
        return checkboxWidget

    def get_checkbox(self, checkbox_name):
        return self.checkboxWidgetsInfo[checkbox_name]

    # return (names_list, texts_list, displaycolors_list)
    def get_config(self):
        names = []
        texts = []
        displaycolors = []
        for checkboxOption in self.checkGroupDescListTuple:
                thisCheckboxName = checkboxOption[config.METADATA_ATTR_VALUE_TOKEN]
                names.append(thisCheckboxName)
                thisCheckboxText = checkboxOption[config.METADATA_DISPLAYTEXT_TOKEN]
                texts.append(thisCheckboxText)
                thisCheckboxDisplayColor = checkboxOption.get(config.METADATA_DISPLAYCOLOR_TOKEN, None) 
                if thisCheckboxDisplayColor is None:
                    thisCheckboxDisplayColor = checkboxOption.get(config.COLOR_ATTR_RGB_VALUE_TOKEN, None)
                # print u"name = {} text = {} color = {}".format(thisCheckboxName, thisCheckboxText, thisCheckboxDisplayColor)
                displaycolors.append(thisCheckboxDisplayColor)
        return names, texts, displaycolors
                
    # return names_list
    def get_checkboxs_name(self):
        names = []
        for checkboxOption in self.checkGroupDescListTuple:
                thisCheckboxName = checkboxOption[config.METADATA_ATTR_VALUE_TOKEN]
                names.append(thisCheckboxName)
        return names
             
    def onClickedWidget(self):
        widget = self.sender()
        
        if widget.isChecked():
            (num, widgets) = self.get_checked_widgets_number()
            # print "\nget_checked_widgets_number {} maxCheckedNum {} len(_checked_checkbox_widgets) {}".format(num, self._maxCheckedNum, len(self._checked_checkbox_widgets))
            # for index, item in enumerate(self._checked_checkbox_widgets):
            #    print u"before: checked_checkbox_widgets[{}] - {}".format(index, item.text())

            # if current checked widgets exceed allowed max number, set state of oldest N widgets in checked_widgets record list to False and remove it from checked_widgets record list
            if self._maxCheckedNum < num:
                if (self._checked_checkbox_widgets is not None) and (len(self._checked_checkbox_widgets) >= (num - self._maxCheckedNum)):
                    for i in xrange(num - self._maxCheckedNum):
                        # print u"set checked_checkbox_widgets[{}] - {} -- unchecked".format(i, self._checked_checkbox_widgets[i].text())
                        self._checked_checkbox_widgets[i].setChecked(False)
                    del self._checked_checkbox_widgets[0:(num - self._maxCheckedNum)]

            # record current selected widgets to checked_widgets record list
            if widget not in self._checked_checkbox_widgets:
                self._checked_checkbox_widgets.append(widget)
        else:
            # print "some widget is unchecked..."
            if widget in self._checked_checkbox_widgets:
                self._checked_checkbox_widgets.remove(widget)
            # for index, item in enumerate(self._checked_checkbox_widgets):
            #   print u"after: checked_checkbox_widgets[{}] - {}".format(index, item.text())


        # for index, item in enumerate(self._checked_checkbox_widgets):
        #    print u"after: checked_checkbox_widgets[{}] - {}".format(index, item.text())

        self.sendCheckedSignal()
        return
   
    def getCheckedWidgetsOptionInfo(self):
        # print "get getCheckedWidgetsOptionInfo.."
        namesList = self.get_checked_widgets_name()  
        # print "get getCheckedWidgetsOptionInfo... checkGroupDescListTuple = {}".format(self.checkGroupDescListTuple)
        checkedWidgetsOptions = {}
        options = []
        if not namesList:
            return self.groupName, checkedWidgetsOptions
        
        for checkedWidgetName in namesList:
            for option in self.checkGroupDescListTuple:
                if option[config.METADATA_ATTR_VALUE_TOKEN] == checkedWidgetName:
                    options.append(option.copy())

        checkedWidgetsOptions[self.groupName] = options
        # print "get getCheckedWidgetsOptionInfo.. name = {} checkedWidgetsOptions = {}".format(self.groupName, checkedWidgetsOptions)
        return self.groupName, checkedWidgetsOptions

        
    def sendCheckedSignal(self):
        checkedGroupName, checkedWidgetsOptions = self.getCheckedWidgetsOptionInfo()
        # print "group {}: sendCheckedSignal {} ... checkedGroupName {} checkedWidgetsOptions {}...".format( self.groupName, self.checkboxStateChangedSignal, checkedGroupName, checkedWidgetsOptions)
        
        #if checkedWidgetsOptions:
        if True:
            self.checkboxStateChangedSignal.emit(checkedGroupName, checkedWidgetsOptions)
        return


    def get_checked_widgets_number(self):
        number = 0
        widgets = []
        for widgetInfo in self.checkboxWidgetsInfo.values():
            if widgetInfo[0].isChecked():
                number += 1
                widgets.append(widgetInfo[0])
                
        for widgetInfo in self.popupWidgetsInfo.values():
            for actionWidget in widgetInfo[popupWidgetsInfo_actionsWidgetList_idx]:
                if actionWidget.isChecked():
                    number += 1
                    widgets.append(actionWidget)
                   
        return number, widgets   
            
    
    def get_checked_widgets_name(self):
        namesList = []
        for widgetName, widgetInfo in self.checkboxWidgetsInfo.items():
            if widgetInfo[0].isChecked():
                name = widgetName
                namesList.append(name)
                
        for widgetInfo in self.popupWidgetsInfo.values():
            for actionWidget in widgetInfo[popupWidgetsInfo_actionsWidgetList_idx]:
                if actionWidget.isChecked():
                    name = widgetInfo[popupWidgetsInfo_actionsNameList_idx]
                    namesList.append(name)
                                    
        return namesList



    def get_checked_widgets_attrDesc(self):
        descsDict = {}
        for widgetName, widgetInfo in self.checkboxWidgetsInfo.items():
            if widgetInfo[0].isChecked():
                desc = [None, None, None, None, None]
                desc[checkedWidgetsAttrDescList_checkedWidget_idx]           = widgetInfo[0]
                desc[checkedWidgetsAttrDescList_checkedWidgetText_idx]       = widgetInfo[1]
                desc[checkedWidgetsAttrDescList_checkedWidgetColor_idx]      = widgetInfo[2]
                desc[checkedWidgetsAttrDescList_checkedWidgetStyleSheet_idx] = widgetInfo[3]
                descsDict[widgetName] = desc
                
        for widgetInfo in self.popupWidgetsInfo.values():
            for actionWidget in widgetInfo[popupWidgetsInfo_actionsWidgetList_idx]:
                if actionWidget.isChecked():
                    idx = widgetInfo[popupWidgetsInfo_actionsWidgetList_idx].index(actionWidget)
                    desc = [None, None, None, None, None]
                    desc[checkedWidgetsAttrDescList_checkedWidget_idx]           = actionWidget
                    desc[checkedWidgetsAttrDescList_checkedWidgetText_idx]       = widgetInfo[popupWidgetsInfo_actionsTextList_idx][idx]
                    desc[checkedWidgetsAttrDescList_checkedWidgetColor_idx]       = widgetInfo[popupWidgetsInfo_actionsColorList_idx][idx]
                    desc[checkedWidgetsAttrDescList_checkedWidgetStyleSheet_idx] = widgetInfo[popupWidgetsInfo_actionsWidgetStyleSheet_idx]
                    desc[checkedWidgetsAttrDescList_checkedWidgetPopupParentWidget_idx] = widgetInfo[popupWidgetsInfo_pushButtonWidget_idx]
                    widgetName = widgetInfo[popupWidgetsInfo_actionsNameList_idx][idx]
                    descsDict[widgetName] = desc
                                    
        return descsDict
        
        
    def get_widget_name(self, widgetObj):
        for key, val in self.checkboxWidgetsInfo.items():
            if widgetObj is val[0]:  
                return key

        for key, val in self.popupWidgetsInfo.items():
            # print ("[ZXD] CheckboxListWidget.get_checkbox_name ... popupWidgetsInfo.key {} val {} widgetObj {} 'widgetObj is val[0]' = {} 'widgetObj == val[0]' = {}").format(key, val, widgetObj, widgetObj is val[0], widgetObj == val[0] )
            if widgetObj in val[popupWidgetsInfo_actionsWidgetList_idx]:  
                idx = val[popupWidgetsInfo_actionsWidgetList_idx].index(widgetObj)
                return val[popupWidgetsInfo_actionsNameList_idx]
        
        return None    


class AttrAreaWidget(QWidget):
    checkboxStateChangedSignal = pyqtSignal(str, object)


    def setAnnotationScene(self, annotationScene):
        self._scene = annotationScene
        
    def enableAllGroups(self, enabled = True):
        for gn, gw in self.checkboxGroupWidgets.items():
            gw.setEnabled(enabled)
            gw.enableAll(enabled)
                   
    def enableCheckboxGroup(self, checkboxGroupName, enabled = True):
        groupWidget = self.checkboxGroupWidgets.get(checkboxGroupName, None)
        if groupWidget is not None:
                groupWidget.setEnabled(enabled)
                groupWidget.enableAll(enabled)

    def enableCheckbox(self, checkboxGroupName, checkboxName, enabled = True):
        groupWidget = self.checkboxGroupWidgets.get(checkboxGroupName, None)
        if groupWidget is not None:
            groupWidget.enable(checkboxName, enabled)
                        
    # return (names_list, texts_list, displaycolors_list)
    def get_group_config(self, checkboxGroupName):
        names = []
        texts = []
        displaycolors = []
        groupWidget = self.checkboxGroupWidgets.get(checkboxGroupName, None)
        if groupWidget is not None:
            names, texts, displaycolors = groupWidget.get_config()
        
        return names, texts, displaycolors
              
    # return names_list
    def get_group_names(self):
        groupNames = []
        for groupName in self.checkboxGroupWidgets.keys():
            groupNames.append(groupName)
        return groupNames
        

    def setCheckedAllGroups(self, checked = True):
        for groupName, groupWidget in self.checkboxGroupWidgets.items():
            groupWidget.setCheckedAll(checked)
                
                
    def setCheckedGroup(self, checkboxGroupName, checked = True):
        groupWidget = self.checkboxGroupWidgets.get(checkboxGroupName, None)
        if groupWidget is not None:
            groupWidget.setCheckedAll(checked)
 
    def setCheckedCheckbox(self, checkboxGroupName, checkboxName, checked = True):
        # print "checkboxGroupName {} checkboxName {} checked {} ...".format(checkboxGroupName, checkboxName, checked)
        groupWidget = self.checkboxGroupWidgets.get(checkboxGroupName, None)
        # print "checkboxGroupWidgets = {}...".format(self.checkboxGroupWidgets)
        if groupWidget is not None:
            # LOG.info("AttrAreaWidget.setCheckedCheckbox for group {} checked {} ..".format(checkboxGroupName, checked))
            # print ("AttrAreaWidget.setCheckedCheckbox for group {} checked {} ..".format(checkboxGroupName, checked))
            groupWidget.setCheckedCheckbox(checkboxName, checked)
            
                               
    def setCheckedCheckboxs(self, checkboxGroupName, checkboxNamesList, checked = True):
        if checkboxNamesList is None:
            return
        groupWidget = self.checkboxGroupWidgets.get(checkboxGroupName, None)
        if groupWidget is not None:
            # LOG.info(u"{} AttrAreaWidget.setCheckedCheckbox for group {} box {} checked {} ..".format(self.groupName, checkboxGroupName, checkboxNamesList, checked))
            groupWidget.setCheckedCheckboxs(checkboxNamesList, checked)

    def sendCheckedSignal(self, checkboxGroupName):
        groupWidget = self.checkboxGroupWidgets.get(checkboxGroupName, None)
        if groupWidget is not None:
            groupWidget.sendCheckedSignal()
       
    def getCheckedWidgetsOptionInfo(self, checkboxGroupName):
        groupWidget = self.checkboxGroupWidgets.get(checkboxGroupName, None)
        if groupWidget is not None:
            return groupWidget.getCheckedWidgetsOptionInfo()
        return None, None
       
       
    def setOptionStateChangedSignalSlot(self, checkboxStateChangedSignalSlot):
        if checkboxStateChangedSignalSlot is not None:
            # print u"pannel {}: checkboxStateChangedSignal{} checkboxStateChangedSignalSlot {} is connected...".format(self.idName, self.checkboxStateChangedSignal, checkboxStateChangedSignalSlot)
            self.checkboxStateChangedSignal.connect(checkboxStateChangedSignalSlot)

    def hideGroup(self, checkboxGroupName):
        groupWidget = self.checkboxGroupWidgets.get(checkboxGroupName, None)
        if groupWidget is not None:
            return groupWidget.hide()
            
    def __init__(self, property = None, idName = None, displayName = None, parent=None):
        QWidget.__init__(self, parent)

        self.hotkeys = []
        self.displayName = displayName
        self.idName = idName
        
        self.vlayout = MyVBoxLayout() #QVBoxLayout()
        self.vlayout.setAlignment(Qt.AlignTop)
        self.vlayout.setSpacing(4)
        self.vlayout.setMargin(4)
        #self.vlayout.setContentsMargins(0, 0, 0, 44)
        
        # LOG.info("AttrAreaWidget constructor : property {} ...".format(property))
        self.numGroups = len(property) if property is not None else 0
  
        self.checkboxGroupsDescDict = {}
        self.checkboxGroupWidgets = {}
        
        for i in xrange(self.numGroups):
            thisGroupProperty = property[i]                    # thisGroupProperty is a dict
            thisGroupName = thisGroupProperty.get('name')      # thisGroupName is a string
            thisGroupOption = thisGroupProperty.get('option')  # thisGroupOption is a tuple of dicts. each dict describes a checkbox
            thisGroupText = thisGroupProperty.get('displaytext')
            
            isExclusive = False if thisGroupName in config.NON_EXCLUSIVE_ATTRS_TAG_LIST else True
            if thisGroupName == config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN:
                checkboxWidgetMinWidthInPixels = 52
            else:
                checkboxWidgetMinWidthInPixels = 38
            
            if thisGroupName == config.ANNOTATION_UPPER_COLOR_TOKEN:
                thisGroup_maxCheckedNum = config.MAX_UPPER_COLOR_NUMBER
                thisGroup_maxSeperateWidgetNum = config.GUI_MAX_SEPERATE_UPPER_COLOR_WIDGET_NUMBER
            elif thisGroupName == config.ANNOTATION_LOWER_COLOR_TOKEN:
                thisGroup_maxCheckedNum = config.MAX_LOWER_COLOR_NUMBER
                thisGroup_maxSeperateWidgetNum = config.GUI_MAX_SEPERATE_LOWER_COLOR_WIDGET_NUMBER
            elif thisGroupName == config.ANNOTATION_VEHICLE_COLOR_TOKEN:
                thisGroup_maxCheckedNum = config.MAX_VEHICLE_COLOR_NUMBER
                thisGroup_maxSeperateWidgetNum = config.GUI_MAX_SEPERATE_VEHICLE_COLOR_WIDGET_NUMBER
            else:
                thisGroup_maxCheckedNum = config.MAX_CHECKED_OPTIONS_NUMBER
                thisGroup_maxSeperateWidgetNum = config.MAX_OPTIONS_NUMBER
                
            thisGroupWidget = CheckboxListWidget(thisGroupName, thisGroupText, isExclusive, thisGroupOption, self.checkboxStateChangedSignal, thisGroup_maxCheckedNum, thisGroup_maxSeperateWidgetNum)

            # add checkbox record to this checkbox group record    
            thisGroupCheckboxs = {}
            for checkboxOption in thisGroupOption:
                thisCheckboxName = checkboxOption[config.METADATA_ATTR_VALUE_TOKEN]
                thisCheckboxProperty = checkboxOption.copy()
                thisGroupCheckboxs[thisCheckboxName] = thisCheckboxProperty 

            self.vlayout.addWidget(thisGroupWidget)
            
            
            self.checkboxGroupsDescDict[thisGroupName] = thisGroupCheckboxs  # add this checkbox group record to checkbox groups recrod
            self.checkboxGroupWidgets[thisGroupName] = thisGroupWidget

        # LOG.info("checkboxGroupWidgets = {} checkboxGroupsDescDict = {}".format(self.checkboxGroupWidgets, self.checkboxGroupsDescDict)
        
        
        self.vlayout.addStretch(1)
        self.setLayout(self.vlayout)
        return

    def stateHasChanged(self, checkedWidgetsAttrDescDict):
        # LOG.info("call AttrAreaWidget.stateHasChanged({})".format(checkedWidgetsAttrDescDict))
        return


    def get_checked_widgets_name(self, group_name):
        widget = self.checkboxGroupWidgets.get(str(group_name), None)
        # LOG.info("AttrAreaWidget.get_checked_widgets_name ... widget = {}".format(widget))
        checkedWidgetsNameList = widget.get_checked_widgets_name() if widget is not None else None
        # LOG.info("AttrAreaWidget.get_checked_widgets_name ... checkedWidget = {}".format(checkedWidget))
        return checkedWidgetsNameList


    def add_hotkey(self, choice, name, hotkey):
        self.hotkeys.append((choice, name, hotkey))



    def get_checked_widgets_attrDesc(self):
        descsDict = {}
        for widgetName, widgetInfo in self.checkboxWidgetsInfo.items():
            if widgetInfo[0].isChecked():
                desc = [None, None, None, None, None]
                desc[checkedWidgetsAttrDescList_checkedWidget_idx]           = widgetInfo[0]
                desc[checkedWidgetsAttrDescList_checkedWidgetText_idx]       = widgetInfo[1]
                desc[checkedWidgetsAttrDescList_checkedWidgetColor_idx]      = widgetInfo[2]
                desc[checkedWidgetsAttrDescList_checkedWidgetStyleSheet_idx] = widgetInfo[3]
                descsDict[widgetName] = desc
                
        for widgetInfo in self.popupWidgetsInfo.values():
            for actionWidget in widgetInfo[popupWidgetsInfo_actionsWidgetList_idx]:
                if actionWidget.isChecked():
                    idx = widgetInfo[popupWidgetsInfo_actionsWidgetList_idx].index(actionWidget)
                    desc = [None, None, None, None, None]
                    desc[checkedWidgetsAttrDescList_checkedWidget_idx]           = actionWidget
                    desc[checkedWidgetsAttrDescList_checkedWidgetText_idx]       = widgetInfo[popupWidgetsInfo_actionsTextList_idx][idx]
                    desc[checkedWidgetsAttrDescList_checkedWidgetColor_idx]       = widgetInfo[popupWidgetsInfo_actionsColorList_idx][idx]
                    desc[checkedWidgetsAttrDescList_checkedWidgetStyleSheet_idx] = widgetInfo[popupWidgetsInfo_actionsWidgetStyleSheet_idx]
                    desc[checkedWidgetsAttrDescList_checkedWidgetPopupParentWidget_idx] = widgetInfo[popupWidgetsInfo_pushButtonWidget_idx]
                    widgetName = widgetInfo[popupWidgetsInfo_actionsNameList_idx][idx]
                    descsDict[widgetName] = desc
                                    
        return descsDict
        
        
    def startEditMode(self, model_items):
        return

    # def exitInsertMode(self):
    #     widgetsNameList = self.group1_checkbox_list.get_checked_widgets_name()
    #     if widgetsNameList is not None:
    #         for .....
    #         self.group1_checkbox_list.toggleChecked(checkbox)


def main():
    # from conf import config
    # config.update("example_config.py")

    app = QApplication(sys.argv)
    ba1 = AttrAreaWidget(None, config.BUTTONGROUP4, "BUTTONGROUP4")
    ba1.show()

    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())


