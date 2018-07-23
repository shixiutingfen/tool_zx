# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

#!/usr/bin/python
import logging, os
from PyQt4 import QtCore, QtGui
from sloth.gui.floatinglayout import FloatingLayout
from PyQt4.QtGui import QMainWindow, QSizePolicy, QWidget, QVBoxLayout, QAction, QMenu, \
        QLabel, QMessageBox, QButtonGroup, QFileDialog, QCheckBox, QGroupBox, QTextEdit, \
        QDockWidget, QProgressBar, QSlider, QHBoxLayout, QRadioButton, QLineEdit, QPushButton, QGridLayout, QIntValidator, QDialog, QFont
from sloth.gui import utils
from sloth.conf import config
from sloth.core import commands


GUIDIR = os.path.join(os.path.dirname(__file__))
LOG = logging.getLogger(config.LOG_FILE_NAME)

"""
from PIL import Image, ImageDraw
import numpy as np
def MultiImgFilesAvgFusion(imgFilesFolder, AccFileSavePath):
    list_dirs = os.walk(imgFilesFolder)
    imgsCnt = 0
    AccImgData = None
    ImgMode = None
    for root, dirs, files in list_dirs:
        for f in files:
            thisfile = os.path.join(root, f)
            print "[INF] find file ", thisfile, " ..."
            ImgObj = Image.open(thisfile)
            ImgMode = ImgObj.mode
            ImgData = np.array(ImgObj)
            print ImgData.dtype
            if imgsCnt <= 0:
                AccImgData = ImgData.astype(np.int32)
            else:
                AccImgData += ImgData
            imgsCnt += 1
            print ImgData.shape, ImgData.dtype, AccImgData.dtype

    AccImgData = (AccImgData / imgsCnt).astype(np.uint8)
    print AccImgData.dtype
    Image.fromarray(AccImgData, ImgMode).save(AccFileSavePath)
"""

