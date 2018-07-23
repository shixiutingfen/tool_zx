# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

import time
import math
import logging
from PyQt4.QtCore import pyqtSignal, QSize, Qt, QSettings, QVariant, QPoint
from sloth.annotations.model import GET_ANNOTATION
from PyQt4.QtGui import QWidget, QGroupBox, QVBoxLayout, QPushButton, QScrollArea, QLineEdit, QDoubleValidator, QIntValidator, QShortcut, QKeySequence, QMessageBox
from sloth.core.exceptions import ImproperlyConfigured
from sloth.annotations.model import AnnotationModelItem
from sloth.gui.floatinglayout import FloatingLayout
from sloth.gui.utils import MyVBoxLayout
from sloth.utils.bind import bind
from sloth.conf import default_config
from sloth.conf import config
from sloth.gui import utils, annotationscene, attrArea
from attrArea import CheckboxListWidget
from sloth.annotations import model

LOG = logging.getLogger(config.LOG_FILE_NAME)

class AttachedCheckboxGroupWidget(CheckboxListWidget):
    def __init__(self, hostName, checkGroupName, checkboxGroupText, isExclusive, checkboxGroupDescListTuple, checkboxStateChangedSignal, thisGroup_maxCheckedNum = 100, thisGroup_maxSeperateWidgetNum = 100, parent = None):
        CheckboxListWidget.__init__(self, checkGroupName, checkboxGroupText, isExclusive, checkboxGroupDescListTuple, checkboxStateChangedSignal, thisGroup_maxCheckedNum, thisGroup_maxSeperateWidgetNum, parent)
        self._hostName = hostName
        return
        
    def sendCheckedSignal(self):
        checkedWidgetsAttrDesc = self.get_checked_widgets_attrDesc()
        allCheckboxsNameList = self.get_checkboxs_name()
        
        self.checkboxStateChangedSignal.emit(self._hostName, [checkedWidgetsAttrDesc, allCheckboxsNameList])
        return        
        
