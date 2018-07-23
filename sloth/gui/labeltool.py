# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

#!/usr/bin/python
import logging, os
import functools
import fnmatch,sys,json,datetime,time
import datetime
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QMainWindow, QSizePolicy, QWidget, QVBoxLayout, QAction, QMenu, \
        QKeySequence, QLabel, QItemSelectionModel, QMessageBox, QFileDialog, QFrame, \
        QDockWidget, QProgressBar, QSlider, QHBoxLayout, QLineEdit, QPushButton, QGridLayout, QIntValidator, QDialog, QFont,QDialogButtonBox,QRegExpValidator,QListWidget
from PyQt4.QtCore import SIGNAL, QSettings, QSize, QPoint, QVariant, QFileInfo, QTimer, pyqtSignal, QObject, QString,Qt,QRegExp
import PyQt4.uic as uic
from PIL import Image
from sloth.gui import qrc_icons  # needed for toolbar icons
from sloth.gui.propertyeditor import PropertyEditor
from sloth.gui.annotationscene import AnnotationScene
from sloth.gui.frameviewer import GraphicsView
from sloth.gui.controlbuttons import ControlButtonWidget
from sloth.conf import config
from sloth.core.utils import import_callable
from sloth.annotations.model import AnnotationTreeView, FrameModelItem, ImageFileModelItem, VideoFileModelItem
from sloth.utils.bind import bind, compose_noargs
from sloth.gui.buttonarea import ButtonArea
from sloth.gui.attrArea import AttrAreaWidget
from sloth.gui.textArea import TextAreaWidget
from sloth.gui.comboArea import ComboAreaWidget
from sloth.gui import utils
from sloth.utils import  dbutil
from ftplib import FTP
# from sloth.items.overideGraphicsScene import override_AnnotationScene

GUIDIR=os.path.join(os.path.dirname(__file__))

LOG = logging.getLogger(config.LOG_FILE_NAME)

reload(sys);
sys.setdefaultencoding("utf8")

pannelCreatorFunctions = { 
'PropertyEditor'  : PropertyEditor,
'ComboAreaWidget' : PropertyEditor,   
'AttrAreaWidget'  : AttrAreaWidget
}
                                                       


image_types = [ '*.jpg', '*.bmp', '*.png', '*.pgm', '*.ppm', '*.ppm', '*.tif', '*.gif' ]
video_types = [ '*.mp4', '*.mpg', '*.mpeg', '*.avi', '*.mov', '*.vob' ]

class BackgroundLoader(QObject):
    finished = pyqtSignal()

    def __init__(self, model, statusbar, progress):
        QObject.__init__(self)
        self._max_levels = 3
        self._model = model
        self._statusbar = statusbar
        self._message_displayed = False
        self._progress = progress
        self._progress.setMinimum(0)
        self._progress.setMaximum(1000 * self._max_levels)
        self._progress.setMaximumWidth(150)

        self._level = 1
        self._iterator = self._model.iterator(maxlevels=self._level)
        self._pos = 0
        self._rows = self._model.root().rowCount() + 1
        self._next_rows = 0

    def load(self):
        if not self._message_displayed:
            self._statusbar.showMessage("Loading annotations...", config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS)
            self._message_displayed = True
        if self._level <= self._max_levels and self._rows > 0:
            try:
                item = next(self._iterator)
                self._next_rows += item.rowCount()
                self._pos += 1
                self._progress.setValue(int((float(self._pos) / float(self._rows) + self._level - 1) * 1000))
            except StopIteration:
                self._level += 1
                self._iterator = self._model.iterator(maxlevels=self._level)
                self._pos = 0
                self._rows = self._next_rows
                self._next_rows = 1
        else:
            LOG.debug("Loading finished...")
            self.finished.emit()