class statisticsForCurLoadedJsonFileDialog(QWidget):

    def __init__(self, parent = None, mainwindow = None, exitDialogSlot = None, exitDialogSlotArg1 = None, exitDialogSlotArg2 = None):
        QWidget.__init__(self, parent)

        self._exitDialogSlot = exitDialogSlot
        self._exitDialogSlotArg1 = exitDialogSlotArg1
        self._exitDialogSlotArg2 = exitDialogSlotArg2
        self._mainwindow = mainwindow

        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.Dialog)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowCloseButtonHint)

        # zx comment: must be ApplicationModal. otherwise, this dialog cannot block following codes in same thread
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setEnabled(True)

        self._gLayout = QVBoxLayout() # QGridLayout()
        self.checkbox_groups = []
        self.widgetsInfo = {}   # format: { widgetGroupName: [[widgetObj, widgetName], ....],  }
    
        for displayOrder, groupElementsList  in config.STATISTICS_PLUGIN_DISPLAY_ELEMENTS_DICT.items():
           groupName = groupElementsList[0]
           groupElementsList = groupElementsList[1]
           group_box = QGroupBox(str(groupName), self)
           flayout = FloatingLayout()

           # Create buttongroup
           checkbox_group = QButtonGroup(group_box)
           checkbox_group.setExclusive(False)
           checkboxs = []
           for i, token in enumerate(groupElementsList):
               # print "i = {} token = {}".format(i, token)

               if token == config.ANNOTATION_UPPER_COLOR_TOKEN or token == config.ANNOTATION_LOWER_COLOR_TOKEN or token == config.ANNOTATION_VEHICLE_COLOR_TOKEN:
                   if token == config.ANNOTATION_UPPER_COLOR_TOKEN or token == config.ANNOTATION_LOWER_COLOR_TOKEN:
                       editor = self._mainwindow.property_editor4
                   else:
                       editor = self._mainwindow.property_editor6
                   names_list, texts_list, displaycolors_list = editor.get_group_config(token)
                   for t, text in enumerate(texts_list):
                       checkbox = QCheckBox(text)

                       # get widget display color
                       if token == config.ANNOTATION_UPPER_COLOR_TOKEN or token == config.ANNOTATION_LOWER_COLOR_TOKEN or token == config.ANNOTATION_VEHICLE_COLOR_TOKEN:
                           thisCheckboxBkgColorChecked = displaycolors_list[t]
                           thisCheckboxBkgColor = thisCheckboxBkgColorChecked
                       else:
                           thisCheckboxBkgColorChecked = displaycolors_list[t]
                           thisCheckboxBkgColor = None

                           # calc widget text color
                           # thisCheckboxBkgColorChecked string pattern: #123456
                       txtColorChecked = None
                       if thisCheckboxBkgColorChecked is not None:
                           import math
                           rgba = utils.hexColorStrToRGBA(thisCheckboxBkgColorChecked)
                           distance = math.sqrt((rgba[0] - 255) ** 2 + (rgba[1] - 255) ** 2 + (rgba[2] - 255) ** 2)
                           txtColorChecked = '#ffffff' if distance > config.GUI_COLOR_TAG_TEXT_BLACKWHITE_TOGGLE_THRESHOLD else '#000000'

                       txtColor = txtColorChecked if token == config.ANNOTATION_UPPER_COLOR_TOKEN or token == config.ANNOTATION_LOWER_COLOR_TOKEN or token == config.ANNOTATION_VEHICLE_COLOR_TOKEN else None

                       desc = utils.set_qobj_stylesheet(checkbox, 'QCheckBox', thisCheckboxBkgColor,
                                                        txtColor, thisCheckboxBkgColorChecked,
                                                        txtColorChecked)
                       checkbox_group.addButton(checkbox)
                       flayout.addWidget(checkbox)
                       # print u"checkbox_group.addcheckbox {}".format(checkbox.text())
                       checkbox.clicked.connect(self.onClickedWidget)
                       checkbox.setChecked(False)
                       checkboxs.append([checkbox, names_list[t]])
               else:
                   checkbox = QCheckBox(token)
                   desc = utils.set_qobj_stylesheet(checkbox, 'QCheckBox', "#ffffff", "#000000", "#ffffff", "#000000")
                   checkbox_group.addButton(checkbox)
                   flayout.addWidget(checkbox)
                   # print "checkbox_group.addButton {}".format(checkbox)
                   checkbox.clicked.connect(self.onClickedWidget)
                   checkboxs.append([checkbox, token])

              
           all = QRadioButton("All")
           desc = utils.set_qobj_stylesheet(all, 'QRadioButton', "#ffffff", "#000000", "#ffffff", "#000000")
           checkbox_group.addButton(all)
           flayout.addWidget(all)
           all.clicked.connect(self.selectAllWidgetsInCurrentGroup)
           checkboxs.append([all, "all"])
           group_box.setLayout(flayout)
           # add this checkboxgroup to layout
           self._gLayout.addWidget(group_box)
           
           self.checkbox_groups.append(checkbox_group)
           self.widgetsInfo[groupName] = checkboxs

        self._filtersGoup = QGroupBox("Filters", self)
        self._filtersGoup_layout = QHBoxLayout()
        self._filtersGoup.setLayout(self._filtersGoup_layout)
        self._gLayout.addWidget(self._filtersGoup)

        self._buttonStatisticWithFilterWidget = QPushButton("STATISTICS with filters")
        utils.set_qobj_stylesheet(self._buttonStatisticWithFilterWidget, 'QPushButton', '#C0C0C0', '#ff0000', '#909090', '#0080FF')
        self._buttonStatisticWithFilterWidget.clicked.connect(self.onClickedStatisticWithFilter)
        self._filtersGoup_layout.addWidget(self._buttonStatisticWithFilterWidget)

        """
        self._buttonStatisticAllColorsWidget = QPushButton("STATISTICS all colors")
        utils.set_qobj_stylesheet(self._buttonStatisticAllColorsWidget, 'QPushButton', '#C0C0C0', '#ff0000', '#909090', '#0080FF')
        self._buttonStatisticAllColorsWidget.clicked.connect(self.onClickedStatisticAllColors)
        self._filtersGoup_layout.addWidget(self._buttonStatisticAllColorsWidget)
        """

        self._buttonApplyFilterOnViewModeWidget = QPushButton("Apply filters on view mode")
        utils.set_qobj_stylesheet(self._buttonApplyFilterOnViewModeWidget, 'QPushButton', '#C0C0C0', '#ff0000', '#909090', '#0080FF')
        self._buttonApplyFilterOnViewModeWidget.clicked.connect(self.onClickedApplyFilterOnViewMode)
        self._filtersGoup_layout.addWidget(self._buttonApplyFilterOnViewModeWidget)

        self._statLabelWidget = QLabel(u'<font color="red">{}</font>'.format("statistics result"))
        self._statLabelWidget.setFont(QFont("Timers", 16, QFont.Bold))
        self._gLayout.addWidget(self._statLabelWidget)

        self._statResultTxtWidget = QTextEdit('')
        self._gLayout.addWidget(self._statResultTxtWidget)


        self.setLayout(self._gLayout)
        self.setWindowTitle(config.STATISTIC_OR_APPLY_OBJVIEWFILTER_FOR_CUR_JSON_FILE_PLUGIN_DISPLAYTEXT)
        self.resize(1000, 800)

        utils.centerGuiWidget(self)
        return


    def onClickedStatisticWithFilter(self):
        widget = self.sender()
        infoToStatistic = self.getCheckedWidgetsInfo()
        # print u"infoToStatistic = {}".format(infoToStatistic)
        if self._mainwindow == None:
            return

        filters = getFilters(infoToStatistic, self.widgetsInfo)

        if filters is None or (not filters):
            self._statResultTxtWidget.setText(
                "No any annotation is found!\n\nFilter hasn't been set or filter is invalid!")
            return

        # print u"\nfilters = {}".format(filters)

        anno = self._mainwindow.labeltool._model.root().getAnnotations(recursive=True)
        matchcnt = applyFilterOnMultipleImages(anno, filters)

        filtersDesc = getFilterTextDescription(filters)
        self._statResultTxtWidget.setText("infoToStatistic {} \nFilter {} Totally {} annotation are found!\n\n".format(infoToStatistic, filters, matchcnt))
        return
    
    def onClickedWidget(self):
        pass
        # widget = self.sender()
        # if widget.isChecked():
        #    print u"{} is checked".format(widget.text())

    def selectAllWidgetsInCurrentGroup(self):
        widget = self.sender()
        
        if widget.isChecked():
            # print u"{} is checked".format(widget.text())

            for groupname, checkboxs in self.widgetsInfo.items():
                widgetnum = len([widget for checkbox in checkboxs if checkbox[0] == widget])
                # print u"groupname = {} widgetnum = {} widget = {}".format(groupname, widgetnum, widget.text())
                if widgetnum <= 0:
                    continue
                # print "checkboxs = {}".format(checkboxs)
                for i, checkbox in enumerate(checkboxs):
                    if checkbox[0] != widget:
                        # checkbox[0].setChecked(True)
                        checkbox[0].setEnabled(False)
        else:
            for groupname, checkboxs in self.widgetsInfo.items():
                widgetnum = len([widget for checkbox in checkboxs if checkbox[0] == widget])
                if widgetnum <= 0:
                    continue
                for i, checkbox in enumerate(checkboxs):
                    if checkbox[0] != widget:
                       checkbox[0].setEnabled(True)
                    
    def getCheckedWidgetsInfo(self):
        number = 0
        widgets = []
        
        checkedWidgetsNameAmongGroups = {}
        for checkboxsgroupname, checkboxslist in self.widgetsInfo.items():
            # checkedNames = [unicode(i[0].text()) for i in checkboxslist if i[0].isChecked() ]
            checkedNames = [unicode(i[1]) for i in checkboxslist if i[0].isChecked() ]
            checkedWidgetsNameAmongGroups[checkboxsgroupname] = checkedNames
            
        return checkedWidgetsNameAmongGroups
        

    def exitDialog(self):
        self.close()
        if self._exitDialogSlot is not None:
           self._exitDialogSlot(self._exitDialogSlotArg1, self._exitDialogSlotArg2)

        return

    def onClickedStatisticAllColors(self):
        # if ( self._mainwindow.labeltool._model.isEmpty()):
        #     anno = self._mainwindow.labeltool._model.root().getAnnotations(recursive=True)
        desc = statisticAllColorsForOneJsonFile(None, self._mainwindow.labeltool._model.root().getAnnotations(recursive=True))
        print "desc = {}".format(desc)
        textdesc = getStatisticsResultTextDescription(desc)
        print "textdesc = {}".format(textdesc)
        self._statResultTxtWidget.setText(textdesc)
        return

    def onClickedApplyFilterOnViewMode(self):
        widget = self.sender()
        infoToStatistic = self.getCheckedWidgetsInfo()
        # print u"infoToStatistic = {}".format(infoToStatistic)
        if self._mainwindow == None:
            return

        filters = getFilters(infoToStatistic, self.widgetsInfo)

        if filters is None or (not filters):
            self._statResultTxtWidget.setText(
                "No any annotation is found!\n\nFilter hasn't been set or filter is invalid!")
            return

        # print u"\nfilters = {}".format(filters)

        self._mainwindow.labeltool._view_filters = filters
        anno = self._mainwindow.labeltool._model.root().getAnnotations(recursive=True)
        matchcnt = applyFilterOnMultipleImages(anno, filters)

        filtersDesc = getFilterTextDescription(filters)
        self._statResultTxtWidget.setText("filterOnViewMode {} \nTotally {} annotation are found!\nNow you can enter objViewMode to view filtered objects!\n\n".format(infoToStatistic, matchcnt))
        return



