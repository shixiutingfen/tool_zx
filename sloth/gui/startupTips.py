# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

#!/usr/bin/python
import logging, os
from PyQt4 import QtCore, QtGui
from sloth.gui.floatinglayout import FloatingLayout
from PyQt4.QtGui import QWidget, QDialog, QVBoxLayout, QLabel, QFont
from sloth.conf import config
from sloth.gui import utils

GUIDIR = os.path.join(os.path.dirname(__file__))
LOG = logging.getLogger(config.LOG_FILE_NAME)


class startupTipsDialog(QDialog):

    def __init__(self, parent = None):
        QDialog.__init__(self, parent)

        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.Dialog)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowCloseButtonHint)

        # zx comment: must be ApplicationModal. otherwise, this dialog cannot block following codes in same thread
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setEnabled(True)

        self._gLayout = QVBoxLayout() # QGridLayout()

        self._statLabelWidget = QLabel(u'<font color="red">{}</font>'.format(config.STARTUP_TIPS_DIALOG_DISPLAYTEXT))
        self._statLabelWidget.setFont(QFont("Timers", 16, QFont.Bold))
        self._gLayout.addWidget(self._statLabelWidget)

        self.setLayout(self._gLayout)
        self.setWindowTitle(config.STARTUP_TIPS_DIALOG_TITLE)
        self.resize(1000, 800)

        utils.centerGuiWidget(self)
        return


