# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

# !/usr/bin/python
import logging, os
from PyQt4 import QtCore, QtGui
from sloth.gui import utils
from sloth.conf import config
from sloth.core import commands
from PyQt4.QtGui import QWidget, QMessageBox, QFileDialog
import copy

GUIDIR = os.path.join(os.path.dirname(__file__))
LOG = logging.getLogger(config.LOG_FILE_NAME)


class createJsonForSpecificImgFolderDialog(QWidget):
    def __init__(self, parent=None, mainwindow=None, exitDialogSlot=None, exitDialogSlotArg1=None,
                 exitDialogSlotArg2=None):
        QWidget.__init__(self, parent)

        self._exitDialogSlot = exitDialogSlot
        self._exitDialogSlotArg1 = exitDialogSlotArg1
        self._exitDialogSlotArg2 = exitDialogSlotArg2
        self._mainwindow = mainwindow

        # ----------------------------------------------------------------------------
        # popup openfolder dialog
        # ----------------------------------------------------------------------------

        path = u'.'
        _folder = QFileDialog.getExistingDirectory(self, "Open Directory",
                                                   path,
                                                   QFileDialog.ShowDirsOnly
                                                   | QFileDialog.DontResolveSymlinks)
        folder = utils.toUTFStr(_folder)

        if not os.path.isdir(folder):
            QMessageBox.critical(None, config.GUI_CRITIAL_ERROR_TEXT, config.GUI_INVALID_PATH_TEXT.format(folder))
            return

        # ----------------------------------------------------------------------------
        # execute commands via command line mode
        # ----------------------------------------------------------------------------
        sloth_app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../slothx.py')
        argv = [sloth_app_dir, 'create', utils.toUTFStr(folder)]
        # print "argv = {}".format(argv)
        self._mainwindow.labeltool.execute_from_commandline(argv, enableExitAfterExecution=False)

        return



class mergeMultipleJsonFilesDialog(QWidget):
    def __init__(self, parent=None, mainwindow=None, exitDialogSlot=None, exitDialogSlotArg1=None,
                 exitDialogSlotArg2=None):
        QWidget.__init__(self, parent)

        self._exitDialogSlot = exitDialogSlot
        self._exitDialogSlotArg1 = exitDialogSlotArg1
        self._exitDialogSlotArg2 = exitDialogSlotArg2
        self._mainwindow = mainwindow

        # ----------------------------------------------------------------------------
        # popup openfile dialog
        # ----------------------------------------------------------------------------

        path = u'.'
        _fnameList = QFileDialog.getOpenFileNames(self, config.GUI_MERGE_JSON_FILE_DIALOG_SRC_FILE_TITLE.format(config.APP_NAME),   path, config.GUI_JSON_FILE_TYPE_TEXT.format  ('*.json'))
        if not _fnameList:
             return
        
        if len(_fnameList) < 2:
            msg = config.GUI_PLS_SPECIFY_MORE_THAN_ONE_JSON_FILES_TEXT
            QMessageBox.critical(None, config.GUI_SUCCESS_TEXT, msg)
            return
        
        fnameList = [ utils.toUTFStr(i) for i in _fnameList ]

        # ----------------------------------------------------------------------------
        # popup savefile dialog
        # ----------------------------------------------------------------------------
        _savefname = QFileDialog.getSaveFileName(self, config.GUI_MERGE_JSON_FILE_DIALOG_DST_FILE_TITLE.format(config.APP_NAME),   path, config.GUI_JSON_FILE_TYPE_TEXT.format  ('*.json'))
        savefname = utils.toUTFStr(_savefname)
        savefdir = os.path.dirname(savefname)
        if not os.path.exists(savefdir):
            os.makedirs(savefdir)
        if not os.path.exists(savefdir):
            msg = config.GUI_INVALID_FOLDER_PATH_TEXT
            QMessageBox.critical(None, config.GUI_ERROR_TEXT, msg)
            return
            
        # ----------------------------------------------------------------------------
        # execute commands via command line mode
        # ----------------------------------------------------------------------------
        sloth_app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../slothx.py')
        _argv = [sloth_app_dir, 'mergefiles']
        # tmpresultfname = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../tmpMerge.json')
        fname1 = fnameList[0]
        fnameCnt = 1
        for index, fname2 in enumerate(fnameList):
            if index == 0:
                continue
            
            argv = copy.deepcopy(_argv)
            argv.append(fname1)
            argv.append(fname2)
            argv.append(savefname)
            fnameCnt += 1
            self._mainwindow.labeltool.execute_from_commandline(argv, enableExitAfterExecution=False)
            fname1 = savefname

        # ----------------------------------------------------------------------------
        # tell user completion
        # ----------------------------------------------------------------------------
        if os.path.exists(savefname) and os.path.isfile(savefname):
            msg = config.GUI_MERGE_JSON_FILE_DIALOG_MERGE_SUCCESS_TEXT.format(fnameCnt, savefname)
            QMessageBox.critical(None, config.GUI_SUCCESS_TEXT, msg)
            return
      
        return