class statisticsForMultipleJsonFilesDialog(QWidget):

    def __init__(self, parent = None, mainwindow = None, exitDialogSlot = None, exitDialogSlotArg1 = None, exitDialogSlotArg2 = None):
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
            QMessageBox.critical(None, config.GUI_CRITIAL_ERROR_TEXT,config.GUI_INVALID_PATH_TEXT.format(folder ))
            return

        # ----------------------------------------------------------------------------
        # statistics for selected folder
        # ----------------------------------------------------------------------------
        data_path = os.path.normpath(folder)
        resultDesc = ""
        accResult = None
        fileCnt = 0
        for root, dirs, files in os.walk(data_path):
            files = [ fi for fi in files if (fi.endswith(".json") )]
            for name in sorted(files):
                thisfile = os.path.join(root, name)
                fileCnt += 1
                result = statisticAllColorsForOneJsonFile(thisfile, None)
                accResult = accumulateStatisticsResult(result, accResult)
                resultDesc += "========================= file {} ========================\n".format(thisfile)
                resultDesc += getStatisticsResultTextDescription(result)

        accResultDesc = "========================= Totally {} files under folder {} ========================\n".format(fileCnt, _folder)
        accResultDesc+= getStatisticsResultTextDescription(accResult)
        accResultDesc += resultDesc
        # print "accResultDesc = {}".format(accResultDesc)
        # QMessageBox.critical(None, config.GUI_CRITIAL_ERROR_TEXT, accResultDesc)

        # ----------------------------------------------------------------------------
        # display statistics result in dialog
        # ----------------------------------------------------------------------------
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.Dialog)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.WindowCloseButtonHint)

        # zx comment: must be ApplicationModal. otherwise, this dialog cannot block following codes in same thread
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setEnabled(True)

        self._gLayout = QVBoxLayout() # QGridLayout()
        self._statResultTxtWidget = QTextEdit('')
        self._gLayout.addWidget(self._statResultTxtWidget)

        self.setLayout(self._gLayout)
        self.setWindowTitle(config.STATISTIC_FOR_MULTIPLE_JSON_FILES_PLUGIN_DISPLAYTEXT)
        self.resize(1000, 800)

        utils.centerGuiWidget(self)

        self._statResultTxtWidget.setText(accResultDesc)
        return


