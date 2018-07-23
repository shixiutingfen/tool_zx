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

LOG = logging.getLogger(config.LOG_FILE_NAME)


class ButtonListWidget(QGroupBox):
    groupSelectionChanged = pyqtSignal(str, str)
    

    def __init__(self, name, parent=None):
        QGroupBox.__init__(self, name, parent)
        self.setLayout(FloatingLayout())

        self.name = name
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(False)
        self.buttonWidgets = {}

    def create_button(self, button_name, background_color = None, text_colr = None):
        buttonWidget = QPushButton(button_name)
        
        desc1, desc2 = None, None
        if background_color is not None and background_color != "":
            desc1 = "background-color: {}".format(background_color)
            
        if text_colr is not None and text_colr != "":
            desc2 = "color: {}".format(text_colr)

        font  = "font: 14px; "
        fontPressed  = "bold font: 14px; "
        desc  = desc1
        desc += "; " if desc1 is not None and desc2 is not None else ""
        desc += desc2 if desc2 is not None else ""
         
        if desc != "":
            # LOG.info("QPushButton {{ {} {} }}; QPushButton:pressed {{ {} {} }};".format(fontPressed, desc, fontPressed, desc))
            buttonWidget.setStyleSheet('QPushButton {{ {} {} }}; QPushButton:pressed {{ {} {} }};'.format(fontPressed, desc, fontPressed, desc))
        	
        # buttonWidget.setFlat(True)
        buttonWidget.setCheckable(True)
        buttonWidget.clicked.connect(self.clickedButton)
        
        return buttonWidget, desc



    def add_button(self, button_name, background_color = None, text_colr = None):
        buttonWidget, buttonStyleSheet = self.create_button(button_name, background_color, text_colr)
        self.buttonWidgets[button_name] = [buttonWidget, buttonStyleSheet]
        self.layout().addWidget(buttonWidget)
        self.button_group.addButton(buttonWidget)
        return buttonWidget


    def get_button(self, button_name):
        return self.buttonWidgets[button_name]

    def toggleChecked(self, button_name, apply=True):
        selection = None

        for button in self.button_group.buttons():
            if button.text() != button_name:
                button.setChecked(False)
            else:
                if apply:
                    button.setChecked(not button.isChecked())
                if button.isChecked():
                    selection = button_name

        if selection is not None:
            self.groupSelectionChanged.emit(str(self.name), str(selection))

    def clickedButton(self):
        button_name = str(self.sender().text())
        self.toggleChecked(button_name, False)

        # for button in self.button_group.buttons():
        # if button is not self.sender():
        # button.setChecked(False)
        # print "sender:", label_name
        
       
 

    def get_checked_button(self):
        return self.button_group.checkedButton()


class ButtonArea(QWidget):
    stateChanged = pyqtSignal(str, str, object)

    def __init__(self, stateChangedSignalSlot = None, labels=None, groupName=None, parent=None):
        QWidget.__init__(self, parent)

        # self.group1_button_list = ButtonListWidget("" if groupName is None else groupName)

        self.hotkeys = []

        self.vlayout = QVBoxLayout()
        self.vlayout.setAlignment(Qt.AlignTop)
        
        # self.stateChanged.connect(self.stateHasChanged)
        if stateChangedSignalSlot is not None:
            self.stateChanged.connect(stateChangedSignalSlot)

        # LOG.info("ButtonArea constructor : labels {} ...".format(labels))
        self.numGroups = len(labels) if labels is not None else 0
  
        self.buttonGroups = {}
        self.buttonGroupWidgets = {}
        
        for i in xrange(self.numGroups):
            thisGroupLabels = labels[i]                           # thisGroupLabels is a dict
            thisGroupName = thisGroupLabels.get('name')      # thisGroupName is a string
            thisGroupOption = thisGroupLabels.get('option')  # thisGroupOption is a tuple of dicts. each dict describes a button
            thisGroupWidget = ButtonListWidget(thisGroupName) 
            
            thisGroupButtons = {}
            for buttonOption in thisGroupOption:
                thisButtonName = buttonOption[config.METADATA_ATTR_VALUE_TOKEN]
                thisButtonProperty = buttonOption.copy()
                
                # thisButtonProperty.pop(config.METADATA_ATTR_VALUE_TOKEN, None)
            	
                if thisGroupName == config.ANNOTATION_UPPER_COLOR_TOKEN or thisGroupName == config.ANNOTATION_LOWER_COLOR_TOKEN or thisGroupName == config.ANNOTATION_VEHICLE_COLOR_TOKEN:
                    thisButtonBkgColor = thisButtonProperty[config.COLOR_ATTR_RGB_VALUE_TOKEN]
                else:
                    thisButtonBkgColor = None
            	    
                thisGroupButtons[thisButtonName] = thisButtonProperty  # add button record to this button group record
  
                thisGroupWidget.add_button(thisButtonName, thisButtonBkgColor)
                
            
            if cnt >= 1:
            	thisGroupWidget.groupSelectionChanged.connect(self.clikedAnyButtonInGroup)
            self.vlayout.addWidget(thisGroupWidget)
            
            self.buttonGroups[thisGroupName] = thisGroupButtons  # add this button group record to button groups recrod
            self.buttonGroupWidgets[thisGroupName] = thisGroupWidget

        # LOG.info("buttonGroupWidgets = {} buttonGroups = {}".format(self.buttonGroupWidgets, self.buttonGroups)

        self.vlayout.addStretch(1)
        self.setLayout(self.vlayout)
        return

    def stateHasChanged(self, button_group_name, button_name, button_attr_desc_dict):
        # LOG.info("stateChanged({}, {}, {})".format(button_group_name, button_name, button_attr_desc_dict))
        return


    def get_checked_button(self, group_name):
        widget = self.buttonGroupWidgets.get(str(group_name), None)
        checkedButtonWidget = widget.get_checked_button() if widget is not None else None
        return checkedButtonWidget


    def add_hotkey(self, choice, name, hotkey):
        self.hotkeys.append((choice, name, hotkey))


    # def get_current_state(self, group_name):
    #     checkedButtonWidget = self.get_checked_button(group_name)
    #     LOG.info("get_current_state with group {} ... ret button {} button.text {}!".format(group_name, checkedButtonWidget, checkedButtonWidget.text()))
    #     return str(checkedButtonWidget.text())
        

    def clikedAnyButtonInGroup(self, _newselection_button_group_name, _newselection_button_name):
        newselection_button_group_name = str(_newselection_button_group_name)
        newselection_button_name = str(_newselection_button_name)
        # LOG.info("clikedAnyButtonInGroup: group {} button {}".format(newselection_button_group_name, newselection_button_name))
        buttonAttrDescDict = self.buttonGroups[newselection_button_group_name][newselection_button_name]
        # self.stateChanged.emit(str(newselection_button_group_name), self.get_current_state(newselection_button_group_name))
        self.stateChanged.emit(str(newselection_button_group_name), str(newselection_button_name), buttonAttrDescDict)

    def startEditMode(self, model_items):
        return

    # def exitInsertMode(self):
    #     button = self.group1_button_list.get_checked_button()
    #     if button is not None:
    #         self.group1_button_list.toggleChecked(button)


def main():
    # from conf import config
    # config.update("example_config.py")

    app = QApplication(sys.argv)
    ba1 = ButtonArea(None, config.BUTTONGROUP4)
    ba1.show()

    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())