class cleanDuplicateDataInJsonFileDialog(QWidget):
    def __init__(self, parent=None, mainwindow=None, exitDialogSlot=None, exitDialogSlotArg1=None,
                 exitDialogSlotArg2=None):
        QWidget.__init__(self, parent)

        self._exitDialogSlot = exitDialogSlot
        self._exitDialogSlotArg1 = exitDialogSlotArg1
        self._exitDialogSlotArg2 = exitDialogSlotArg2
        self._mainwindow = mainwindow

        # ----------------------------------------------------------------------------
        # popup openfile dialog
        # ----------------------------------------------------------------------------

        path = u'.'
        _fname = QFileDialog.getOpenFileName(self, config.GUI_CLEAN_DUPLICATE_DATA_IN_JSON_FILE_DIALOG_TITLE.format(config.APP_NAME),   path, config.GUI_JSON_FILE_TYPE_TEXT.format  ('*.json'))
        if not _fname:
             return
        
        fname = utils.toUTFStr(_fname)

        # ----------------------------------------------------------------------------
        # popup savefile dialog
        # ----------------------------------------------------------------------------
        _savefname = QFileDialog.getSaveFileName(self, config.GUI_CLEAN_DUPLICATE_DATA_IN_JSON_FILE_DIALOG_DST_FILE_TITLE.format(config.APP_NAME),   path, config.GUI_JSON_FILE_TYPE_TEXT.format  ('*.json'))
        savefname = utils.toUTFStr(_savefname)
        savefdir = os.path.dirname(savefname)
        if not os.path.exists(savefdir):
            os.makedirs(savefdir)
        if not os.path.exists(savefdir):
            msg = config.GUI_INVALID_FOLDER_PATH_TEXT
            QMessageBox.critical(None, config.GUI_ERROR_TEXT, msg)
            return
            
        # ----------------------------------------------------------------------------
        # execute commands via command line mode
        # ----------------------------------------------------------------------------
        sloth_app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../slothx.py')
        argv = [sloth_app_dir, 'cleanduplicate']
        # tmpresultfname = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../tmpMerge.json')
        argv.append(fname)
        argv.append(savefname)
        self._mainwindow.labeltool.execute_from_commandline(argv, enableExitAfterExecution=False)
        
        # ----------------------------------------------------------------------------
        # tell user completion
        # ----------------------------------------------------------------------------
        if os.path.exists(savefname) and os.path.isfile(savefname):
            msg = config.GUI_CLEAN_DUPLICATE_DATA_IN_JSON_FILE_DIALOG_SUCCESS_TEXT.format(fname, savefname)
            QMessageBox.critical(None, config.GUI_SUCCESS_TEXT, msg)
            return
      
        return
        
class SplitToMultipleJsonFilesDialog(QWidget):
    def __init__(self, parent=None, mainwindow=None, exitDialogSlot=None, exitDialogSlotArg1=None,
                 exitDialogSlotArg2=None):
        QWidget.__init__(self, parent)

        self._exitDialogSlot = exitDialogSlot
        self._exitDialogSlotArg1 = exitDialogSlotArg1
        self._exitDialogSlotArg2 = exitDialogSlotArg2
        self._mainwindow = mainwindow
        
        picNum = 100
        enableCopyMediaFilesToSubFolder = 1

        # ----------------------------------------------------------------------------
        # popup openfile dialog
        # ----------------------------------------------------------------------------

        path = u'.'
        _fname = QFileDialog.getOpenFileName(self, 
                config.GUI_OPEN_ANNOTATIONS_DIALOG_TITLE_TEXT % config.APP_NAME, path,
                config.GUI_JSON_FILE_TYPE_TEXT.format  ('*.json'))
        if not _fname:
             return
        
        fname = utils.toUTFStr(_fname)

        # ----------------------------------------------------------------------------
        # execute commands via command line mode
        # ----------------------------------------------------------------------------
        sloth_app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../slothx.py')
        _argv = [sloth_app_dir, 'split']
        # tmpresultfname = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../tmpMerge.json')
        
        outname_base = os.path.join(os.path.dirname(fname), os.path.basename(fname).split(".")[0]+"part")
        # print "outname_base = {}".format(outname_base)
        argv = copy.deepcopy(_argv)
        argv.append(fname)
        argv.append(outname_base)
        argv.append(str(picNum))
        argv.append(str(enableCopyMediaFilesToSubFolder))
        # print "argv = {}".format(argv)
        self._mainwindow.labeltool.execute_from_commandline(argv, enableExitAfterExecution=False)
        
        
        # ----------------------------------------------------------------------------
        # tell user completion
        # ----------------------------------------------------------------------------
        QMessageBox.information(None, config.GUI_SUCCESS_TEXT, "Split completed!")

        return

        