def getFilters(checkedWidgetsNameAmongGroups, widgetsInfo = None):
    filters = []
    for groupname, value in checkedWidgetsNameAmongGroups.items():
        # print u"groupname = {} value = {}".format(groupname, value)

        if groupname == "ObjType":
            if (value == None) or (not value):
                break
            filters.append([])
            for i, boxname in enumerate(value):
                if boxname == "all":
                    if widgetsInfo:
                        for index, item in enumerate(widgetsInfo[groupname]):
                            if item[1] != boxname:
                                labelkey = "class"
                                labelvalue = item[1]
                                labellevel = 0
                                filters[-1].append((labelkey, labelvalue, labellevel))
                                # print u"filters[-1].append({}, {}, {})".format(labelkey, labelvalue, labellevel)
                else:
                    labelkey = "class"
                    labelvalue = boxname
                    labellevel = 0
                    filters[-1].append((labelkey, labelvalue, labellevel))
                    # print u"filters[-1].append({}, {}, {})".format(labelkey, labelvalue, labellevel)

        if groupname == "PersonBodyType":
            if (value == None):   break
            if (not value):       continue
            filters.append([])
            for i, boxname in enumerate(value):
                if boxname == "all":
                    if widgetsInfo:
                        for index, item in enumerate(widgetsInfo[groupname]):
                            if item[1] != boxname:
                                labelkey = "class"
                                labelvalue = item[1]
                                labellevel = 0
                                filters[-1].append((labelkey, labelvalue, labellevel))
                                # print u"filters[-1].append({}, {}, {})".format(labelkey, labelvalue, labellevel)
                else:
                    labelkey = "class"
                    labelvalue = boxname
                    labellevel = 1
                    filters[-1].append((labelkey, labelvalue, labellevel))
                    # print u"filters[-1].append({}, {}, {})".format(labelkey, labelvalue, labellevel)

        if groupname == config.ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN:
            if (value == None):   break
            if (not value):       continue
            filters.append([])
            for i, boxname in enumerate(value):
                if boxname == "all":
                    if widgetsInfo:
                        for index, item in enumerate(widgetsInfo[groupname]):
                            if item[1] != boxname:
                                labelkey = "class"
                                labelvalue = item[1]
                                labellevel = 0
                                filters[-1].append((labelkey, labelvalue, labellevel))
                                # print u"filters[-1].append({}, {}, {})".format(labelkey, labelvalue, labellevel)
                else:
                    labelkey = "class"
                    labelvalue = boxname
                    labellevel = 1
                    filters[-1].append((labelkey, labelvalue, labellevel))
                    # print u"filters[-1].append({}, {}, {})".format(labelkey, labelvalue, labellevel)

        if groupname == config.ANNOTATION_UPPER_COLOR_TOKEN or groupname == config.ANNOTATION_LOWER_COLOR_TOKEN or groupname == config.ANNOTATION_VEHICLE_COLOR_TOKEN:
            if (value == None):   break
            if (not value):       continue
            filters.append([])

            for i, boxname in enumerate(value):
                if boxname == "all":
                    if widgetsInfo:
                        for index, item in enumerate(widgetsInfo[groupname]):
                            if item[1] != boxname:
                                labelvalue = item[1]
                                labellevel = 1 if groupname == config.ANNOTATION_UPPER_COLOR_TOKEN or groupname == config.ANNOTATION_LOWER_COLOR_TOKEN else 0
                                filters[-1].append((groupname + "0Tag", labelvalue, labellevel))
                                if groupname == config.ANNOTATION_UPPER_COLOR_TOKEN or groupname == config.ANNOTATION_LOWER_COLOR_TOKEN:
                                    filters[-1].append((groupname + "1Tag", labelvalue, labellevel))
                                    filters[-1].append((groupname + "2Tag", labelvalue, labellevel))

                else:
                    labelvalue = boxname
                    labellevel = 1 if groupname == config.ANNOTATION_UPPER_COLOR_TOKEN or groupname == config.ANNOTATION_LOWER_COLOR_TOKEN else 0
                    filters[-1].append((groupname + "0Tag", labelvalue, labellevel))
                    if groupname == config.ANNOTATION_UPPER_COLOR_TOKEN or groupname == config.ANNOTATION_LOWER_COLOR_TOKEN:
                        filters[-1].append((groupname + "1Tag", labelvalue, labellevel))
                        filters[-1].append((groupname + "2Tag", labelvalue, labellevel))

    return filters