class PropertyEditor(QWidget):
    # Signals
    insertionModeStarted       = pyqtSignal(str, str, str)
    insertionModeEnded         = pyqtSignal()
    insertionPropertiesChanged = pyqtSignal(object)
    editPropertiesChanged      = pyqtSignal(object)
    checkboxStateChangedSignal   = pyqtSignal(str, object)
    _optionsCheckboxStateChangedSignal    = pyqtSignal(str, object)
    def setAnnotationScene(self, annotationScene):
        self._scene = annotationScene

    def setOptionStateChangedSignalSlot(self, checkboxStateChangedSignalSlot):
        if checkboxStateChangedSignalSlot is not None:
            self.checkboxStateChangedSignal.connect(checkboxStateChangedSignalSlot)
        self._optionsCheckboxStateChangedSignal.connect(self.onInserterButtonOptionChanged)

    # set enable status for the checkbox group which is attached to inserterButton 
    def enableCheckboxGroup(self, inserterButtonName, enabled = True):
        widgetsInfo = self._widgets_dict.get(inserterButtonName, None)
        if not widgetsInfo:  return
        if widgetsInfo[1]:
            # this button has an attachedCheckboxGroup
            attachedCheckboxGroupWidget = widgetsInfo[1]
            attachedCheckboxGroupWidget.enableAll(enabled)
            
      
 
    # set check status for one specific checkbox which is attached to inserterButton
    def setCheckedCheckbox(self, inserterButtonName, checkBoxName, checked = True):
        widgetsInfo = self._widgets_dict.get(inserterButtonName, None)
        # print "inserterButtonName {} _widgets_dict {} checkBoxName {} checked {} ...".format(inserterButtonName, self._widgets_dict, checkBoxName, checked)
        if not widgetsInfo:  return
        if widgetsInfo[1]:
            # this button has an attachedCheckboxGroup
            attachedCheckboxGroupWidget = widgetsInfo[1]
            attachedCheckboxGroupWidget.setCheckedCheckbox(checkBoxName, checked)        

    # set check status for some specific checkboxs which are attached to inserterButton
    def setCheckedCheckboxs(self, inserterButtonName, checkBoxNamesList, checked = True):
        widgetsInfo = self._widgets_dict.get(inserterButtonName, None)
        if not widgetsInfo:  return
        if widgetsInfo[1]:
            # this button has an attachedCheckboxGroup
            attachedCheckboxGroupWidget = widgetsInfo[1]
            attachedCheckboxGroupWidget.setCheckedCheckboxs(checkBoxNamesList, checked) 
                
    # get names list of all checkboxs in the checkbox group which is attached to inserterButton 
    def getCheckboxsName(self, inserterButtonName, enabled = True):
        widgetsInfo = self._widgets_dict.get(inserterButtonName, None)
        if not widgetsInfo:  return
        if widgetsInfo[1]:
            # this button has an attachedCheckboxGroup
            attachedCheckboxGroupWidget = widgetsInfo[1]
            return attachedCheckboxGroupWidget.get_checkboxs_name()
        return None
                                 
    def __init__(self, config, idName, displayName, groupBoxName, parent = None):
        QWidget.__init__(self, parent)
        self._inserters_modelitems                 = {}     # dict. { inserter_class_name : AnnotationModelItem, ...}. Note that, inserter_class_name is not always equal to inserter_button_name, for those buttons with attached options.
        self._inserters_guiitems                   = {}     # dict. { inserter_class_name : (inserter_creator_method, inserted_item_creator_method) } 
        self._idName                               = idName
        self._groupBoxName                         = groupBoxName
        self._displayName                          = displayName
        self._scene                                = None
        self._current_toinsert_inserterClassName   = None 
        self._current_is_insert_mode               = False
        self._widgets_dict                         = {}    # dict. { inserter_button_name :[buttonWidget, buttonAttachedOptionsWidget, buttonName], ....}
        
        self._setupGUI(self._groupBoxName)

        # Add label classes from config
        for buttonConfig in config:  self.addButton(buttonConfig)
		
        # print "self._inserters_guiitems = {}".format(self._inserters_guiitems)

    def onModelChanged(self, new_model):
        pass


    def addButton(self, buttonConfig):
        # LOG.info("addLabelClass with buttonConfig {} ...".format(buttonConfig))
        # Check label configuration
        if 'attributes' not in buttonConfig:
            raise ImproperlyConfigured("Label with no 'attributes' dict found")
        
        inserter_creator_method = buttonConfig[ 'inserter' ] 
        inserted_item_creator_method = buttonConfig[ 'item' ]
        
        attrs = buttonConfig['attributes']
        # LOG.info("buttonConfig['attributes'] {} type {} ...".format(buttonConfig['attributes'], type(buttonConfig['attributes'])))
        if config.METADATA_LABELCLASS_TOKEN not in attrs:
            raise ImproperlyConfigured("Labels must have an attribute config.METADATA_LABELCLASS_TOKEN")
        label_class = attrs[config.METADATA_LABELCLASS_TOKEN]
        # LOG.info("buttonConfig['attributes'][config.METADATA_LABELCLASS_TOKEN] {} type {} ...".format(attrs[config.METADATA_LABELCLASS_TOKEN], type(attrs[config.METADATA_LABELCLASS_TOKEN])))
        if label_class in self._inserters_modelitems:
            raise ImproperlyConfigured("Label with class '%s' defined more than once" % label_class)

      
        # Add INSERTER button
        displaytext = attrs['displaytext']
        buttonName = label_class
        button = QPushButton(displaytext, self)

        optionInfo = attrs.get('optioninfo', None)
        # print "button {}: option {}".format(buttonName, optionInfo)
        buttonOptionsWidget = None
        buttonDisplayColor = None
        tmp = [ o.get(default_config.METADATA_DISPLAYCOLOR_TOKEN, None) for o in optionInfo['option'] if o.get(config.METADATA_IS_DEFAULT_TOKEN, False) ] [0] if optionInfo else None
        buttonDisplayColor = tmp if tmp else optionInfo['option'][0].get(default_config.METADATA_DISPLAYCOLOR_TOKEN, None) if optionInfo  else attrs.get(default_config.METADATA_DISPLAYCOLOR_TOKEN, None)

        # LOG.info(u"buttonConfig['attributes'] = {}, displaytext = {}, displayColor = {}".format(attrs, displaytext, buttonDisplayColor))
        
        # ==== zx add @ 20161114 to display button with color configured by user ====
        txtColor = None
        if buttonDisplayColor is not None:
            qtColor, hexColor = utils.getColorDesc(buttonDisplayColor)
            rgba = utils.hexColorStrToRGBA(hexColor)
            distance = math.sqrt((rgba[0]-255)**2 + (rgba[1]-255)**2 + (rgba[2]-255)**2)            
            txtColor = '#000000' if distance > config.GUI_COLOR_TAG_TEXT_BLACKWHITE_TOGGLE_THRESHOLD else '#ffffff'
            buttonDisplayColor = hexColor[0:8]
            # LOG.info(u"buttonDisplayColor = {} txtColor = {}, qtColor = {} hexColor = {}".format(buttonDisplayColor, txtColor, qtColor, hexColor ))
            # print (u"buttonDisplayColor = {} txtColor = {}, qtColor = {} hexColor = {}".format(buttonDisplayColor, txtColor, qtColor, hexColor ))
        
        # print "button {} buttonDisplayColor {} ...".format(buttonName, buttonDisplayColor)
        utils.set_qobj_stylesheet(button, 'QPushButton', widgetBackgroundColor = None, widgetTextColor = None, widgetBackgroundColorWhenChecked = buttonDisplayColor, widgetTextColorWhenChecked = txtColor)
        # ========================== zx add end ============================

        button.clicked.connect(bind(self.onClassButtonPressed, label_class))
        # Add hotkey
        if 'hotkey' in buttonConfig:
            hotkey = QShortcut(QKeySequence(buttonConfig['hotkey']), self)
            hotkey.activated.connect(button.click)
            self._class_shortcuts[label_class] = hotkey
            # print "{} is set hotkey {} {}".format(label_class, buttonConfig['hotkey'], hotkey)

        if optionInfo:
            optionListName = optionInfo['name']
            optionListText = optionInfo['displaytext']
            option         = optionInfo['option']
            buttonOptionsWidget = AttachedCheckboxGroupWidget(buttonName, optionListName, optionListText, True, option, self._optionsCheckboxStateChangedSignal, parent = None)

            isDefaultOption = False
            for o in option:
                new_class = o.get('tag', None)
                if new_class:
                    # Add prototype mdoelItem for insertion                    
                    mi = {config.METADATA_LABELCLASS_TOKEN: new_class}       
                    mi['displaytext'] = o.get('displaytext', new_class)  

                    self._inserters_modelitems[new_class] = AnnotationModelItem(mi)    
                    self._inserters_guiitems[new_class] = (inserter_creator_method, inserted_item_creator_method)
                    # print "addButton.....self._inserters_guiitems[{}] = {}".format(new_class, (inserter_creator_method, inserted_item_creator_method))
                    for key, val in o.iteritems():
                        if key != 'tag':
                            self._inserters_modelitems[new_class][key] = val 
                    
        else:
            attrs = buttonConfig['attributes']
        
            # Add prototype mdoelItem for insertion
            mi = {config.METADATA_LABELCLASS_TOKEN: label_class}
            mi['displaytext'] = attrs.get('displaytext', label_class)
            
            self._inserters_modelitems[label_class] = AnnotationModelItem(mi)
            self._inserters_guiitems[label_class] = (inserter_creator_method, inserted_item_creator_method)
            
            # update their values
            for key, val in attrs.iteritems():
                self._inserters_modelitems[label_class][key] = val
                # LOG.info("self._inserters_modelitems[{}][{}] = {}".format(label_class, key, val))

        self._widgets_dict[label_class] = [ button, buttonOptionsWidget ]
        # print "self._widgets_dict [ {} ] = {}".format(label_class, button)

        button.setCheckable(True)

        utils.set_qobj_stylesheet(self._widgets_dict[label_class][0], 'QPushButton', widgetBackgroundColor = None, widgetTextColor = None, widgetBackgroundColorWhenChecked = buttonDisplayColor, widgetTextColorWhenChecked = txtColor)

        
        if buttonOptionsWidget:
            # self._layout.addWidget(button)
            self._inserterButtonGroup_layout.addWidget(button)
            self._layout.addWidget(buttonOptionsWidget)
        else:
            self._inserterButtonGroup_layout.addWidget(button)
        

 
    def onClassButtonPressed(self, pressedButtonName):
        # print "onClassButtonPressed ... button {} isChecked !".format(pressedButtonName)
        inserterClassName = pressedButtonName

        if pressedButtonName not in  self._widgets_dict.keys():
            # check whether passed-in pressedButtonName argument is an checkbox option name
            for kk, vv in self._widgets_dict.iteritems():
                buttonOptionsWidget = vv[1] if vv else None
                if buttonOptionsWidget:
                    optionsName = buttonOptionsWidget.get_checkboxs_name()
                    if pressedButtonName in optionsName:
                        pressedButtonName = kk
                        # print "pressedButtonName ============ {}".format(kk)

        if self._widgets_dict[pressedButtonName][0].isChecked():
            if not self._scene._image_item:
                self._widgets_dict[pressedButtonName][0].setChecked(False)
                return
                
            checkedOption = None    
            if self._widgets_dict[pressedButtonName][1]:
                buttonOptionsWidget = self._widgets_dict[pressedButtonName][1]
                checkedOptionsNameList = buttonOptionsWidget.get_checked_widgets_name()
                if not checkedOptionsNameList:
                    checkedOptionsNameList = [buttonOptionsWidget._defaultCheckboxName]
                    buttonOptionsWidget.setCheckedCheckbox(buttonOptionsWidget._defaultCheckboxName)

                buttonOptionsWidget.enableAll()
                checkedOptionName = checkedOptionsNameList[0]
                
                orgClsNames = [i for i in buttonOptionsWidget.get_checkboxs_name() if i in self._inserters_modelitems.keys() ]
                if (not orgClsNames) :
                    raise RuntimeError("There are no or more than one inserters")
                inserterClassName = checkedOptionName

            if ((not self._scene._labeltool._enableAutoConnectLabelMode) and (self._scene._selectedDisplayItemsList is not None) and (len(self._scene._selectedDisplayItemsList) == 1)):
                parentModelItem = self._scene._selectedDisplayItemsList[0][annotationscene.SELECTED_DISPLAYED_ITEMS_LIST_MODELITEM_INDEX]
                clsNameOfChild = inserterClassName
                if ( (clsNameOfChild == config.ANNOTATION_PERSONBIKE_TOKEN) or (clsNameOfChild == config.ANNOTATION_PEDESTRAIN_TOKEN)  or (clsNameOfChild == config.ANNOTATION_VEHICLE_TOKEN) ):
                    self._scene._selectedDisplayItemsList = [ ]
                    parentModelItem = None
        		
            elif (self._scene._sceneViewMode == config.OBJ_VIEW_MODE) and (self._scene._objViewModeTopModelItem is not None):
                parentModelItem = self._scene._objViewModeTopModelItem
            else :
                parentModelItem = None
                
            LOG.info("onClassButtonPressed ... self._scene._labeltool._enableAutoConnectLabelMode = {} parentModelItem = {}".format(self._scene._labeltool._enableAutoConnectLabelMode, parentModelItem))    
            if not self._scene._labeltool._enableAutoConnectLabelMode:
                
                clsNameOfChild = inserterClassName
                isValid, rectBoundary = self._scene.checkModelItemValidity(clsNameOfChild, None, parentModelItem, self._scene._image_item, enablePopupMsgBox = True, enableEmitStatusMsg = False, enableCountingThisModelItem = True)

                if not isValid: 
                    LOG.info("enter hhhhhhhhhhhhhhh....")
                    
                    # --------------------------------------
                    # added by zx @ 2017-02-08
                    # to exit all inserters among all pannels
                    # --------------------------------------
                    for i in self._scene._labeltool.propertyeditors():
                        if i:
                            i.setCheckedAll(False)
                    # self._scene._labeltool.exitInsertMode()
                    self._scene.deselectAllItems()
                    # --------------------------------------
                            
                    return
                         
            LOG.info("onClassButtonPressed ... call startInsertionMode...") 
                 
            self.startInsertionMode(pressedButtonName, inserterClassName)
            
        else:
        
            LOG.info("onClassButtonPressed ... call endInsertionMode...")
            self.endInsertionMode()

        return
        
    def startInsertionMode(self, pressedButtonName, inserterClassName):
        self.endInsertionMode(False)
        LOG.info("Starting insertion mode for {} .. self._inserters_modelitems[{}]={} ".format(inserterClassName, inserterClassName, self._inserters_modelitems[inserterClassName]))
        
        for lc, buttonAndOption in self._widgets_dict.items():
            buttonAndOption[0].setChecked(lc == pressedButtonName)
            if buttonAndOption[1]:
                # print ("startInsertionMode .. setchecked for {} option {} enabled = {} ".format(lc, buttonAndOption[1], (lc == pressedButtonName)))
                buttonAndOption[1].enableAll(lc == pressedButtonName)
               
            LOG.info("startInsertionMode .. setchecked for {} button checked = {} ".format(lc, lc == inserterClassName))
            # print ("startInsertionMode .. setchecked for {} button {} checked = {} ".format(lc, buttonAndOption[0], lc == inserterClassName))

        self._current_toinsert_inserterClassName = inserterClassName
        # print "==== startInsertionMode set _current_is_insert_mode False ..."
        self._current_is_insert_mode = True
        
        LOG.info(u"startInsertionMode .. emit insertionModeStarted(pannel = {}, inserter = {})... ".format(self._idName, inserterClassName))
        
        self.insertionModeStarted.emit(self._idName, inserterClassName, inserterClassName)

            
    def endInsertionMode(self, uncheck_buttons=True):
        if uncheck_buttons:
            self.setCheckedAll(False)
            
        LOG.info(u"endInsertionMode... PropertyEditor {} endInsertionMode(uncheck_buttons = {})".format(self._displayName, uncheck_buttons))
        # print (u"endInsertionMode... PropertyEditor {} endInsertionMode(uncheck_buttons = {})".format(self._displayName, uncheck_buttons))
        self._current_is_insert_mode = False    
        self.insertionModeEnded.emit()
            
    def enableAll(self, enabled = True):
        for v, buttonAndOption in self._widgets_dict.items():
            buttonAndOption[0].setEnabled(enabled)
                
    def setCheckedAll(self, checked = True):
        for v, buttonAndOption in self._widgets_dict.items():
            buttonAndOption[0].setChecked(checked)
        
 
    def getChecked(self):
        buttonname = None
        for buttonName, buttonWidgets in self._widgets_dict.iteritems():
            if buttonWidgets[0].isChecked():
                return buttonName
        return buttonname

            
    def setChecked(self, buttonName, checked = True):
        buttonWidget = self._widgets_dict.get(buttonName, None)
        if buttonWidget is not None:
            buttonWidget[0].setChecked(checked)

    def enable(self, buttonName, enabled = True):
        buttonWidget = self._widgets_dict.get(buttonName, None)
        if buttonWidget is not None:
            buttonWidget[0].setEnabled(enabled)
                        
    def markEditButtons(self, buttonNamesList):
        for lc, buttonAndOption in self._widgets_dict.items():
            # buttonAndOption[0].setFlat(lc not in buttonNamesList)
            buttonAndOption[0].setChecked(lc in buttonNamesList)

    def updateCurrentInserter(self, inserterClassName):
        self._current_toinsert_inserterClassName = inserterClassName
        return
    
    def isInsertingMode(self):
        return self._current_is_insert_mode

 
    def currentToInsertItemProperty(self):
        return self._inserters_modelitems.get(self._current_toinsert_inserterClassName, {}) if self._current_toinsert_inserterClassName else {}
        
    # return [inserter0ClassName, inserter1ClassName, ...]
    def getSupportedInserters(self):
        return self._inserters_modelitems.keys()

    
    def startEditMode(self, model_items):
        # If we're in insertion mode, ignore empty edit requests
        if self._current_is_insert_mode and len(model_items) == 0:
            return

        self.endInsertionMode()
        LOG.info("Starting edit mode for model_items: {} ".format( model_items ))
        self._current_toinsert_inserterClassName = None
        # print "==== startEditMode set _current_is_insert_mode False ..."
        self._current_is_insert_mode = False
        
        labelClasses = set([item[config.METADATA_LABELCLASS_TOKEN] for item in model_items if config.METADATA_LABELCLASS_TOKEN in item])
        self.markEditButtons(labelClasses)
        

    def _setupGUI(self, _groupBoxName):
        self._widgets_dict = {}
        self._class_shortcuts = {}

        # Label class buttons
        qss = "QGroupBox::title {subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; color : red; font-weight:bold; }"
        self._inserterButtonGroupbox = QGroupBox(_groupBoxName, self)
        self._inserterButtonGroupbox.setStyleSheet(qss)
        self._inserterButtonGroup_layout = FloatingLayout()
        self._inserterButtonGroupbox.setLayout(self._inserterButtonGroup_layout)

        # Global widget
        self._layout = MyVBoxLayout()
        self.setLayout(self._layout)
        self._layout.addWidget(self._inserterButtonGroupbox, 0)
        self._layout.addStretch(1)



    def onInserterButtonOptionChanged(self, _inserterButtonName, checkboxsInfo):
        # print "onInserterButtonOptionChanged {}: inserterButton {} checkboxinfo {}".format(self._idName, _inserterButtonName, checkboxsInfo)
        if not checkboxsInfo:
            return
        if len(checkboxsInfo) != 2:
            return

        inserterButtonName = str(_inserterButtonName)
        
        checkedWidgetsAttrDescDict = checkboxsInfo[0]
        allCheckboxsNameList = checkboxsInfo[1]

        if len(checkedWidgetsAttrDescDict) != 1:
            return

        checkedOptionName = checkedWidgetsAttrDescDict.keys()[0]
        
        if (self._current_toinsert_inserterClassName == checkedOptionName): return
        
        checkedOptionDisplayText  = checkedWidgetsAttrDescDict.values()[0][attrArea.checkedWidgetsAttrDescList_checkedWidgetText_idx]
        checkedOptionDisplayColor = checkedWidgetsAttrDescDict.values()[0][attrArea.checkedWidgetsAttrDescList_checkedWidgetColor_idx]

        # change inserter button displaycolor
        # print "--- self._current_is_insert_mode = {} self._widgets_dict[{}][0].is_checked() = {} ...".format(self._current_is_insert_mode, inserterButtonName, self._widgets_dict[inserterButtonName][0].isChecked())
        utils.set_qobj_stylesheet(self._widgets_dict[inserterButtonName][0], 'QPushButton', widgetBackgroundColor = None, widgetTextColor = None, widgetBackgroundColorWhenChecked = checkedOptionDisplayColor, widgetTextColorWhenChecked = None)

        if  not self._current_is_insert_mode or self._scene._sceneViewMode == config.OBJ_VIEW_MODE:
            parentModelItem = None
            
            if self._scene._sceneViewMode == config.OBJ_VIEW_MODE:
                # print "_sceneViewMode = {} _objViewModeTopModelItem = {}".format(self._scene._sceneViewMode, self._scene._objViewModeTopModelItem)
                parentModelItem = self._scene._objViewModeTopModelItem

            if not parentModelItem:
                # get current scene's parent modelitem
            	if len(self._scene._selectedDisplayItemsList) > 0:
                    parentModelItem = self._scene._selectedDisplayItemsList[0][annotationscene.SELECTED_DISPLAYED_ITEMS_LIST_MODELITEM_INDEX]
                    # print "_selectedDisplayItemsList = {}".format(self._scene._selectedDisplayItemsList)
 
            if not parentModelItem:
                parentModelItem = self._scene._labeltool._current_image

            # print ("checkedOptionName = {} parentModelItem = {}".format(checkedOptionName, GET_ANNOTATION(parentModelItem)))
            # print ("allCheckboxsNameList = {}".format((allCheckboxsNameList)))

            # find all modelItems which has class which in is the option list of changed inserter option but not has not that class of option
            foundNum = 0
            foundListList = []
            for a in allCheckboxsNameList:
                foundList = model.findModelItemsWithSpecificClassNameFromRoot(a, parentModelItem, 5)
                # print "find {} => {}".format(a, foundList)
                foundNum += len(foundList) # if a != checkedOptionName else 0
                maxNum = 1
                if foundNum > maxNum:
                    print "Error: there are {} items of {} in current image! We can only modify at least {} item once!".format(foundNum, allCheckboxsNameList, maxNum)
                    foundListList = []
                    break
                if a != checkedOptionName:
                    foundListList += foundList

            # print ("foundListList = {}".format((foundListList)))
            # update found modelitems' class field to current selected option
            if foundListList:
                for found in foundListList:
                    if not found: continue
                    modelItem = found[0]
                    iterativeLevelNum = found[1]
                    # print "ModelItem is changed from {} => {}!".format(modelItem.get_label_name(), checkedOptionName)
                    modelItem.update({'class' : checkedOptionName}, needEmitDatachanged = True)
                    sceneItem = self._scene.modelItem_to_baseItem(modelItem)

                    # print u"checkedOptionDisplayText = {} checkedOptionDisplayColor = {}".format(checkedOptionDisplayText, checkedOptionDisplayColor)
                    sceneItem.updateInfo(checkedOptionDisplayText, checkedOptionDisplayColor)

                    # newModelItem = copy.deepcopy(oldModelItem)
                    # self._scene.deleteItems(self, [oldModelItem], recursiuve=True)
        else:
        
            # switch to new inserter as per current selected inserter button type
            # print "---------------- _current_is_insert_mode = {} ...".format(self._current_is_insert_mode)
            # print "call onInsertionModeStarted with {} {}...".format(checkedOptionName, inserterButtonName)
            self.updateCurrentInserter(checkedOptionName)
            self._scene.onInsertionModeStarted(self._idName, checkedOptionName, inserterButtonName)

        return
                   
    def onInsertionModeStarted(self, _classNameToInsert, _buttonNameOfInserter):
        buttonNameOfInserter = str(_buttonNameOfInserter)
        self.setChecked(buttonNameOfInserter, True) 
        self._current_is_insert_mode = True
        self.updateCurrentInserter(str(_classNameToInsert))
        return