class MainWindow(QMainWindow):
    exitGuiMainWindow = pyqtSignal()
    currentDisplayContentChanged = pyqtSignal(bool, object)
    
    def __init__(self, labeltool, parent=None):
        QMainWindow.__init__(self, parent)
        self._lastOpenAnnoFileFolderPath = ""
        self.idletimer = QTimer()
        self.loader = None

        self.labeltool = labeltool
        self.setupGui()
        self.loadApplicationSettings()
        self.onAnnotationsLoaded()
       
        self.last_pos = None
        # self.createContextMenuAction()
        
        self._newInsertingPersonBikeType = config.DEFAULT_PERSONBIKE_TYPE_TOKEN
        return
        

    # ------------------------------------------------------------------------------------------
    # e.g.:
    # setNewInsertingPersonBikeType(config.TAG_PERSONBIKE_TYPE_OF_LIGHT_MOTOR_DISPLAYTEXT)
    # ------------------------------------------------------------------------------------------
    def setNewInsertingPersonBikeType(self, type):
        self._newInsertingPersonBikeType = type
        return

        
    # Slots
    def onPluginLoaded(self, action):
        self.ui.menuPlugins.addAction(action)

    def onStatusMessage(self, message='', messageDisplayTime = config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS):
        # self.statusBar().showMessage('<font color="red">{}</font>'.format(message), config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS)
        self.statusBar().showMessage(message, messageDisplayTime)

    def setWinTitle(self, fileName):
        if fileName is not None:
            self.setWindowTitle(u"%s - %s" % (config.APP_NAME, fileName))
        else:
            self.setWindowTitle(u"%s - %s" % (config.APP_NAME, config.GUI_UNAMED_ANNOTATION_TEXT))
              
    def onModelDirtyChanged(self, dirty):
        fileFullName = self.labeltool.getCurrentContainerFilename()
        fileFullName = fileFullName if fileFullName is not None else config.GUI_UNAMED_ANNOTATION_TEXT
        
        fileName = os.path.basename(fileFullName)
        filenameutf = utils.toUTFStr(fileName)
        self.setWinTitle(filenameutf + (" [+]" if dirty else ""))
        
    def onItemIsInsertedOrSelected(self, x, y, flag):
        width = -1
        height = -1
        if flag == 0:   # inserter mouse press
            self.last_pos = [x, y]
        elif flag == 1: # inserter mouse move
            if self.last_pos is not None:
                width  = abs(x - self.last_pos[0])
                height = abs(y - self.last_pos[1])
                self.bboxsize.setText("%d * %d" % (width, height))
            return
        elif flag == 2: # inserter finished
             if self.last_pos is not None:
                width  = abs(x - self.last_pos[0])
                height = abs(y - self.last_pos[1])   
             self.last_pos = None         
        elif flag == 3: # item is selected
            width = x
            height = y
            
        self.bboxsize.setText("%d * %d" % (width, height))
        return
                
    
    def onMousePositionChanged(self, x, y):
        self.posinfo.setText("%d, %d" % (x, y))

    def startBackgroundLoading(self):
        self.stopBackgroundLoading(forced=True)
        self.loader = BackgroundLoader(self.labeltool.model(), self.statusBar(), self.sb_progress)
        self.idletimer.timeout.connect(self.loader.load)
        self.loader.finished.connect(self.stopBackgroundLoading)
        self.statusBar().addWidget(self.sb_progress)
        self.sb_progress.show()
        self.idletimer.start()

    def stopBackgroundLoading(self, forced=False):
        if not forced:
            self.statusBar().showMessage(config.GUI_BACKGROUND_LOADING_ANNOTATION_MODEL_TIP, config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS)
        self.idletimer.stop()

        if self.loader is not None:
            self.idletimer.timeout.disconnect(self.loader.load)
            self.statusBar().removeWidget(self.sb_progress)
            self.loader = None

    def onAnnotationsLoaded(self):
        LOG.info("onAnnotationsLoaded ... MODEL = {} self._root.rowCount() = {}".format(self.labeltool.model(), self.labeltool.model()._root.rowCount()))
        self.initGuiWidgets()

        self.labeltool.model().dirtyChanged.connect(self.onModelDirtyChanged)
        self.onModelDirtyChanged(self.labeltool.model().dirty())
        self.treeview.setModel(self.labeltool.model())
        self.scene.setModel(self.labeltool.model())
        self.selectionmodel = QItemSelectionModel(self.labeltool.model())
        self.treeview.setSelectionModel(self.selectionmodel)
        self.treeview.selectionModel().currentChanged.connect(self.labeltool.onCurrentChanged)
        LOG.info("treeview.selectionModel {} connect setCurrentImage ...".format(self.treeview.selectionModel()))

        map(lambda x:x.onModelChanged(self.labeltool.model()), self.inserterAreaWidgets.values())

        
        # if config.ENABLE_TOP_OBJECT_MODE:
        if False:
            map(lambda x: x.hide(), self.pannels.values())
            map(lambda x: x.hide(), self.getPannelContainers().values())
            self.getPannelContainers()['dockProperties_personbike'].show()
            self.pannels['COMBOGROUP_PERSONBIKE'].show()


        
        # zx added @ 20161117
        LOG.info("onAnnotationsLoaded .. Model {} setDirty False ...".format(self.scene._model))
        self.scene._model.setDirty(False)
        
        self.startBackgroundLoading()


    def statisticNDisplayObjInfo(self):
        cur_image = self.labeltool.currentImage()
        pedestrainstr, info = utils.statisticPedestrainObjInfo(cur_image)
        personbikestr, info = utils.statisticPersonBikeObjInfo(cur_image)
        vehiclestr, info = utils.statisticVehicleObjInfo(cur_image)
        self.displayObjInfo(pedestrainstr, personbikestr, vehiclestr)
        
                    
    def displayObjInfo(self, pedestrainstr, personbikestr, vehiclestr):
        self.controls.setPedestrainObjInfo('<font color="red"> {} </font>'.format(pedestrainstr  if pedestrainstr else ''))
        self.controls.setPersonBikeObjInfo('<font color="blue"> {} </font>'.format(personbikestr if personbikestr else ''))
        self.controls.setVehicleObjInfo('<font color="darkred"> {} </font>'.format(vehiclestr    if vehiclestr    else ''))


    def displayFilenameNFrameIdx(self, objDescStr, current_img_item):
        if current_img_item is None:
            self.controls.setFilename("")
        else:    
            if isinstance(current_img_item, FrameModelItem):
                # self.controls.setFrameIdx(current_img_item.frameidx(), current_img_item.timestamp())
                videoFileName, videoFileItem = self.labeltool.getFrmParentVideo(current_img_item)
                self.controls.setFilename((objDescStr if objDescStr else '') + "Frm{} - (".format(current_img_item.frameidx())+str( videoFileItem.index().row()+1)+") "+os.path.basename(videoFileName))
            elif isinstance(current_img_item, ImageFileModelItem):
                self.controls.setFilename((objDescStr if objDescStr else '') + "("+str( current_img_item.index().row()+1)+") "+os.path.basename(current_img_item[config.ANNOTATION_FILENAME_TOKEN]))


 
    def onCurrentDisplayContentChanged(self, isImgViewMode, current_img_item):
        if isImgViewMode:
            self.displayFilenameNFrameIdx(None, current_img_item)
        else:
            (idx, num) = self.scene.get_objViewModeInfo(current_img_item)

            objDescStr = u'{}{}/{} | '.format(config.GUI_OBJ_TEXT, idx, num)
            # print u"objDescStr = {}".format(objDescStr)
            self.displayFilenameNFrameIdx(objDescStr, current_img_item)
            


    def onCurrentImageChanged(self, flush = False, display = True):
        new_image = self.labeltool.currentImage()
        LOG.info("onCurrentImageChanged CALL setCurrentImage {}...".format(new_image))
        
        self.scene.setCurrentImage(new_image, flush, display)
        
        self.onFitToWindowModeChanged()
        self.treeview.scrollTo(new_image.index())

        if self.scene._image is None:
            self.displayFilenameNFrameIdx(None, None)
            self.selectionmodel.setCurrentIndex(new_image.index(), QItemSelectionModel.ClearAndSelect|QItemSelectionModel.Rows)
            return
            
        [w, h] = self.scene.currentImageSize()
        self.displayImageResolution(w, h)
        

        # TODO: This info should be obtained from AnnotationModel or LabelTool
        self.displayFilenameNFrameIdx(None, new_image)
            
        self.statisticNDisplayObjInfo()
         
        self.selectionmodel.setCurrentIndex(new_image.index(), QItemSelectionModel.ClearAndSelect|QItemSelectionModel.Rows)

    def onNewItemIsInserted(self, parentModelItem, modelItemName):
        selected_scene_items = [self.scene.modelItem_to_baseItem(parentModelItem)]
        self.scene.setWidgetState(selected_scene_items)
    
        self.onCurImageInfoUpdated(modelItemName)
    
    # zx add @ 20161015
    def onCurImageInfoUpdated(self, insertedOrDeletedModelItemName):
        pass
        #cur_img = self.labeltool.currentImage()
        ## print "[ZXD] onCurImageInfoUpdated is called with {}".format(insertedOrDeletedModelItemName)
        #if ( oriinsertedOrDeletedModelItemNamegin == "PersonHead"):
        #    self.controls.setHeadsInfo ( '<font color="red">Heads: {}</font>'.format(cur_img.getSpecificLabelsNum('class', 'PersonHead')) ) 
        #else :
        #    if ( insertedOrDeletedModelItemName == "PersonUpRightHeight"):
        #        self.controls.setPersonHeightsInfo ( '<font color="red">Heights: {}</font>'.format(cur_img.getSpecificLabelsNum('class', 'PersonUpRightHeight')) )

    def onFitToWindowModeChanged(self):
        if self.options[config.OPTION_ACTION_FITTOWIN_TOKEN].isChecked():
            self.view.fitInView()

    def onScaleChanged(self, scale):
        self.zoominfo.setText("%.2f%%" % (100 * scale, ))

    def initShortcuts(self, HOTKEYS):
        self.shortcuts = []

        for hotkey in HOTKEYS:
            assert len(hotkey) >= 2
            key = hotkey[0]
            fun = hotkey[1]
            desc = ""
            if len(hotkey) > 2:
                desc = hotkey[2]

            hk = QAction(desc, self)
            if key != None:
                hk.setShortcut(QKeySequence(key))
                
            hk.setEnabled(True)
            
            if (type(fun) == str):
                fun = import_callable(fun)
                
            if hasattr(fun, '__call__'):
                hk.triggered.connect(bind(fun, self.labeltool))
            else:
                hk.triggered.connect(compose_noargs([bind(f, self.labeltool) for f in fun]))
            
            self.ui.menuShortcuts.addAction(hk)
            self.shortcuts.append(hk)

    def initOptions(self):
        self.options = {}
        for o in [config.OPTION_ACTION_FITTOWIN_TOKEN]:
            action = QAction(config.GUI_MENU_OPTION_ACTION_FITTOWIN_DISPLAYTEXT, self)
            action.setCheckable(True)
            self.ui.menuOptions.addAction(action)
            self.options[o] = action

 
    def getBelongingPannel(self, labelName):
        pannelName = config._class_pannelName[str(labelName)]
        if pannelName:
            return self.pannels.get(pannelName, None)           
        else:
            return None
    
    def setWidgetChecked(self, labelName, checked = False):
        pe = self.getBelongingPannel(labelName)
        if pe:
            pe.setChecked(labelName, checked)
        return
                 
    ###___________________________________________________________________________________________
    ###
    ### GUI/Application setup
    ###___________________________________________________________________________________________
    def getPannelContainers(self):
        if self.ui:
            pannelContainers = {
                'dockProperties1': self.ui.dockProperties1,
                'dockProperties2': self.ui.dockProperties2,
                'dockProperties3': self.ui.dockProperties3,
                'dockProperties4': self.ui.dockProperties4,
                'dockProperties5': self.ui.dockProperties5,
                'dockProperties6': self.ui.dockProperties6,
                'dockProperties_personbike': self.ui.dockProperties_personbike,
                'dockAnnotations'     : self.ui.dockAnnotations,
                'dockObjViewModeInfoWidget'        : self.ui.dockObjViewModeInfoWidget
            }
            return pannelContainers
        return {}
           
    def setupGui(self):
        self.ui = uic.loadUi(os.path.join(GUIDIR, "labeltool.ui"), self)
          

        self.pannels = {}
        self.inserterAreaWidgets = {}
        self.attrAreaWidgets = {}
        inserters = {}
        items = {}
        for pannelProterty, pannelName, pannelDisplayText, pannelCreatorName, pannelContainerName, extraArgs in config.PANNELPROPERTY_LIST:
            pannelCreator = pannelCreatorFunctions.get(pannelCreatorName, None)
            if pannelCreatorName == 'PropertyEditor':
                self.pannels[pannelName] = PropertyEditor(pannelProterty, pannelName, pannelDisplayText, "")
                self.getPannelContainers()[pannelContainerName].setWidget(self.pannels[pannelName])
                self.getPannelContainers()[pannelContainerName].setWindowTitle(pannelDisplayText)
                self.inserterAreaWidgets[pannelName] = self.pannels[pannelName]
                inserters.update(dict( [key, value[0] ] for key, value in self.pannels[pannelName]._inserters_guiitems.iteritems() ) )
                items.update    (dict( [key, value[1] ] for key, value in self.pannels[pannelName]._inserters_guiitems.iteritems() ) )
            elif pannelCreatorName == 'ComboAreaWidget':
                self.pannels[pannelName] = ComboAreaWidget(comboPannelProperty = pannelProterty,
                                                           idName = pannelName, displayName = pannelDisplayText, groupBoxName = extraArgs[0], parent = None)
                self.getPannelContainers()[pannelContainerName].setWidget(self.pannels[pannelName])
                self.getPannelContainers()[pannelContainerName].setWindowTitle(pannelDisplayText)
                self.inserterAreaWidgets[pannelName] = self.pannels[pannelName].propertyEditorWidget
                self.attrAreaWidgets[pannelName] = self.pannels[pannelName].attrAreaWidget
                inserters.update(dict( [key, value[0] ] for key, value in self.pannels[pannelName].propertyEditorWidget._inserters_guiitems.iteritems()))
                items.update    (dict( [key, value[1] ] for key, value in self.pannels[pannelName].propertyEditorWidget._inserters_guiitems.iteritems() ) )
            elif pannelCreatorName == 'AttrAreaWidget':
                self.pannels[pannelName] = AttrAreaWidget(pannelProterty, pannelName, pannelDisplayText)
                self.getPannelContainers()[pannelContainerName].setWidget(self.pannels[pannelName])
                self.getPannelContainers()[pannelContainerName].setWindowTitle(pannelDisplayText)
                self.attrAreaWidgets[pannelName] = self.pannels[pannelName]


        # print "setupGUI... inserters = {}".format(inserters)
        # print "setupGUI... items = {}".format(items)

        self.property_editor1  = self.pannels.get('BUTTONGROUP1', None)
        self.property_editor2  = self.pannels.get('BUTTONGROUP2', None)
        self.property_editor3  = self.pannels.get('BUTTONGROUP3', None)
        self.property_editor4  = self.pannels.get('BUTTONGROUP4', None)
        self.property_editor5  = self.pannels.get('BUTTONGROUP5', None)
        self.property_editor6  = self.pannels.get('BUTTONGROUP6', None)
        self.personbike_pannel = self.pannels.get('COMBOGROUP_PERSONBIKE', None)

        
        # get inserters and items from labels
        # FIXME for handling the new-style config correctly

        # Scene
        self.scene = AnnotationScene(self.labeltool, items=items, inserters=inserters)     
        # self.scene = override_AnnotationScene(self.labeltool, items=items, inserters=inserters)   
        for key, pannel in self.pannels.iteritems():
            pannel.setAnnotationScene(self.scene)
            if config.PANNELPROPERTY_LIST[ [ index for index, i in enumerate(config.PANNELPROPERTY_LIST) if i[1] == key ][0] ] [3] == 'ComboAreaWidget':
                pannel.setOptionStateChangedSignalSlot(self.scene.onAttrChanged)
            else:    
                pannel.setOptionStateChangedSignalSlot(self.scene.onAttrChanged)
            
        # dockObjViewModeInfo
        if config.ENABLE_STATISTIC_OBJ_INFO:
            self.objViewModeInfoWidget = TextAreaWidget(u'物体信息')
            self.ui.dockObjViewModeInfoWidget.setWidget(self.objViewModeInfoWidget)
            self.ui.dockObjViewModeInfoWidget.setWindowTitle(u'物体信息')
            self.pannels["OBJINFO"] = self.objViewModeInfoWidget
        else:
            self.ui.dockObjViewModeInfoWidget.deleteLater()

        # create slots
        self.property_editor1.propertyEditorWidget.insertionModeStarted.connect(self.scene.onInsertionModeStarted)
        self.property_editor1.propertyEditorWidget.insertionModeEnded.connect(self.scene.onInsertionModeEnded)
        self.personbike_pannel.propertyEditorWidget.insertionModeStarted.connect(self.scene.onInsertionModeStarted)
        self.personbike_pannel.propertyEditorWidget.insertionModeEnded.connect(self.scene.onInsertionModeEnded)
        self.property_editor2.insertionModeStarted.connect(self.scene.onInsertionModeStarted)
        self.property_editor2.insertionModeEnded.connect(self.scene.onInsertionModeEnded)
        self.property_editor3.insertionModeStarted.connect(self.scene.onInsertionModeStarted)
        self.property_editor3.insertionModeEnded.connect(self.scene.onInsertionModeEnded)
        self.property_editor6.propertyEditorWidget.insertionModeStarted.connect(self.scene.onInsertionModeStarted)
        self.property_editor6.propertyEditorWidget.insertionModeEnded.connect(self.scene.onInsertionModeEnded)
        
        # SceneView
        # self.view = override_GraphicsView(self)  # self.view = GraphicsView(self)
        self.view = GraphicsView(self)
        self.view.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.view.setScene(self.scene)


        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout()
        self.controls = ControlButtonWidget()

        self.controls.back_button.clicked.connect(bind(self.labeltool.gotoPrevious, 1))
        self.controls.forward_button.clicked.connect(bind(self.labeltool.gotoNext, 1))
        
        self.central_layout.addWidget(self.controls)
        self.central_layout.addWidget(self.view)
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)

        self.initShortcuts(config.HOTKEYS)
        self.initOptions()

        self.treeview = AnnotationTreeView()
        self.treeview.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.ui.dockAnnotations.setWidget(self.treeview)
        self.ui.dockAnnotations.setWindowTitle(config.GUI_ANNOTATION_DISPLAYTEXT)
        self.pannels["ANNOTATION"] = self.treeview 
        

        self.scene.selectionChanged.connect(self.scene.onSelectionChanged)
        self.treeview.selectedItemsChanged.connect(self.scene.onSelectionChangedInTreeView)
        
 
        self.topViewModeObjEdgeXRatioTextWidget = QLabel()
        self.statusBar().addPermanentWidget(self.topViewModeObjEdgeXRatioTextWidget)
               
        self.topViewModeObjEdgeXRatioSliderWidget = QSlider(QtCore.Qt.Horizontal)
        self.topViewModeObjEdgeXRatioSliderWidget.setMinimum(0)
        self.topViewModeObjEdgeXRatioSliderWidget.setMaximum(100)
        posX = 20
        self.topViewModeObjEdgeXRatioSliderWidget.setValue(posX)
        self.topViewModeObjEdgeXRatioTextWidget.setText(u'<font color="red", style="font-weight:bold">MarginX={}</font>'.format(posX))
        # self.topViewModeObjEdgeXRatioSliderWidget.resize(100, 50)
        self.statusBar().addPermanentWidget(self.topViewModeObjEdgeXRatioSliderWidget)
        self.topViewModeObjEdgeXRatioSliderWidget.valueChanged.connect(self.setTopViewModeObjEdgeXRatio)
        
        self.topViewModeObjEdgeYRatioTextWidget = QLabel()
        self.statusBar().addPermanentWidget(self.topViewModeObjEdgeYRatioTextWidget)
               
        self.topViewModeObjEdgeYRatioSliderWidget = QSlider(QtCore.Qt.Horizontal)
        self.topViewModeObjEdgeYRatioSliderWidget.setMinimum(0)
        self.topViewModeObjEdgeYRatioSliderWidget.setMaximum(100)
        posY = 20
        self.topViewModeObjEdgeYRatioSliderWidget.setValue(posY)
        self.topViewModeObjEdgeYRatioTextWidget.setText(u'<font color="red", style="font-weight:bold">MarginY={}</font>'.format(posY))
        # self.topViewModeObjEdgeYRatioSliderWidget.resize(100, 50)
        self.statusBar().addPermanentWidget(self.topViewModeObjEdgeYRatioSliderWidget)
        self.topViewModeObjEdgeYRatioSliderWidget.valueChanged.connect(self.setTopViewModeObjEdgeYRatio)

        self.imgOrObjViewModeInfo = QLabel()
        self.imgOrObjViewModeInfo.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        self.statusBar().addPermanentWidget(self.imgOrObjViewModeInfo)
        
        self.selectCnts = QLabel()
        self.selectCnts.setFrameStyle(QFrame.StyledPanel)
        self.statusBar().addPermanentWidget(self.selectCnts)
        
        self.autoConnectLabelModeInfo = QLabel()
        self.autoConnectLabelModeInfo.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        self.statusBar().addPermanentWidget(self.autoConnectLabelModeInfo)
 
        self.insertOrEditModeInfo = QLabel()
        self.insertOrEditModeInfo.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        self.statusBar().addPermanentWidget(self.insertOrEditModeInfo)

        self.posinfo = QLabel("-1, -1")
        self.posinfo.setFrameStyle(QFrame.StyledPanel)
        self.statusBar().addPermanentWidget(self.posinfo)
        self.scene.mousePositionChanged.connect(self.onMousePositionChanged)

        self.bboxsize = QLabel("-1, -1")
        self.bboxsize.setFrameStyle(QFrame.StyledPanel)
        self.statusBar().addPermanentWidget(self.bboxsize)
        self.scene.itemIsInsertedOrSelected.connect(self.onItemIsInsertedOrSelected)

        self.image_resolution = QLabel()
        self.image_resolution.setFrameStyle(QFrame.StyledPanel)
        self.statusBar().addPermanentWidget(self.image_resolution)

        self.zoominfo = QLabel()
        self.zoominfo.setFrameStyle(QFrame.StyledPanel)
        self.statusBar().addPermanentWidget(self.zoominfo)
        self.view.scaleChanged.connect(self.onScaleChanged)
        self.onScaleChanged(self.view.getScale())
        
        self.initGuiWidgets()

        
        # hide specific pannels
        for p in config.HIDDEN_PANNELS:
            pw = self.pannels.get(p, None)
            if pw:
                pw.hide()

        # hide specific checkbox groups
        for p, g in config.PANNELS_HIDDEN_GROUPS.iteritems():
            pw = self.pannels.get(p, None)
            if pw and g:
                pw.hideGroup(g)
        


        self.sb_progress = QProgressBar()
        
        # View menu
        for pcname, pc in self.getPannelContainers().iteritems():
            pname = [i[1] for i in config.PANNELPROPERTY_LIST if i[4] == pcname]
            if pname and pname[0] not in config.HIDDEN_PANNELS:
                if pc:
                    self.ui.menu_Views.addAction(pc.toggleViewAction())
        
        # customize menus' title
        self.ui.menuPlugins.setTitle(config.GUI_MENU_PLUGIN_DISPLAYTEXT)
        self.ui.menuShortcuts.setTitle(config.GUI_MENU_SHORTCUT_DISPLAYTEXT)
        self.ui.menuOptions.setTitle(config.GUI_MENU_OPTION_DISPLAYTEXT)
        self.ui.menuFile.setTitle(config.GUI_MENU_FILE_DISPLAYTEXT)
        self.ui.menu_Edit.setTitle(config.GUI_MENU_EDIT_DISPLAYTEXT)
        self.ui.menu_Views.setTitle(config.GUI_MENU_VIEW_DISPLAYTEXT)
        self.ui.menu_Help.setTitle(config.GUI_MENU_HELP_DISPLAYTEXT)
        self.ui.menu_Net.setTitle(config.GUI_MENU_NET_DISPLAYTEXT)
        self.ui.action_Add_Image.setText(config.GUI_MENU_EDIT_ACTION_ADD_IMG_DISPLAYTEXT   )
        self.ui.action_Add_Video.setText(config.GUI_MENU_EDIT_ACTION_ADD_VIDEO_DISPLAYTEXT   )
        self.ui.actionNew.setText(config.GUI_MENU_FILE_ACTION_NEW_DISPLAYTEXT       )
        self.ui.actionOpen.setText(config.GUI_MENU_FILE_ACTION_OPEN_DISPLAYTEXT      )
        self.ui.actionSave.setText(config.GUI_MENU_FILE_ACTION_SAVE_DISPLAYTEXT      )
        self.ui.actionSave_As.setText(config.GUI_MENU_FILE_ACTION_SAVEAS_DISPLAYTEXT    )
        self.ui.actionExit.setText(config.GUI_MENU_FILE_ACTION_EXIT_DISPLAYTEXT      )
        self.ui.actionLocked.setText(config.GUI_MENU_VIEW_ACTION_LOCKED                )
        self.ui.action_About.setText(config.GUI_MENU_HELP_ACTION_ABOUT_DISPLAYTEXT     )
        self.ui.actionNet.setText(config.GUI_MENU_HELP_ACTION_IMPORTNET_DISPLAYTEXT     )

        self.currentDisplayContentChanged.connect(self.onCurrentDisplayContentChanged)
        
        
        # Show the UI.  It is important that this comes *after* the above 
        # adding of custom widgets, especially the central widget.  Otherwise the
        # dock widgets would be far to large.
        self.ui.show()

        ## connect action signals
        self.connectActions()

    def setTopViewModeObjEdgeXRatio(self, value):
        pos = self.topViewModeObjEdgeXRatioSliderWidget.value()
        self.topViewModeObjEdgeXRatioTextWidget.setText(u'<font color="red", style="font-weight:bold">MarginX={}</font>'.format(pos))
        if (self.scene._sceneViewMode == config.OBJ_VIEW_MODE):
            self.scene.setCurrentDisplayObjImg(self.scene._objViewModeTopModelItem, flush = True)

    def setTopViewModeObjEdgeYRatio(self, value):
        pos = self.topViewModeObjEdgeYRatioSliderWidget.value()
        self.topViewModeObjEdgeYRatioTextWidget.setText(u'<font color="red", style="font-weight:bold">MarginY={}</font>'.format(pos))
        if (self.scene._sceneViewMode == config.OBJ_VIEW_MODE):
            self.scene.setCurrentDisplayObjImg(self.scene._objViewModeTopModelItem, flush = True)


                   
    def displayInsertOrEditMode(self, text):
        LOG.info(u"settext {}...".format(text))
        self.insertOrEditModeInfo.setText(u'<font color="red", style="font-weight:bold">{}</font>'.format(text))

    def displayImageResolution(self, w, h):
        self.image_resolution.setText("%dx%d" % (w, h))

    def displayAutoConnectLabelMode(self, text):
        self.autoConnectLabelModeInfo.setText(u'<font color="red", style="font-weight:bold">{}</font>'.format(text))

    def displayImgOrObjViewMode(self, text):
        self.imgOrObjViewModeInfo.setText(u'<font color="red", style="font-weight:bold">{}</font>'.format(text))
                                                         
    def displaySelectedObjsCnt(self, pedestrainCnt, personBikeCnt, vehicleCnt):
        self.selectCnts.setText(u'<font color="blue", style="font-weight:bold"> {}: P{}|B{}|V{} </font>'.format(config.GUI_SELECTED_TIP, pedestrainCnt, personBikeCnt, vehicleCnt))

    def statisticNdisplaySelectedObjsCnt(self):
        (pedestrainCnt, personBikeCnt, vehicleCnt) = self.scene.statisticSelectedObjsCnt()
        self.displaySelectedObjsCnt(pedestrainCnt, personBikeCnt, vehicleCnt)
        
        
    def initGuiWidgets(self):
        self.displayImgOrObjViewMode(config.IMG_VIEW_MODE_DISPLAY_TEXT)
        self.displaySelectedObjsCnt(0, 0, 0)
        self.displayInsertOrEditMode(config.GUI_EDIT_MODE_DISPLAY_TEXT)
        self.displayImageResolution(0, 0)
        self.displayObjInfo(None, None, None)
        self.displayFilenameNFrameIdx(None, None)
        self._enableAutoConnectLabelMode = config.DEFAULT_AUTO_CONNECT_LABELS_MODE
        self.displayAutoConnectLabelMode(config.GUI_AUTO_CONNECT_MODE_DISPLAY_TEXT if self._enableAutoConnectLabelMode else config.GUI_MANNUAL_CONNECT_MODE_DISPLAY_TEXT)

                
    def connectActions(self):
        ## File menu
        self.ui.actionNew.    triggered.connect(self.fileNew)
        self.ui.actionOpen.   triggered.connect(self.fileOpen)
        self.ui.actionSave.   triggered.connect(self.fileSave)
        self.ui.actionSave_As.triggered.connect(self.fileSaveAs)
        self.ui.actionExit.   triggered.connect(self.close)

        ## View menu
        self.ui.actionLocked.toggled.connect(self.onViewsLockedChanged)

        ## Help menu
        self.ui.action_About.triggered.connect(self.about)
        ## NetMenu
        self.ui.actionNet.triggered.connect(self.importNet)
        ## Navigation
        self.ui.action_Add_Image.triggered.connect(self.addImageFiles)
        self.ui.action_Add_Video.triggered.connect(self.addVideoFileWithFrmIntervalDialog)
        self.ui.actionPrevious.  triggered.connect(bind(self.labeltool.gotoPrevious, 1))
        self.ui.actionNext.      triggered.connect(bind(self.labeltool.gotoNext, 1))
        self.ui.actionZoom_In.   triggered.connect(functools.partial(self.view.setScaleRelative, 1.2))
        self.ui.actionZoom_Out.  triggered.connect(functools.partial(self.view.setScaleRelative, 1/1.2))

        ## Connections to LabelTool
        self.labeltool.pluginLoaded.       connect(self.onPluginLoaded)
        self.labeltool.statusMessage.      connect(self.onStatusMessage)
        self.labeltool.annotationsLoaded.  connect(self.onAnnotationsLoaded)
        self.labeltool.currentImageChanged.connect(self.onCurrentImageChanged)
        
        # zx add @ 20161015
        self.labeltool.newItemIsInserted.connect(self.onNewItemIsInserted)
        self.labeltool.itemIsDeleted.connect(self.onCurImageInfoUpdated)

        ## options menu
        self.options[config.OPTION_ACTION_FITTOWIN_TOKEN].changed.connect(self.onFitToWindowModeChanged)

    def loadApplicationSettings(self):
        settings = QSettings()
        lastOpenAnnoFileFoderPath = settings.value("AnnoFile/Folder", "")
        size   = settings.value("MainWindow/Size", QSize(800, 600))
        pos    = settings.value("MainWindow/Position", QPoint(10, 10))
        dockProperties1_size = settings.value("dockProperties1/Size",     QSize (80, 20))
        dockProperties1_pos  = settings.value("dockProperties1/Position", QPoint(10, 10))
        dockProperties_personbike_size = settings.value("dockProperties_personbike/Size",     QSize (80, 20))
        dockProperties_personbike_pos  = settings.value("dockProperties_personbike/Position", QPoint(10, 10))
        dockProperties2_size = settings.value("dockProperties2/Size",     QSize (80, 20))
        dockProperties2_pos  = settings.value("dockProperties2/Position", QPoint(10, 10))
        dockProperties3_size = settings.value("dockProperties3/Size",     QSize (80, 20))
        dockProperties3_pos  = settings.value("dockProperties3/Position", QPoint(10, 10))
        dockProperties4_size = settings.value("dockProperties4/Size",     QSize (80, 20))
        dockProperties4_pos  = settings.value("dockProperties4/Position", QPoint(10, 10))
        dockProperties5_size = settings.value("dockProperties5/Size",     QSize (80, 20))
        dockProperties5_pos  = settings.value("dockProperties5/Position", QPoint(10, 10))
        dockProperties6_size = settings.value("dockProperties6/Size",     QSize (80, 20))
        dockProperties6_pos  = settings.value("dockProperties6/Position", QPoint(10, 10))
        if config.ENABLE_STATISTIC_OBJ_INFO:
            dockObjViewModeInfoWidget_size = settings.value("dockObjViewModeInfoWidget/Size",     QSize (80, 20))
            dockObjViewModeInfoWidget_pos  = settings.value("dockObjViewModeInfoWidget/Position", QPoint(10, 10))
        dockAnnotations_size = settings.value("dockAnnotations/Size",     QSize (80, 20))
        dockAnnotations_pos  = settings.value("dockAnnotations/Position", QPoint(10, 10))
        state  = settings.value("MainWindow/State")
        locked = settings.value("MainWindow/ViewsLocked", False)
        if isinstance(size,   QVariant): size  = size.toSize()
        if isinstance(pos,    QVariant): pos   = pos.toPoint()
        if isinstance(lastOpenAnnoFileFoderPath,    QVariant): lastOpenAnnoFileFoderPath = lastOpenAnnoFileFoderPath.toString()
        
        if isinstance(dockProperties1_size,   QVariant): dockProperties1_size  = dockProperties1_size.toSize()
        if isinstance(dockProperties1_pos,    QVariant): dockProperties1_pos   = dockProperties1_pos.toPoint()
        if isinstance(dockProperties_personbike_size,   QVariant): dockProperties_personbike_size  = dockProperties_personbike_size.toSize()
        if isinstance(dockProperties_personbike_pos,    QVariant): dockProperties_personbike_pos   = dockProperties_personbike_pos.toPoint()
        if isinstance(dockProperties2_size,   QVariant): dockProperties2_size  = dockProperties2_size.toSize()
        if isinstance(dockProperties2_pos,    QVariant): dockProperties2_pos   = dockProperties2_pos.toPoint()
        if isinstance(dockProperties3_size,   QVariant): dockProperties3_size  = dockProperties3_size.toSize()
        if isinstance(dockProperties3_pos,    QVariant): dockProperties3_pos   = dockProperties3_pos.toPoint()
        if isinstance(dockProperties4_size,   QVariant): dockProperties4_size  = dockProperties4_size.toSize()
        if isinstance(dockProperties4_pos,    QVariant): dockProperties4_pos   = dockProperties4_pos.toPoint()
        if isinstance(dockProperties5_size,   QVariant): dockProperties5_size  = dockProperties5_size.toSize()
        if isinstance(dockProperties5_pos,    QVariant): dockProperties5_pos   = dockProperties5_pos.toPoint()
        if isinstance(dockProperties6_size,   QVariant): dockProperties6_size  = dockProperties6_size.toSize()
        if isinstance(dockProperties6_pos,    QVariant): dockProperties6_pos   = dockProperties6_pos.toPoint()
        if config.ENABLE_STATISTIC_OBJ_INFO:
            if isinstance(dockObjViewModeInfoWidget_size,   QVariant): dockObjViewModeInfoWidget_size  = dockObjViewModeInfoWidget_size.toSize()
            if isinstance(dockObjViewModeInfoWidget_pos,    QVariant): dockObjViewModeInfoWidget_pos   = dockObjViewModeInfoWidget_pos.toPoint()
        if isinstance(dockAnnotations_size,   QVariant): dockAnnotations_size  = dockAnnotations_size.toSize()
        if isinstance(dockAnnotations_pos,    QVariant): dockAnnotations_pos   = dockAnnotations_pos.toPoint()
        if isinstance(state,  QVariant): state = state.toByteArray()
        if isinstance(locked, QVariant): locked = locked.toBool()

        self.resize(size)
        self.move(pos)
        self.ui.dockProperties1.resize(dockProperties1_size)
        self.ui.dockProperties1.move  (dockProperties1_pos)
        self.ui.dockProperties_personbike.resize(dockProperties_personbike_size)
        self.ui.dockProperties_personbike.move  (dockProperties_personbike_pos)
        self.ui.dockProperties2.resize(dockProperties2_size)
        self.ui.dockProperties2.move  (dockProperties2_pos)
        self.ui.dockProperties3.resize(dockProperties3_size)
        self.ui.dockProperties3.move  (dockProperties3_pos)
        self.ui.dockProperties4.resize(dockProperties4_size)
        self.ui.dockProperties4.move  (dockProperties4_pos)
        self.ui.dockProperties5.resize(dockProperties5_size)
        self.ui.dockProperties5.move  (dockProperties5_pos)
        self.ui.dockProperties6.resize(dockProperties6_size)
        self.ui.dockProperties6.move  (dockProperties6_pos)
        if config.ENABLE_STATISTIC_OBJ_INFO:
            self.ui.dockObjViewModeInfoWidget.resize(dockObjViewModeInfoWidget_size)
            self.ui.dockObjViewModeInfoWidget.move  (dockObjViewModeInfoWidget_pos)
        
        self.ui.dockAnnotations.resize(dockAnnotations_size)
        self.ui.dockAnnotations.move  (dockAnnotations_pos)
        self.restoreState(state)
        self.ui.actionLocked.setChecked(bool(locked))
        
        self._lastOpenAnnoFileFolderPath = utils.toUTFStr(lastOpenAnnoFileFoderPath)
        
        return                               

    def saveApplicationSettings(self):
        settings = QSettings()
        settings.setValue("MainWindow/Size",        self.size())
        settings.setValue("MainWindow/Position",    self.pos())
        settings.setValue("dockProperties1/Size",        self.ui.dockProperties1.size())
        settings.setValue("dockProperties1/Position",    self.ui.dockProperties1.pos())
        settings.setValue("dockProperties_personbike/Size",        self.ui.dockProperties_personbike.size())
        settings.setValue("dockProperties_personbike/Position",    self.ui.dockProperties_personbike.pos())
        settings.setValue("dockProperties2/Size",        self.ui.dockProperties2.size())
        settings.setValue("dockProperties2/Position",    self.ui.dockProperties2.pos())
        settings.setValue("dockProperties3/Size",        self.ui.dockProperties3.size())
        settings.setValue("dockProperties3/Position",    self.ui.dockProperties3.pos())
        settings.setValue("dockProperties4/Size",        self.ui.dockProperties4.size())
        settings.setValue("dockProperties4/Position",    self.ui.dockProperties4.pos())
        settings.setValue("dockProperties5/Size",        self.ui.dockProperties5.size())
        settings.setValue("dockProperties5/Position",    self.ui.dockProperties5.pos())
        settings.setValue("dockProperties6/Size",        self.ui.dockProperties6.size())
        settings.setValue("dockProperties6/Position",    self.ui.dockProperties6.pos())
        if config.ENABLE_STATISTIC_OBJ_INFO:
            settings.setValue("dockObjViewModeInfoWidget/Size",        self.ui.dockObjViewModeInfoWidget.size())
            settings.setValue("dockObjViewModeInfoWidget/Position",    self.ui.dockObjViewModeInfoWidget.pos())
        
        settings.setValue("dockAnnotations/Size",        self.ui.dockAnnotations.size())
        settings.setValue("dockAnnotations/Position",    self.ui.dockAnnotations.pos())
        
        settings.setValue("MainWindow/State",       self.saveState())
        settings.setValue("MainWindow/ViewsLocked", self.ui.actionLocked.isChecked())
        ccf = self.labeltool.getCurrentContainerFilename()
        if ccf:
            folder = os.path.dirname(ccf)
        else:
            folder = ''

        settings.setValue("AnnoFile/Folder", folder) 
        # settings.setValue("LastFile", None) #ccf

        
    # ----------------------------------------------------------------------------------
    # return value:
    # False - havn't save change to annotation file and should not exit app
    # True  - file saving success, no change exist any longer, and you can exit app
    # ----------------------------------------------------------------------------------
    def okToContinue(self):
        # LOG.info("okToContinue ... self.labeltool.model().dirty() = {}".format(self.labeltool.model().dirty()))
        if self.labeltool.model().dirty():
            reply = QMessageBox.question(self,
                    config.GUI_SAVE_CHANGE_MSGBOX_TITLE_TEXT % (config.APP_NAME),
                    config.GUI_SAVE_CHANGE_MSGBOX_QUESTION_TEXT,
                    QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                return self.fileSave()
        return True
        
    def fileNew(self):
        if self.okToContinue():
            self.labeltool.clearAnnotations()

    def fileOpen(self):
        if not self.okToContinue():
            return
        
        path = self._lastOpenAnnoFileFolderPath    # path = '.'

        # filename = self.labeltool.getCurrentContainerFilename()
        # if (filename is not None) and (len(filename) > 0):
        #     path = QFileInfo(filename).path()

        format_str = ' '.join(self.labeltool.getAnnotationFilePatterns())
        fname = QFileDialog.getOpenFileName(self, 
                config.GUI_OPEN_ANNOTATIONS_DIALOG_TITLE_TEXT % config.APP_NAME, path,
                config.GUI_OPEN_ANNOTATIONS_DIALOG_OPENTYPE_TEXT % (format_str))

        # tfname = fname
        tfname = unicode(fname.toUtf8(), 'utf8', 'ignore')
        
        if len(tfname) > 0:
            self.labeltool.loadAnnotations(tfname)

            # ==== zx add @ 20151113 to automatically display first image after loading a annotation file via "open annotatons " menu ====
            # goto to first image
            self.labeltool._current_image = None
            LOG.info("fileOpen call labeltool.gotoIndex(0) ...")
            self.labeltool.gotoIndex(0)
            # ==== zx add end ====
                           

    def fileSave(self):
        filename = self.labeltool.getCurrentContainerFilename()
        if filename is None:
            return self.fileSaveAs()
        return self.labeltool.saveAnnotations(filename)

    def fileSaveAs(self):
        # folder = '.'  
        ccf = self.labeltool.getCurrentContainerFilename()
        if ccf:
            folder = os.path.dirname(ccf)
        else:
            folder = ''
        
        format_str = ' '.join(self.labeltool.getAnnotationFilePatterns())
        fname = QFileDialog.getSaveFileName(self,
                config.GUI_SAVE_ANNOTATIONS_DIALOG_TITLE_TEXT % config.APP_NAME, folder,
                config.GUI_SAVE_ANNOTATIONS_DIALOG_SAVETYPE_TEXT % (format_str))

        fnameutf = utils.toUTFStr(fname)
        if fnameutf and (len(fnameutf) > 0):
               return self.labeltool.saveAnnotations(fnameutf)
        return False

    def addImageFiles(self):
        mediatype = 0
        numVideoFiles = sum([ 1 if isinstance(i, VideoFileModelItem) else 0 for i in self.labeltool._model.root().children() ])
        if numVideoFiles > 0:
            msg = config.GUI_ONE_VIDEO_FILE_OR_MULTIPLE_IMG_FILES_IS_ALLOWED_TEXT
            QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
            return None
                    
        fnameList = self.openFileDialog(mediatype)
        firstFile = None
        if fnameList:
            for i in xrange(len(fnameList)):
                fname = fnameList[i]
                # LOG.info(u"[ZXD] addImageFile for fname = {}".format(fname))
                for pattern in image_types:
                    if fnmatch.fnmatch(fname, pattern):
                        # LOG.info(u"call addMediaFile for {}".format(fname)
                        mediaFileItem, errorForFileHasBeenAdded = self.labeltool.addImageFile(fname)
                        
                        if (mediaFileItem is None) and (not errorForFileHasBeenAdded):
                            msg = config.GUI_IMPORT_VIDEO_FAILURE_TIP.format(fname)
                            QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
                            break
                        
                        if (mediaFileItem is None) and (errorForFileHasBeenAdded):
                            msg = config.GUI_IMPORT_VIDEO_FAILURE_FOR_HAS_ALREADY_ADDED_TIP.format(fname)
                            QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
                            break
                            
                        if firstFile is None:
                            firstFile = mediaFileItem    
        
        if firstFile:
            # === zx add @ 20161113 to display image automatically after loading image ====
            self.labeltool.setCurrentImage(firstFile) 
            self.labeltool._model.setDirty(False)
            # === zx add @ 20161113 end ===================================================
                        
        return


    def addVideoFileWithFrmIntervalDialog(self):
        mediatype = 1
        # numVideoFiles = sum([ 1 if isinstance(i, VideoFileModelItem) else 0 for i in self.labeltool._model.root().children() ])
        # if numVideoFiles > 0:
        numFiles = self.labeltool._model.root().numFiles()
        if numFiles > 0:
            msg = config.GUI_ONE_VIDEO_FILE_OR_MULTIPLE_IMG_FILES_IS_ALLOWED_TEXT
            QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
            return None
            
        fnameList = self.openFileDialog(mediatype)
        if fnameList and len(fnameList) > 1:
            msg = config.GUI_ONE_VIDEO_FILE_OR_MULTIPLE_IMG_FILES_IS_ALLOWED_TEXT
            QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
            return None

        fname = fnameList[0]
        if fname is None or fname == "":
           msg = config.GUI_SPECIFY_VIDEO_FILE_TIP
           self.labeltool.statusMessage.emit(msg, 1000)
           return
     
        dlg = setVideoFramesIntervalDialog(self, self.addMediaFile, fname)
        dlg.show()


       
    def openFileDialog(self, mediaType):
        path = self._lastOpenAnnoFileFolderPath    # path = '.'
        
        # filename = self.labeltool.getCurrentContainerFilename()
        # if (filename is not None) and (len(filename) > 0):
        #     path = QFileInfo(filename).path()
        #     path = unicode(path)

        # print ("openFileDialog 961 from path {}....".format(path)) 
        if mediaType == 0:
            fnameList = QFileDialog.getOpenFileNames(self, config.GUI_OPEN_IMG_FILE_DIALOG_TITLE.format(config.APP_NAME),   path, config.GUI_OPEN_IMG_FILE_DIALOG_FILE_TYPE_TEXT.format  (' '.join(image_types)))
        else:
            fname = QFileDialog.getOpenFileName(self, config.GUI_OPEN_VIDEO_FILE_DIALOG_TITLE.format(config.APP_NAME), path, config.GUI_OPEN_VIDEO_FILE_DIALOG_FILE_TYPE_TEXT.format(' '.join(video_types)))
            fnameList = []
            fnameList.append(fname)
            
        # LOG.info(u"openFileDialog.. 1 - fname = {}".format(fname))
        if len(fnameList) == 0:
            return None, None

        _fnameList = []
        for fname in fnameList:
            _fname = unicode(fname)
            _fnameList.append(_fname)
            
            # if os.path.isabs(_fname):
            #    _fname = os.path.relpath(_fname, path)
        
        return _fnameList
        
    
    def addMediaFile(self, fname, videoFrmsInterval):

        mediaFileItem, errorForFileHasBeenAdded = self.labeltool.addVideoFile(fname, videoFrmsInterval)
        if mediaFileItem is not None and mediaFileItem.rowCount() > 0:
            LOG.warning("video file has {} frames!".format(mediaFileItem.rowCount()))
        else:
            LOG.warning("video file has no frames!")
            # self.labeltool.statusMessage.emit(config.GUI_IMPORT_VIDEO_FAILURE_TIP.format(fname), 2000)
            msg = config.GUI_IMPORT_VIDEO_FAILURE_TIP.format(fname)
            QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
            return None

        # === zx add @ 20161113 to display image automatically after loading image ====
        self.labeltool.statusMessage.emit(config.GUI_IMPORT_VIDEO_SUCCESS_TIP.format(fname), 2000)
        self.labeltool.setCurrentImage(mediaFileItem.childAt(0))
        self.labeltool._model.setDirty(False)
        # === zx add @ 20161113 end ===================================================

        return mediaFileItem

    def onViewsLockedChanged(self, checked):
        features = QDockWidget.AllDockWidgetFeatures
        if checked:
            features = QDockWidget.NoDockWidgetFeatures 

        self.ui.dockProperties1.setFeatures(features)
        self.ui.dockProperties_personbike.setFeatures(features)   
        self.ui.dockProperties2.setFeatures(features)
        self.ui.dockProperties3.setFeatures(features)
        self.ui.dockProperties4.setFeatures(features)
        self.ui.dockProperties5.setFeatures(features)
        self.ui.dockProperties6.setFeatures(features)
        if config.ENABLE_STATISTIC_OBJ_INFO:
            self.ui.dockObjViewModeInfoWidget.setFeatures(features)
        self.ui.dockAnnotations.setFeatures(features)


    ###
    ### global event handling
    ###______________________________________________________________________________
    def closeEvent(self, event):
        LOG.info("self.labeltool.model() {} dirty() {}..".format(self.labeltool.model(), self.labeltool.model().dirty()))
        
        # ============================== zx comment start ===================================
        # self.okToContinue() return value:
        # False - havn't save change to annotation file and should not exit app
        # True  - file saving success, no change exist any longer, and you can exit app
        # ============================== zx comment end  ====================================
        shouldExitApp = self.okToContinue()

        # LOG.info(u"MainWindow.closeEvent received! Should Exit? - {} ".format(shouldExitApp))

        if shouldExitApp:
            self.saveApplicationSettings()
            self.exitGuiMainWindow.emit()
        else:
            event.ignore()
        

    def about(self):
        QMessageBox.about(self, config.GUI_ABOUT_DIALOG_TITLE % config.APP_NAME, config.GUI_ABOUT_DIALOG_TEXT % (config.APP_NAME, config.VERSION, config.ORGANIZATION_DOMAIN, config.ORGANIZATION_DOMAIN))

    def callback(self,caseStr=''):
        taskid = caseStr.split('&')[1]
        jsonpath = self.labeltool.getCurrentContainerFilename()
        print taskid+','+jsonpath
        timeseconds = str(time.time())
        resourceid = timeseconds[:timeseconds.find(".")]
        self.ftp = Ftp(taskid,jsonpath,resourceid,self)
        remotejsonpath = self.ftp.uploadPic()
        add_result = dbutil.add_resource(taskid,resourceid,remotejsonpath)
        print add_result
    def importNet(self):
        fruit = dbutil.get_task_list()
        self.s = StringListDlg(fruit,self.callback,self)
        self.s.show()

    # def createContextMenuAction(self):
    #     self.action_group = QAction("Group", self)
    #     self.action_group.setCheckable(True)
    #     # connect(firstChannel, SIGNAL(triggered()), this, SLOT(firstChannelSlot()))
    #      
    # def contextMenuEvent(self, event): 
    #     menu = QMenu(self) 
    #     menu.addAction(self.action_group)
    #     menu.addSeparator()  
    #     menu.addSeparator()  
    #     menu.exec_(event.globalPos())
 

class setVideoFramesIntervalDialog(QWidget):

    def __init__(self, parent = None, exitDialogSlot = None, exitDialogSlotArg1 = None):
        QWidget.__init__(self, parent)

        self._exitDialogSlot = exitDialogSlot
        self._exitDialogSlotArg1 = exitDialogSlotArg1

        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.Dialog)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowCloseButtonHint)

        # zx comment: must be ApplicationModal. otherwise, this dialog cannot block following codes in same thread
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setEnabled(True)

        self._gLayout = QGridLayout()

        self._sliderWidget = QSlider(QtCore.Qt.Horizontal)

        self._sliderWidget.setMinimum(config.GUI_VIDEO_FRME_INTERVAL_MIN_VALUE)
        self._sliderWidget.setMaximum(config.GUI_VIDEO_FRME_INTERVAL_MAX_VALUE)
        self._sliderWidget.setValue(config.GUI_VIDEO_FRME_INTERVAL_DEFAULT_VALUE)

        self._lineEditWidget = QLineEdit(str(config.GUI_VIDEO_FRME_INTERVAL_DEFAULT_VALUE))
        self._lineEditWidget.setValidator(QIntValidator(config.GUI_VIDEO_FRME_INTERVAL_MIN_VALUE, config.GUI_VIDEO_FRME_INTERVAL_MAX_VALUE))
        self._buttonWidget = QPushButton(config.GUI_OK_DISPLAYTEXT)
        utils.set_qobj_stylesheet(self._buttonWidget, 'QPushButton', '#C0C0C0', '#ff0000', '#909090', '#0080FF')

        # font = QFont('Decorative', weight=QFont.Bold)
        self._labelWidget = QLabel(u'<font color="red">{}</font>'.format(config.GUI_SET_VIDEO_FRME_INTERVAL_DIALOG_TEXT))
        self._labelWidget.setFont(QFont("Timers", 16, QFont.Bold))

        self._sliderWidget.resize(config.GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_SLIDER_WIDTH,  config.GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_SLIDER_HEIGHT)
        self._lineEditWidget.setFixedWidth(config.GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_LINEEDIT_WIDTH)
        self._lineEditWidget.setFixedHeight(config.GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_SLIDER_HEIGHT)
        self._buttonWidget.setFixedWidth(config.GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_BUTTON_WIDTH)
        self._buttonWidget.setFixedHeight(config.GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_SLIDER_HEIGHT)
        self._labelWidget.setFixedHeight(config.GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_SLIDER_HEIGHT)

        self.resize(config.GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_WIDTH, config.GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_HEIGHT)

        self._gLayout.addWidget(self._labelWidget, 0, 0)
        self._gLayout.addWidget(self._sliderWidget,   1, 0)
        self._gLayout.addWidget(self._lineEditWidget, 1, 1)
        self._gLayout.addWidget(self._buttonWidget,   2, 1)

        self.setLayout(self._gLayout)
        self.setWindowTitle(config.GUI_SET_VIDEO_FRME_INTERVAL_DIALOG_TITLE)

        self._sliderWidget.valueChanged.connect(self.setLineEditValue)
        self._lineEditWidget.textEdited.connect(self.getLineEditValue)
        self._buttonWidget.clicked.connect(self.exitDialog)


    def setLineEditValue(self, value):
        pos = self._sliderWidget.value()
        self._lineEditWidget.setText('{}'.format(pos))

    def getLineEditValue(self, valueStr):
        self._sliderWidget.setValue(eval(str(valueStr)))

    def exitDialog(self):
        frmInterval = self._sliderWidget.value()
        self.close()
        if self._exitDialogSlot is not None:
           self._exitDialogSlot(self._exitDialogSlotArg1, frmInterval)