def applyFilterOnImage(oneAnno, filters):
    labellevel = 0
    matchcnt = 0
    if oneAnno["class"] == config.ANNOTATION_IMAGE_TOKEN:
        uanno = oneAnno["annotations"]
        for j in uanno:
            matchcnt += 1 if applyFilterOnObj(j, filters) else 0
    elif oneAnno["class"] == config.ANNOTATION_VIDEO_TOKEN:
        uanno = oneAnno["frames"]
        for frame in uanno:
            # print "frame = {}".format(frame)
            # print "frameIdx = {} frame[annotations] = {}".format(frame["frmidx"], frame["annotations"])
            for j in frame["annotations"]:
                matchcnt += 1 if applyFilterOnObj(j, filters) else 0
    return matchcnt

def applyFilterOnMultipleImages(annoList, filters):
    matchcnt = 0
    for i in xrange(len(annoList)):
        matchcnt += applyFilterOnImage(annoList[i], filters)
    return matchcnt

def applyFilterOnObj(oneObjAnno, filters):
    if not filters:
        return True

    isMatch = False
    if oneObjAnno is None or (not oneObjAnno):
        return isMatch

    match_in_andfields = True
    for filter_or_list in filters:
        match_in_orfields = False
        # print "filter_or_list = {}".format(filter_or_list)

        for f in filter_or_list:
            # print "filter = {}".format(f)

            if (f[2] == 0) and (f[0] in oneObjAnno.keys()):
                if ( oneObjAnno[f[0]] == f[1] ):
                    match_in_orfields = True
            elif (f[2] == 1):
                subanno = oneObjAnno.get('subclass', None)
                # print "subanno = {}".format(subanno)
                if subanno != None:
                    tc = len([ f[0] for sa in subanno if f[0] in sa.keys() and sa[f[0]] == f[1] ])
                    if tc > 0:
                        match_in_orfields = True

            # print "thisorfield: match_in_orfields = {} match_in_andfields = {}".format(match_in_orfields, match_in_andfields)

        match_in_andfields &= match_in_orfields
        # print "== thisandfield: match_in_orfields = {} match_in_andfields = {}".format(match_in_orfields, match_in_andfields)

    if match_in_andfields:
        # print "match one annotation: {}".format(oneObjAnno)
        isMatch = True

    return isMatch

