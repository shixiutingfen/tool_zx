# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import logging
from sloth.conf import config

LOG = logging.getLogger(config.LOG_FILE_NAME)

class Label(QLabel):
    
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        
    def mouseReleaseEvent(self, ev):
        menu = QMenu(self)
        menu.addActions(self.actions())
        menu.exec_(ev.globalPos())


class ControlButtonWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        layout = QHBoxLayout()
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignTop)
        self.back_button = QPushButton("<")
        self.forward_button = QPushButton(">")

        self._labelfilename = Label('<p align="left"><b></b></p>')
        self._labelPedestrainInfo = Label('<p align="right"><b></b></p>')
        self._labelPersonBikeInfo = Label('<p align="right"><b></b></p>')
        self._labelVehicleInfo = Label('<p align="right"><b></b></p>')

        self._action_copy_filename = QAction("Copy", self._labelfilename)
        self._labelfilename.addAction(self._action_copy_filename)
        self._action_copy_filename.triggered.connect(self.copyFilename)

        self._action_copy_pedestrainInfo = QAction("Copy", self._labelPedestrainInfo)
        self._labelPedestrainInfo.addAction(self._action_copy_pedestrainInfo)
        self._action_copy_pedestrainInfo.triggered.connect(self.copyPedestrainInfo)
        
        self._action_copy_personBikeInfo = QAction("Copy", self._labelPersonBikeInfo)
        self._labelPersonBikeInfo.addAction(self._action_copy_personBikeInfo)
        self._action_copy_personBikeInfo.triggered.connect(self.copyPersonBikeInfo)


        self._action_copy_vehicleInfo = QAction("Copy", self._labelVehicleInfo)
        self._labelVehicleInfo.addAction(self._action_copy_vehicleInfo)
        self._action_copy_vehicleInfo.triggered.connect(self.copyVehicleInfo)

                
        layout.addWidget(self.back_button)
        layout.addWidget(self.forward_button)
        
        # zx mod calling order of "addWidget" to make label align right
        layout.addWidget(self._labelfilename)
        layout.addWidget(self._labelPedestrainInfo)
        layout.addWidget(self._labelPersonBikeInfo)
        layout.addWidget(self._labelVehicleInfo)

        self.setLayout(layout)

    # def setFrameIdx(self, frmIdx, timestamp):
    #    self._labelfilename.setText("<center><b>%d / %f</b></center>" % (frmIdx, timestamp))
    def setFrameIdx(self, frmIdx, timestamp):
        self._labelfilename.setText("<center><b>Frame {}{}</b></center>".format(int(frmIdx), "" if timestamp is None else " / %f".format(timestamp)))

    def setFilename(self, filename):
        self._labelfilename.setText('<p align="left"><b>%s</b></p>' % (filename))

    def setPedestrainObjInfo(self, info):
        self._labelPedestrainInfo.setText(u'<p align="right"><b>{}</b></p>'.format(info))

    def setPersonBikeObjInfo(self, info):
        self._labelPersonBikeInfo.setText('<p align="right"><b>{}</b></p>'.format(info))


    def setVehicleObjInfo(self, info):
        self._labelVehicleInfo.setText(u'<p align="right"><b>{}</b></p>'.format(info))
   


    @pyqtSlot()
    def copyFilename(self):
        doc = QTextDocument()
        doc.setHtml(self._labelfilename.text())
        text = doc.toPlainText()
        QApplication.clipboard().setText(text)
        QApplication.clipboard().setText(text, QClipboard.Selection)

    @pyqtSlot()
    def copyPedestrainInfo(self):
        doc = QTextDocument()
        doc.setHtml(self._labelPedestrainInfo.text())
        text = doc.toPlainText()
        QApplication.clipboard().setText(text)
        QApplication.clipboard().setText(text, QClipboard.Selection)
        
    @pyqtSlot()
    def copyPersonBikeInfo(self):
        doc = QTextDocument()
        doc.setHtml(self._labelPersonBikeInfo.text())
        text = doc.toPlainText()
        QApplication.clipboard().setText(text)
        QApplication.clipboard().setText(text, QClipboard.Selection)        

    @pyqtSlot()
    def copyVehicleInfo(self):
        doc = QTextDocument()
        doc.setHtml(self._labelVehicleInfo.text())
        text = doc.toPlainText()
        QApplication.clipboard().setText(text)
        QApplication.clipboard().setText(text, QClipboard.Selection)        