class StringListDlg(QDialog):
    """
    主对话框
    """
    def __init__(self, fruit,callback,parent=None):
        super(StringListDlg, self).__init__(parent)
        self.callback = callback
        self.fruit = fruit
        self.fruits = QListWidget()
        self.fruits.addItems(fruit)
        btn_add = QPushButton(u'&确认...')
        btn_close = QPushButton('&Close')
        v_box = QVBoxLayout()
        v_box.addWidget(btn_add)
        v_box.addStretch(1)
        v_box.addWidget(btn_close)
        h_box = QHBoxLayout()
        h_box.addWidget(self.fruits)
        h_box.addLayout(v_box)
        self.setLayout(h_box)
        self.resize(QSize(400,300))
        self.setWindowTitle(u'任務列表')
        btn_add.clicked.connect(self.add)
        btn_close.clicked.connect(self.close)

    def add(self):
        self.callback(self.fruits.currentItem().text())

    def close(self):
        self.done(0)


#弹出对话框
#add
class FruitDlg(QDialog):
    def __init__(self, title, fruit=None, parent=None):
        super(FruitDlg, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        label_0 = QLabel(title)
        label_0.setWordWrap(True)#让标签字换行
        self.fruit_edit = QLineEdit(fruit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        validator = QRegExp(r'[^\s][\w\s]+')
        self.fruit_edit.setValidator(QRegExpValidator(validator, self))
        v_box = QVBoxLayout()
        v_box.addWidget(label_0)
        v_box.addWidget(self.fruit_edit)
        v_box.addWidget(btns)
        self.setLayout(v_box)
        self.fruit = None

    def accept(self):
        #OK按钮
        self.fruit = unicode(self.fruit_edit.text())
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

class Ftp():
    def __init__(self, taskid, jsonpath,resourceid, parent=None):
        self.taskid = taskid
        self.jsonpath = jsonpath
        self.resourceid = resourceid

    def ftpconnect(self,host, username, password):
        ftp = FTP()
        ftp.connect(host, 21)
        ftp.login(username, password)
        return ftp

    def uploadfile(self,ftp, remotepath, localpath):
        bufsize = 1024
        fp = open(localpath, 'rb')
        ftp.storbinary('STOR ' + remotepath, fp, bufsize)
        ftp.set_debuglevel(0)
        fp.close()

    def uploadPic(self):
        f = open(self.jsonpath)
        strJson = json.load(f)
        ftp = self.ftpconnect("192.168.0.130", "u2amftp", "123456")
        remotepath = '/home/ftp/'+str(datetime.datetime.now().year)+'/'+str(datetime.datetime.now().month)+'/'+str(datetime.datetime.now().day)+'/'+self.taskid+'/'+self.resourceid+'/'
        remotejsonpath = remotepath+self.resourceid+'.json'
        self.create_dir(ftp,remotepath)
        labels = strJson['labels']
        local_base_path = self.jsonpath[:self.jsonpath.rfind('/')+1]
        for label in labels:
            file_remote_path = remotepath+label['filename']
            filelocalname = local_base_path+label['filename']
            file_handler = open(filelocalname, "rb")
            ftp.storbinary('STOR %s'%file_remote_path, file_handler, 4096)
            file_handler.close()
        json_file_handler = open(self.jsonpath, "rb")
        ftp.storbinary('STOR %s'%remotejsonpath, json_file_handler, 4096)
        json_file_handler.close()
        ftp.quit()
        return remotejsonpath

    def create_dir(self,ftp,dir_path):
        paths = str(dir_path).split('/')
        base_path = '/home/ftp'
        for path in paths:
            ftp.cwd(base_path)
            chirld = ftp.nlst()
            if ''!=path and 'home' != path and 'ftp' != path:
                base_path = base_path+'/'+path
                print base_path
            if ''!=path and  'home' != path and 'ftp' != path and path not in chirld:
                ftp.mkd(base_path)