def getFilterTextDescription(listInstance):
    if listInstance is None or (not listInstance):
        return ""
    str = "["
    nonlistElementNum = 0
    for i in listInstance:
        if isinstance(i, list):
            tstr = getFilterTextDescription(i)
            if len(str) <= 1:
                str += "\n"
                str += tstr
            else:
                str += tstr
        else:
            nonlistElementNum += 1
            if nonlistElementNum == 1:
                tstr = "{}".format(i)
            else:
                tstr = ",  {}".format(i)
            str += tstr

    str += "]\n"
    return str


def statisticAllColorsForOneJsonFile(jsonFilePath, jsonFileAnno):
    if jsonFileAnno:
        anno = jsonFileAnno
    elif jsonFilePath:
        anno = commands.readAnnoFromAnnotationFile(jsonFilePath)

    if not anno:
        return None

    infoToStatistic = {}
    personcolors = config.getFieldsInClassOptions(config.ANNOTATION_UPPER_COLOR_TOKEN, config.METADATA_ATTR_VALUE_TOKEN)
    vehiclecolors = config.getFieldsInClassOptions(config.ANNOTATION_VEHICLE_COLOR_TOKEN, config.METADATA_ATTR_VALUE_TOKEN)
    desc = ""
    needAddLower = False
    needAddUpper = False
    needAddVehicle = False

    statisticsResult = {}
    displayOrder = 0
    for i in xrange(4):
        if i == 0:
            infoToStatistic = {'ObjType': [u'pedestrain'], 'PersonBodyType': [u'upper'], 'lowercolor': [], 'vehiclecolor': []}
            needAddUpper = True
            needAddLower   = False
            needAddVehicle = False
            targets = personcolors
        elif i == 1:
            infoToStatistic = {'ObjType': [u'pedestrain'], 'PersonBodyType': [u'lower'], 'uppercolor': [], 'vehiclecolor': []}
            needAddLower = True
            needAddUpper   = False
            needAddVehicle = False
            targets = personcolors
        elif i == 2:
            infoToStatistic = {'ObjType': [u'personbike'], 'PersonBodyType': [u'upper'], 'lowercolor': [], 'vehiclecolor': []}
            needAddUpper = True
            needAddLower   = False
            needAddVehicle = False
            targets = personcolors
        elif i == 3:
            infoToStatistic = {'ObjType': [u'vehicle'],    'PersonBodyType': [], 'lowercolor': [], 'uppercolor': []}
            needAddVehicle = True
            needAddLower   = False
            needAddUpper   = False
            targets = vehiclecolors
         
         
        for t in targets:
            if needAddUpper :
                infoToStatistic['uppercolor'] = [t]
            if needAddLower :
                infoToStatistic['lowercolor'] = [t]
            if needAddVehicle :
                infoToStatistic['vehiclecolor'] = [t]

            filters = getFilters(infoToStatistic, widgetsInfo = None)

            filters = []
            for groupname, value in infoToStatistic.items():
                # print u"groupname = {} value = {}".format(groupname, value)
            
                if groupname == "ObjType":
                    if (value == None) or (not value):
                        break
                    filters.append([])
                    for i, boxname in enumerate(value):
                        labelkey = "class"
                        labelvalue = boxname
                        labellevel = 0
                        filters[-1].append((labelkey, labelvalue, labellevel))
                        # print u"filters[-1].append({}, {}, {})".format(labelkey, labelvalue, labellevel)
            
                if groupname == "PersonBodyType":
                    if (value == None):   break
                    if (not value):       continue
                    filters.append([])
                    for i, boxname in enumerate(value):
                        labelkey = "class"
                        labelvalue = boxname
                        labellevel = 1
                        filters[-1].append((labelkey, labelvalue, labellevel))
                        # print u"filters[-1].append({}, {}, {})".format(labelkey, labelvalue, labellevel)
            
                if groupname == config.ANNOTATION_UPPER_COLOR_TOKEN or groupname == config.ANNOTATION_LOWER_COLOR_TOKEN or groupname == config.ANNOTATION_VEHICLE_COLOR_TOKEN:
                    if (value == None):   break
                    if (not value):       continue
            
                    filters.append([])
                    for i, boxname in enumerate(value):
                         labelvalue = boxname
                         labellevel = 1 if groupname == config.ANNOTATION_UPPER_COLOR_TOKEN or groupname == config.ANNOTATION_LOWER_COLOR_TOKEN else 0
                         filters[-1].append((groupname + "0Tag", labelvalue, labellevel))
                         if groupname == config.ANNOTATION_UPPER_COLOR_TOKEN or groupname == config.ANNOTATION_LOWER_COLOR_TOKEN:
                             filters[-1].append((groupname + "1Tag", labelvalue, labellevel))
                             filters[-1].append((groupname + "2Tag", labelvalue, labellevel))

            if filters:
                matchcnt = applyFilterOnMultipleImages(anno, filters)

            # filtersDesc = getFilterTextDescription(filters)
            # print "filterDesc = {}".format(filtersDesc)
            # statisticsResult[filters] = matchcnt
            statisticsResult[str(infoToStatistic)] = [matchcnt, displayOrder]
            displayOrder += 1

    # return desc
    return statisticsResult


def getStatisticsResultTextDescription(statisticsResult):
    desc = ""
    if not statisticsResult:
        return desc
    statisticsList = []
    # convert dict of statisticsResult to list of statisticsList
    for infoToStatistic, matchCntAndDisplayOrderList in statisticsResult.items():
        statisticsList.append((infoToStatistic, matchCntAndDisplayOrderList[0], matchCntAndDisplayOrderList[1]))
    statisticsList = sorted(statisticsList, key = lambda d: d[2], reverse = 0)
    for index, item in enumerate(statisticsList):
        desc += "{} : {}\n".format(item[0], item[1])
    return desc

def accumulateStatisticsResult(curStatisticsResult, accStatisticsResult):
    if not curStatisticsResult:
        return accStatisticsResult
    if not accStatisticsResult:
        accStatisticsResult = curStatisticsResult
    for key, value in curStatisticsResult.items():
        if key in accStatisticsResult.keys():
            org = accStatisticsResult[key][0]
            accStatisticsResult[key][0] += value[0]
        else:
            accStatisticsResult[key] = value

    return accStatisticsResult
