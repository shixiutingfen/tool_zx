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
from sloth.gui.attrArea import AttrAreaWidget
from sloth.gui.propertyeditor import PropertyEditor
from sloth.gui.utils import MyVBoxLayout



LOG = logging.getLogger(config.LOG_FILE_NAME)

def getInsertersProperty(pannelProperty):
    insertersProperty = []
    for element in pannelProperty:
        if element.get('attributes', None):
            insertersProperty.append(element)
    # print "insertersProperty = {}".format(insertersProperty)
    return insertersProperty

def getAttrAreaProperty(pannelProperty):
    attrAreaProperty = []
    for element in pannelProperty:
        if element.get('option', None):
            attrAreaProperty.append(element)
    # print "attrAreaProperty = {}".format(attrAreaProperty)
    return attrAreaProperty


class ComboAreaWidget(QWidget):

    def setAnnotationScene(self, annotationScene):
        self.propertyEditorWidget.setAnnotationScene(annotationScene)

    def setOptionStateChangedSignalSlot(self, checkboxStateChangedSignalSlot):
        if checkboxStateChangedSignalSlot is not None:
            self.propertyEditorWidget.setOptionStateChangedSignalSlot(checkboxStateChangedSignalSlot)
            self.attrAreaWidget.setOptionStateChangedSignalSlot(checkboxStateChangedSignalSlot)

    def __init__(self, comboPannelProperty = None, idName = None, displayName = None, groupBoxName = None, parent=None): 
        QWidget.__init__(self, parent)
        # print "comboPannelProperty = {}".format(comboPannelProperty)
        insertersProperty = getInsertersProperty(comboPannelProperty)
        attrAreaProperty  = getAttrAreaProperty(comboPannelProperty)
        self.attrAreaWidget = AttrAreaWidget(attrAreaProperty, idName, displayName, self)
        self.propertyEditorWidget = PropertyEditor(insertersProperty, idName, displayName, groupBoxName, parent = self)

        self._displayName = displayName
        self._idName = idName
        
        self.vlayout = QVBoxLayout()
        self.vlayout.setAlignment(Qt.AlignTop)
        self.vlayout.setSpacing(4)
        self.vlayout.setMargin(4)
        #self.vlayout.setContentsMargins(0, 0, 0, 44)
        self.vlayout.addWidget(self.propertyEditorWidget)
        self.vlayout.addWidget(self.attrAreaWidget)
        self.vlayout.addStretch(1)
        self.setLayout(self.vlayout)
        return

    def setChecked(self, buttonName, checked = True):
        self.propertyEditorWidget.setChecked(buttonName, checked)

def main():
    # from conf import config
    # config.update("example_config.py")

    app = QApplication(sys.argv)
    ba1 = ComboAreaWidget(config.PERSONBIKE_DETAIL_GROUP)
    ba1.show()

    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())


