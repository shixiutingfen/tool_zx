# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

"""
This is the core labeltool module.
"""
import os
import sys
import datetime
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from sloth.annotations.model import *
from sloth.annotations.container import AnnotationContainerFactory, AnnotationContainer
from sloth.conf import config
from sloth.core.cli import LaxOptionParser, BaseCommand
from sloth.core.utils import import_callable
from sloth.core.commands import get_commands
from sloth.gui import MainWindow, utils, annotationscene, startupTips, statistics
import logging  
from PIL import Image
import logging.handlers  
import threading
import cv2
import unicodedata

LOG = logging.getLogger(config.LOG_FILE_NAME)



try:
    import okapy.videoio as okv
except ImportError:
    pass



class Logger:
    def __init__(self, logFileName):
        self._logFileName = logFileName  
          
        self._handler = logging.handlers.RotatingFileHandler(self._logFileName, maxBytes = 1024*1024, backupCount = 5)
        # fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'  
        fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(message)s' 
          
        self._formatter = logging.Formatter(fmt)
        self._handler.setFormatter(self._formatter)
          
        self._logger = logging.getLogger(config.LOG_FILE_NAME) 
        self._logger.addHandler(self._handler)
        if config.ENABLE_OUTPUT_LOG_INFO:
            level = config.LOG_INFO_LEVEL_MAPPING.get(config.DEFAULT_OUTPUT_LOG_INFO_LEVEL, logging.CRITICAL)
            self._logger.setLevel(level)  
       

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)
        
    def log(self, msg, *args, **kwargs):
        self._logger.log(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)
        
    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)


	
class LabelTool(QObject):
    """
    This is the main label tool object.  It stores the state of the tool, i.e.
    the current annotations, the containers responsible for loading and saving
    etc.

    It is also responsible for parsing command line options, call respective
    commands or start the gui.
    """
    usage = "\n" + \
            "  %prog [options] [filename]\n\n" + \
            "  %prog subcommand [options] [args]\n"

    help_text = "Sloth can be started in two different ways.  If the first argument\n" + \
                "is any of the following subcommands, this command is executed.  Otherwise the\n" + \
                "sloth GUI is started and the optionally given label file is loaded.\n" + \
                "\n" + \
                "Type '%s help <subcommand>' for help on a specific subcommand.\n\n"

    # Signals
    statusMessage = pyqtSignal(str, int)
    annotationsLoaded = pyqtSignal()
    pluginLoaded = pyqtSignal(QAction)
    # This still emits a QModelIndex, because Qt cannot handle emiting
    # a derived class instead of a base class, i.e. ImageFileModelItem
    # instead of ModelItem
    currentImageChanged = pyqtSignal(bool, bool)
    
    
    # zx add @ 2016-10-15
    newItemIsInserted = pyqtSignal(object, str)
    itemIsDeleted = pyqtSignal(str)

    # TODO clean up --> prefix all members with _
    def __init__(self, parent=None):
        """
        Constructor.  Does nothing except resetting everything.
        Initialize the labeltool with either::

            execute_from_commandline()

        or::

            init_from_config()
        """
        QObject.__init__(self, parent)

        self.clear() 
        self._mainwindow = None 
        self._container_factory = None 
        


    def clear(self):
        self._container = AnnotationContainer()
        self._autoSaveContainer = AnnotationContainer()
        self.latestAutoSaveFileNames = []

        self._imgDir = ""
        self._current_image = None
        self._model = AnnotationModel(self._imgDir, [])

        self.insert_mode_property_editor = None
        self.autoSaveAnnotationFileTimer = None
        self._enableAutoConnectLabelMode = config.DEFAULT_AUTO_CONNECT_LABELS_MODE
        self._view_filters = None
        
    def main_help_text(self):
        """

        Includes a list of all available subcommands.
        """
        usage = self.help_text % self.prog_name
        usage += 'Available subcommands:\n'
        commands = list(get_commands().keys())
        commands.sort()
        for cmd in commands:
            usage += '  %s\n' % cmd
        return usage

    def execute_from_commandline(self, argv=None, enableExitAfterExecution = True):
        """
        TODO
        """
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(argv[0])
        
        self.logger = Logger(config.LOG_FILE_NAME)

        # Preprocess options to extract --settings and --pythonpath.
        # These options could affect the commands that are available, so they
        # must be processed early.
        parser = LaxOptionParser(usage=self.usage,
                                 version=config.VERSION,
                                 option_list=BaseCommand.option_list)
        try:
            options, args = parser.parse_args(self.argv)
        except:
            pass  # Ignore any option errors at this point.

        # Initialize logging
        loglevel = (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG)[int(options.verbosity)]
        logging.basicConfig(level=loglevel,
                            format='%(asctime)s %(levelname)-8s %(name)-30s %(message)s')  #, datefmt='%H:%M:%S.%m')

        # Disable PyQt log messages
        logging.getLogger("PyQt4").setLevel(logging.WARNING)

        # Handle options common for all commands
        # and initialize the labeltool object from
        # the configuration (default config if not specified)
        if options.pythonpath:
            sys.path.insert(0, options.pythonpath)

        self.init_from_config(options.config)

        # check for commands
        try:
            subcommand = args[1]
        except IndexError:
            subcommand = None

        # handle commands and command line arguments
        if subcommand == 'help':
            if len(args) > 2:
                self.fetch_command(args[2]).print_help(self.prog_name, args[2])
                if enableExitAfterExecution:
                    sys.exit(0)
            else:
                sys.stdout.write(self.main_help_text() + '\n')
                parser.print_lax_help()
                if enableExitAfterExecution:
                    sys.exit(0)

        elif self.argv[1:] == ['--version']:
            # LaxOptionParser already takes care of printing the version.
            if enableExitAfterExecution:
                sys.exit(0)

        elif self.argv[1:] in (['--help'], ['-h']):
            sys.stdout.write(self.main_help_text() + '\n')
            parser.print_lax_help()
            if enableExitAfterExecution:
                sys.exit(0)

        elif subcommand in get_commands():
            self.fetch_command(subcommand).run_from_argv(self.argv)
            if enableExitAfterExecution:
                sys.exit(0)

        else:
        
            # popup startup tips dialog
            # --------------------------------------------------------
            # zx comment: below codes cannot implement a modal dialog. why ??? TBC
            # dlg = startupTips.startupTipsDialog()
            # dlg.show()
            # --------------------------------------------------------
            
            # zx comment: this messagebox is annoying. I don't want to see it again
            # QMessageBox.critical(None, config.STARTUP_TIPS_DIALOG_TITLE, config.STARTUP_TIPS_DIALOG_DISPLAYTEXT)

            # Setup GUI
            self._mainwindow = MainWindow(self)
            self._mainwindow.showMaximized()

            # Load plugins
            self.loadPlugins(config.PLUGINS)

            # check if args contain a labelfile filename to load
            if len(args) > 1:
                try:
                    json_file = args[1]
                    if('.json' not in json_file):
                        json_file = os.path.join(json_file, json_file+".json")
						
                    if not os.path.isfile(json_file):
                        if enableExitAfterExecution:
                            print "File {} doesn't exist! Program abort!".format(json_file)
                            sys.exit(0)

                    LOG.info("loadAnnotations json_file = {} ...".format(json_file))
                    self.loadAnnotations(json_file, handleErrors=False)

                    # goto to first image
                    self.gotoIndex(0)
                except Exception as e:
                    LOG.fatal("Error loading annotations: %s" % e)
                    if (int(options.verbosity)) > 1:
                        raise
                    else:
                        if enableExitAfterExecution:
                            sys.exit(1)
            else:
                self.clearAnnotations()

        # start autoSaveAnnoationFile timer
        if self._mainwindow and config.ENABLE_AUTO_SAVE_ANNOTATION_FILE:
            self.autoSaveAnnotationFileTimer = perpetualTimer(config.AUTO_SAVE_ANNOTATION_FILE_TIME_INTERVAL_IN_SECONDS, self.autoSaveAnnotationFile)
            self.autoSaveAnnotationFileTimer.start()
            self._mainwindow.exitGuiMainWindow.connect(self.onExitGuiMainWindow)

    def onExitGuiMainWindow(self):
        LOG.info("enter onExitGuiMainWindow ...")
        if self.autoSaveAnnotationFileTimer is not None:
            LOG.info("self.autoSaveAnnotationFileTimer.cancel() ...")
            self.autoSaveAnnotationFileTimer.cancel()
        
        self.autoSaveAnnotationFile()
        

    def autoSaveAnnotationFile(self):
        try:
            LOG.info("Enter saveAnnotations ...")
            autoSaveFileName = None
            
            autoSaveFileBaseName = ''
            if self._container._filename is not None:
                if os.path.isdir(os.path.dirname(self._container._filename)):
                    autoSaveFileBaseName = os.path.basename(self._container._filename).split(".")[0] + '.'
            
            if len(self.latestAutoSaveFileNames) >= config.LATEST_AUTO_SAVE_FILE_NUMBER:
                # remove oldest filename
                oldestAutoSaveFileName = self.latestAutoSaveFileNames.pop(0)
                if os.path.isfile(oldestAutoSaveFileName):
                    os.remove(oldestAutoSaveFileName)
               
            # ZX TIPS: Be careful that the incantation above won't work if you've already used os.chdir() to change your current working directory!
            # Reference: http://stackoverflow.com/questions/5137497/find-current-directory-and-files-directory
            autoSaveDirName = os.path.dirname(os.path.realpath(__file__)) + "/../../autosave/"
            if not os.path.exists(autoSaveDirName):
                os.makedirs(autoSaveDirName)
            x = datetime.datetime.now()
            fname = "%04d%02d%02d_%02d%02d%02d.json" % (x.year, x.month, x.day, x.hour, x.minute, x.second)
            autoSaveFileName = autoSaveDirName + autoSaveFileBaseName + fname
            self.latestAutoSaveFileNames.append(autoSaveFileName)
            
            self.autoSaveAnnotations(autoSaveFileName)
        except Exception as e:
            print "AutoSaving throw an exception {}".format(str(e))
            return


    def fetch_command(self, subcommand):
        """
        Tries to fetch the given subcommand, printing a message with the
        appropriate command called from the command line if it can't be found.
        """
        try:
            app_name = get_commands()[subcommand]
        except KeyError:
            sys.stderr.write("Unknown command: %r\nType '%s help' for usage.\n" %
                             (subcommand, self.prog_name))
            sys.exit(1)
        if isinstance(app_name, BaseCommand):
            # If the command is already loaded, use it directly.
            klass = app_name
        else:
            # TODO implement load_command_class
            klass = load_command_class(app_name, subcommand)

        # set labeltool reference
        klass.labeltool = self

        return klass

    def init_from_config(self, config_module_path=""):
        """
        Initializes the labeltool from the given configuration
        at ``config_module_path``.  If empty, the default configuration
        is used.
        """
        # Load config
        # print "config_module_path {} ...".format(config_module_path)
        if config_module_path:
            config.update(config_module_path)

        # Instatiate container factory
        self._container_factory = AnnotationContainerFactory(config.CONTAINERS)

    def loadPlugins(self, plugins):
        self._plugins = []
        for plugin in plugins:
            if type(plugin) == str:
                plugin = import_callable(plugin)
            p = plugin(self)
            self._plugins.append(p)
            action = p.action()
            self.pluginLoaded.emit(action)


    def preprocessAnno(self, frmseq_annos_list):

        for index1, value in enumerate(frmseq_annos_list):
            # print "preprocessAnno... index = {} value = {}".format(index1, value)
            thisfrm_annos_list = value.get('annotations', None)
            # print "preprocessAnno... thisfrm_annos_list = {}".format(thisfrm_annos_list)
            thisfrm_annos_newcontainer = {
                    "class": config.DEFAULT_TOP_OBJECT,
                    "height": -1,
                    "width": -1,
                    "x": 0,
                    "y": 0
                }

            indexs_to_remove = []
            for index2, thisanno in enumerate(thisfrm_annos_list):
                thisanno_subclass = thisanno.get('subclass', None)
                # print "preprocessAnno... index2 = {} thisanno = {} ".format(index2, thisanno)
                
                # if not thisanno_subclass:
                #    thisanno['subclass'] = thisanno.pop('class')
                
                ALLOWED_SUBOBJ_KEYS_TUPLE = (
                'x',
                'y',
                'width',
                'height',
                'class',
                'subclass',
                'helmetcolor',
                'helmetcolorTag',
                'licenseplate',
                'uppercolor0',
                'uppercolor0Tag',
                'uppercolor1',
                'uppercolor1Tag',
                'uppercolor2',
                'uppercolor2Tag',
                'lowercolor0',
                'lowercolor0Tag',
                'lowercolor1',
                'lowercolor1Tag',
                'lowercolor2',
                'lowercolor2Tag',
                'billboard' )
                
                for key, v in thisanno.items():
                    # if key != 'x' and key != 'y' and key != 'width' and key != 'height' and key != 'class' and key != 'subclass':
                
                    if key not in ALLOWED_SUBOBJ_KEYS_TUPLE:
                       thisfrm_annos_newcontainer.update({key:v})
                       # print "preprocessAnno... to del {} thisfrm_annos_newcontainer {}...".format(key, thisfrm_annos_newcontainer)
                       del thisanno[key]

                if len(thisanno) == 0:
                    indexs_to_remove.append(index2)
                    
                # print "preprocessAnno... thisanno = {}".format(thisanno)

            if thisfrm_annos_list:
                if indexs_to_remove:
                    for x in indexs_to_remove:
                        thisfrm_annos_list.pop(x)

                thisfrm_annos_newcontainer['subclass'] = thisfrm_annos_list

            value['annotations'] = [ thisfrm_annos_newcontainer ]
            
            # print "preprocessAnno... frmseq_annos_list[{}] = {}".format(index1, frmseq_annos_list[index1])

                 
        return frmseq_annos_list
                
                    
            
    ###
    ### Annoation file handling
    ###___________________________________________________________________________________________
    def loadAnnotations(self, fname, handleErrors=True, popupErrorMsg = True):
        # fname = str(fname)  # convert from QString
        loadSuccess = False
        try:
            self._container = self._container_factory.create(fname)
            self.latestAutoSaveFileNames = []
            self._autoSaveContainer = self._container
            # load() return contents in labels fields in format of list from file
            anno =  self._container.load(fname)
            
            # ============== [PREPROCESSING START] =======================
            if config.ENABLE_TOP_OBJECT_MODE:
                # pre-process annotations loaded from file
                # print "before preprocess ... anno = {}".format(anno)
                anno = self.preprocessAnno(anno)
                # print "after  preprocess ... anno = {}".format(anno)
            # ============== [PREPROCESSING END  ] =======================
            
            self._imgDir = self._container._imgdir
            self._model = AnnotationModel(self._imgDir, anno)
            fnameutf = utils.toUTFStr(fname)
            loadSuccess = True
            LOG.info("createAnnotationModel = {}!".format( self._model))
            msg = config.GUI_LOAD_ANNOTATON_FILE_SUCCESS_TIP.format(fnameutf, self._model.root().numFiles(), self._model.root().numAnnotations())
        except Exception as e:
            if handleErrors:
                msg = config.GUI_LOAD_JSON_FILE_FAIL_MESSAGE.format(str(e))
            else:
                raise

        self.statusMessage.emit(msg, config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS)
        if loadSuccess:
            self.annotationsLoaded.emit()
        else:
            if popupErrorMsg:
                QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
        return

    def annotations(self):
        if self._model is None:
            return None
        return self._model.root().getAnnotations(recursive = True)

    # ============================== zx comment start ===================================
    # return value:
    # False - file saving fail
    # True  - file saving succeed
    # ============================== zx comment end  ===================================
    def saveAnnotations(self, fname):
        success = False
        fnameutf = utils.toUTFStr(fname)
                
        try:
            
            # Get annotations dict
            ann = self._model.root().getAnnotations(recursive = True)
            # LOG.info("[ZXD] saveAnnotations ... getAnnotations {}!".format(ann))
            
            # create new container if the filename is different
            if fname != self._container.filename():
                self._container = self._container_factory.create(fnameutf)
            
            self._container._imgdir = self._imgDir
            
            self._container.save(ann, fname)
            #self._model.writeback() # write back changes that are cached in the model itself, e.g. mask updates

            msg = config.GUI_SAVE_ANNOTATON_FILE_SUCCESS_TIP.format(fnameutf, self._model.root().numFiles(), self._model.root().numAnnotations())
            success = True
            self._model.setDirty(False)
            
            # zx added
            self._mainwindow.setWinTitle(os.path.basename(fnameutf))
 
        except Exception as e:
            msg = config.GUI_SAVE_ANNOTATION_FILE_FAIL_TIP.format(fnameutf, str(e))

        self.statusMessage.emit(msg, config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS)
        return success

    def autoSaveAnnotations(self, _fname):
        success = False
        if _fname is None:
            return success
        
        fname = os.path.abspath(_fname)
        fnameutf = utils.toUTFStr(fname)

        try:
            # create new container if the filename is different
            if fname != os.path.abspath(self._autoSaveContainer.filename()):
                self._autoSaveContainer = self._container_factory.create(fname)

            # Get annotations dict
            ann = self._model.root().getAnnotations(recursive = True)

            self._autoSaveContainer.save(ann, fname)

             
            msg = config.GUI_AUTOSAVE_ANNOTATON_FILE_SUCCESS_TIP.format(fnameutf, self._model.root().numFiles(), self._model.root().numAnnotations(), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            success = True
 
        except Exception as e:
            msg = config.GUI_AUTO_SAVE_ANNOTATION_FILE_FAILE_TIP.format(fnameutf, str(e))

        self.statusMessage.emit(msg, 2000)
        return success
        
    def clearAnnotations(self):
        self.clear()
        self.latestAutoSaveFileNames = []
        LOG.info("clearAnnotations ... self._model = {}".format(self._model))

        #self._model.setBasedir("")
        self.statusMessage.emit('', 1000)
        self.annotationsLoaded.emit()

    def getCurrentContainerFilename(self):
        if self._container:
            return self._container.filename()
        else:
            return None

    ###########################################################################
    # Model stuff
    ###########################################################################

    def model(self):
        return self._model

    def gotoIndex(self, idx):
        if self._model is None:
            return

        current = self._current_image
        LOG.info("AnnotationScene.gotoIndex({}) : current = {}".format(idx, current))
        try:
            if current is None:
                current = next(self._model.iterator(ImageModelItem))
        except StopIteration:
            raise RuntimeError("Could not get next ImageModelItem!")
            

        LOG.info("AnnotationScene.gotoIndex({}) : current is set = {}".format(idx, current))
        next_image = current.getSibling(idx)
        LOG.info("AnnotationScene.gotoIndex({}) : current_image is set = {}".format(idx, next_image))
        if next_image is not None:
            LOG.info("AnnotationScene.gotoIndex({}) : call setCurrentImage({}) ...".format(idx, next_image))
            self.setCurrentImage(next_image, flush = False, display = True)



    def getNextImage(self, cur_image, step = 1):
        next_image = None    
        LOG.info("getNextImage... self._model = {} cur_image = {}".format(self._model, cur_image ))   
        if self._model is not None:
            for i in xrange(step):
                exitLoop = False
                while True:
                   if cur_image is not None:
                       next_image = cur_image.getNextSiblingX()
                       LOG.info("getNextImage... cur_image = {} next_image = {}".format(cur_image, next_image ))   
                   else:
                       next_image = next(self._model.iterator(ImageModelItem))     
                       if next_image is not None:
                           next_image = next_image.getNextSiblingX()                
                   cur_image = next_image
                   LOG.info("getNextImage... cur_image is updated with next_image = {}".format(next_image ))  
                   
                   if next_image is None:
                       exitLoop = True
                       break

                   # print "next_image.annotation = {}".format(GET_ANNOTATION(next_image))
                   # print "next_image['unlabeled'] = {}".format(next_image['unlabeled'])
                   isUnlabeled = next_image['unlabeled']
                   if isUnlabeled:
                      cur_image = next_image
                      continue
                   
                   break
				
                if exitLoop:
                    break
				   
        return next_image
              
                        
    def gotoNextImage(self, step=1, display = True, popTipDialog = True):
        LOG.info("gotoNextImage ... self._current_image = {} step = {}".format(self._current_image, step ))
        next_image = self.getNextImage(self._current_image, step)

        if next_image is not None:
            LOG.info("AnnotationScene.gotoNextImage call setCurrentImage ( {} ) ...".format( next_image))
            self.setCurrentImage(next_image, flush = False, display = True)
        else:
            if popTipDialog:
               msg = config.LAST_OR_FIRST_FRAME_OR_IMAGE_TIP.format(config.LAST_TIP)
               QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
            
        return next_image


                
    def gotoNext(self, step=1):
        """
        # set other GUI widget state
        attention_scene_items = []
        # print "call setWidgetState(sceneItem = {})...".format( sceneItem )
        self.scene().setWidgetState(attention_scene_items)
        """
    
        LOG.info("gotoNext ... self.scene()._sceneViewMode = {} step = {}".format(self.scene()._sceneViewMode, step ))
        if (self.scene()._sceneViewMode == config.IMG_VIEW_MODE):
            return self.gotoNextImage(step, display = True)
        elif (self.scene()._sceneViewMode == config.OBJ_VIEW_MODE):
            return self.gotoNextObjWithFilter(self._view_filters, step)

        return None


    def gotoNextObjWithFilter(self, filter, step=1, popTipDialog = True):
        # print "\n=== gotoNextObjWithFilter(filter = {}) ===".format(filter)
        if filter:
            nextObj = None
            while True:
                nextObj = self.gotoNextObj(step, popTipDialog, immediatelyDisplayObjImg = False)
                if not nextObj:
                    break
                # print "=== ModelItem {} ===".format(GET_ANNOTATION(nextObj))
                isMatch = statistics.applyFilterOnObj(GET_ANNOTATION(nextObj), filter)
                if isMatch:
                    # print "=== isMatch {} ===".format(isMatch)
                    self.displayObj(nextObj)
                    break
            return nextObj

        return self.gotoNextObj(step, popTipDialog, immediatelyDisplayObjImg = True)
            
                    
    def gotoNextObj(self, step=1, popTipDialog = True, immediatelyDisplayObjImg = True):
        
        gotoobj = None
        cur_image = self._current_image
        if (self._model is None) or (cur_image is None):
            return gotoobj
        LOG.info("1: cur_image = {} rowindex = {}".format(cur_image, cur_image.row() if cur_image else None))
        imgend = self.scene().update_objViewModeTopModelItemRowIdxInParent(delta = 1)
        LOG.info("imgend = {} _objViewModeTopModelItemRowIdxInParent = {} ".format(imgend, self.scene()._objViewModeTopModelItemRowIdxInParent))
        parentModelItem = None
        next_image = None
        if imgend: # imgend means there are no any object on current image
            if config.AUTO_SWITCH_TO_IMGVIEW_MODE_WHEN_LAST_OR_FIRST_OBJ:
                self.scene().reset_objViewMode()
                self.toggleDisplayView()
                return None
                
            next_image = cur_image
            while True:
                org = next_image
                LOG.info("gotoNextObj: cur_image = {} rowindex = {}".format(org, org.row() if org else None))
                next_image = self.getNextImage(next_image)
                LOG.info("gotoNextObj: next_image = {} rowindex = {}".format(next_image, next_image.row() if next_image else None))
                if (next_image is None):
                    if popTipDialog:
                        # if isinstance(cur_image, FrameModelItem):
                        #     videoFileName, videoFileItem = self.getFrmParentVideo(cur_image)
                        #     msg = config.LAST_OR_FIRST_OBJ_IN_FRAME_TIP.format(config.LAST_TIP, os.path.basename(videoFileName) if videoFileName else '?')
                        # elif isinstance(cur_image, ImageFileModelItem):
                        #     msg = config.LAST_OR_FIRST_OBJ_IN_IMAGE_TIP.format(config.LAST_TIP)
                        
                        msg = config.NO_MORE_OBJ_TIP
                        QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
                        
                    return None
                else:
                    found = findModelItems(config.OBJ_VIEW_MODE_ALLOWED_TOP_LEVEL_OBJ_TYPE, 1, next_image, 0, next_image.rowCount() - 1, 1, reverse = False)
                    parentModelItem = found[0] if found else None
                    if parentModelItem:
                        LOG.info("AnnotationScene.gotoNextObj call setCurrentImage ( {} ) ...".format( next_image))
                        self.setCurrentImage(next_image, flush = False, display = False)
                        break
                
            if parentModelItem:
                LOG.info("gotoNextObj... try to find a display item! parentModelItem = {}".format(parentModelItem))
                gotoobj = parentModelItem
                if immediatelyDisplayObjImg:
                    self.displayObj(gotoobj)
                return gotoobj
            
            return gotoobj
            
                    
        parentModeItem = self._current_image             
        childModelItem = parentModeItem.childAt(self.scene()._objViewModeTopModelItemRowIdxInParent) if parentModeItem else None
        gotoobj = childModelItem   
        if immediatelyDisplayObjImg:
            self.displayObj(gotoobj)

        return gotoobj   

             
    def displayObj(self, objModelItem):
        # print "displayobj call setCurrentDisplayObjImg(flush = {})...".format(flush)
        self.scene().setCurrentDisplayObjImg(objModelItem, flush = False)  # classAnno branch: last commit: flush = True
        self.scene()._sceneViewMode = config.OBJ_VIEW_MODE
        return
 
 
    def gotoBegin(self):
        LOG.info("gotoBegin ... self.scene()._sceneViewMode = {}".format(self.scene()._sceneViewMode ))
        if (self.scene()._sceneViewMode == config.IMG_VIEW_MODE):
            return self.gotoBeginImage(display = True)
        elif (self.scene()._sceneViewMode == config.OBJ_VIEW_MODE):
            return self.gotoBeginObj()
        
        return None 
        
    def gotoBeginImage(self, display = True):
        LOG.info("gotoBeginImage ... self._current_image = {}".format(self._current_image))
        begin_image = self.getBeginImage(self._current_image)

        if begin_image is not None:
            LOG.info("AnnotationScene.gotoBeginImage call setCurrentImage ( {} ) ...".format( begin_image))
            self.setCurrentImage(begin_image, flush = False, display = True)
            
        return begin_image


    def getBeginImage(self, cur_image):
        begin_image = None    
        LOG.info("getBeginImage... self._model = {} cur_image = {}".format(self._model, cur_image ))   
        if (self._model) and (cur_image):
            begin_image = cur_image.getSibling(0)
            LOG.info("getBeginImage... cur_image = {} begin_image = {}".format(cur_image, begin_image ))   
            
        return begin_image


    def gotoBeginObj(self, popTipDialog = True, immediatelyDisplayObjImg = True):
        gotoobj = None
        parentModelItem = None
        next_image = self.getBeginImage(self._current_image)
        while True:
            LOG.info("gotoBeginObj: next_image = {} rowindex = {}".format(next_image, next_image.row() if next_image else None))
            if (next_image is None):
                if popTipDialog:
                    # if isinstance(cur_image, FrameModelItem):
                    #     videoFileName, videoFileItem = self.getFrmParentVideo(cur_image)
                    #     msg = config.LAST_OR_FIRST_OBJ_IN_FRAME_TIP.format(config.LAST_TIP, os.path.basename(videoFileName) if videoFileName else '?')
                    # elif isinstance(cur_image, ImageFileModelItem):
                    #     msg = config.LAST_OR_FIRST_OBJ_IN_IMAGE_TIP.format(config.LAST_TIP)
                    
                    msg = config.NO_MORE_OBJ_TIP
                    QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
                    
                return None
            else:
                found = findModelItems(config.OBJ_VIEW_MODE_ALLOWED_TOP_LEVEL_OBJ_TYPE, 1, next_image, 0, next_image.rowCount() - 1, 1, reverse = False)
                parentModelItem = found[0] if found else None
                if parentModelItem:
                	LOG.info("AnnotationScene.gotoBeginObj call setCurrentImage ( {} ) ...".format( next_image))
                	self.setCurrentImage(next_image, flush = False, display = False)
                	break
                	
            next_image = self.getNextImage(next_image)
    	
            
        if parentModelItem:
            LOG.info("gotoBeginObj... try to find a display item! parentModelItem = {}".format(parentModelItem)) 
            gotoobj = parentModelItem
            if immediatelyDisplayObjImg:
                self.displayObj(gotoobj)
            return gotoobj
        
        return gotoobj
 
    def gotoEnd(self):
        LOG.info("gotoEnd ... self.scene()._sceneViewMode = {}".format(self.scene()._sceneViewMode ))
        if (self.scene()._sceneViewMode == config.IMG_VIEW_MODE):
            return self.gotoEndImage(display = True)
        elif (self.scene()._sceneViewMode == config.OBJ_VIEW_MODE):
            return self.gotoEndObj()
        
        return None 
        
    def gotoEndImage(self, display = True):
        LOG.info("gotoEndImage ... self._current_image = {}".format(self._current_image))
        end_image = self.getEndImage(self._current_image)

        if end_image is not None:
            LOG.info("AnnotationScene.gotoEndImage call setCurrentImage ( {} ) ...".format( end_image))
            self.setCurrentImage(end_image, flush = False, display = True)
            
        return end_image


    def getEndImage(self, cur_image):
        end_image = None    
        LOG.info("getEndImage... self._model = {} cur_image = {}".format(self._model, cur_image ))   
        if (self._model) and (cur_image):
            end_image = cur_image.getSibling(-1)
            LOG.info("getEndImage... cur_image = {} end_image = {}".format(cur_image, end_image ))   
            
        return end_image


    def gotoEndObj(self, popTipDialog = True, immediatelyDisplayObjImg = True):
        gotoobj = None
        parentModelItem = None
        prev_image = self.getEndImage(self._current_image)
        while True:
            LOG.info("gotoEndObj: prev_image = {} rowindex = {}".format(prev_image, prev_image.row() if prev_image else None))
            if (prev_image is None):
                if popTipDialog:
                    # if isinstance(cur_image, FrameModelItem):
                    #     videoFileName, videoFileItem = self.getFrmParentVideo(cur_image)
                    #     msg = config.LAST_OR_FIRST_OBJ_IN_FRAME_TIP.format(config.LAST_TIP, os.path.basename(videoFileName) if videoFileName else '?')
                    # elif isinstance(cur_image, ImageFileModelItem):
                    #     msg = config.LAST_OR_FIRST_OBJ_IN_IMAGE_TIP.format(config.LAST_TIP)
                    
                    msg = config.NO_MORE_OBJ_TIP
                    QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
                    
                return None
            else:
                found = findModelItems(config.OBJ_VIEW_MODE_ALLOWED_TOP_LEVEL_OBJ_TYPE, 1, prev_image, 0, prev_image.rowCount() - 1, 1, reverse = True)
                parentModelItem = found[-1] if found else None
                if parentModelItem:
                	LOG.info("AnnotationScene.gotoEndObj call setCurrentImage ( {} ) ...".format( prev_image))
                	self.setCurrentImage(prev_image, flush = False, display = False)
                	break
                	
            prev_image = self.getPreviousImage(prev_image)
    	
            
        if parentModelItem:
            LOG.info("gotoEndObj... try to find a display item! parentModelItem = {}".format(parentModelItem)) 
            gotoobj = parentModelItem
            if immediatelyDisplayObjImg:
                self.displayObj(gotoobj)
                        
            return gotoobj
        
        return gotoobj
 

                
    def findRootAnnotationModelItems(self, items):
        if items is None:
           return []
        rootmodelitemsList = []
        for item in items:
            rootmodelitem = item.modelItem()
            lastrootmodelitem = rootmodelitem
            while (rootmodelitem is not None) and (not isinstance(rootmodelitem, ImageModelItem)):
                lastrootmodelitem = rootmodelitem
                rootmodelitem = rootmodelitem.parent()
            
            if lastrootmodelitem not in rootmodelitemsList:
                # print "findRootAnnotationModelItems .. {} anno {} rootmodelitem = {}".format(lastrootmodelitem.get_label_class(), GET_ANNOTATION(lastrootmodelitem), lastrootmodelitem)
                rootmodelitemsList.append(lastrootmodelitem)
        return rootmodelitemsList


    def findChildAnnotationModelItems(self, items):
        if items is None:
            return set()
        rootmodelitemsSet = set()
        for item in items:
            rootmodelitem = item.modelItem()
            while (rootmodelitem is not None) and (not isinstance(rootmodelitem, AnnotationModelItem)):
                rootmodelitem = rootmodelitem.Setparent()

            rootmodelitemsSet.add(rootmodelitem)
        return rootmodelitemsSet


    def getObjViewModeTopModelItem(self, reverse = False):
        parentModelItem = None
        
        selectedItems = self.scene().selectedItems()
        LOG.info("toggleDisplayView... selectedItems = {}".format(selectedItems))
        if selectedItems:
            parentModelItemsList = self.findRootAnnotationModelItems(selectedItems)
            LOG.info("toggleDisplayView... try to find a display item from selected item! parentModelItemsList = {}".format(parentModelItemsList))
            if parentModelItemsList:
                parentModelItem = parentModelItemsList[0]
        
        if parentModelItem is None:
            parentModelItem = self.scene()._objViewModeTopModelItem
            if parentModelItem is not None:
                LOG.info("toggleDisplayView... use last objViewModeTopModelItem = {}".format(parentModelItem)) 
                # print "toggleDisplayView... use last objViewModeTopModelItem = {}".format(parentModelItem) 
                         
        if parentModelItem is None:
            found = findModelItems(config.OBJ_VIEW_MODE_ALLOWED_TOP_LEVEL_OBJ_TYPE, 1, self._current_image, 0, self._current_image.rowCount() - 1, 1, reverse)
            parentModelItem = found[0] if found else None
            if parentModelItem is not None:
                LOG.info("toggleDisplayView... try to find a display item from top-level objects! parentModelItem = {}".format(parentModelItem)) 
        
        return parentModelItem
  
                        
    def toggleDisplayView(self):
        LOG.info("toggleDisplayView... self._model = {} self._current_image = {}".format(self._model, self._current_image))
        if self._model is not None and self._current_image is not None:
            if self.scene()._sceneViewMode == config.IMG_VIEW_MODE:
            
                parentModelItem = self.getObjViewModeTopModelItem(reverse = False)
                LOG.info("toggleDisplayView... parentModelItem = {}".format(parentModelItem))
                if parentModelItem:
                    LOG.info("update_objViewModeTopModelItemRowIdxInParent with fixedValue = {}".format(parentModelItem.row()))
                    self.scene().update_objViewModeTopModelItemRowIdxInParent(fixedValue = parentModelItem.row())
                    self.displayObj(parentModelItem)
                    
                else:
                    if not config.AUTO_SWITCH_TO_IMGVIEW_MODE_WHEN_LAST_OR_FIRST_OBJ:
                        gotoobj = self.gotoNextObj(step = 1, popTipDialog = False)
                        if gotoobj is None:
                            gotoobj = self.gotoPreviousObj(step = 1, popTipDialog = False)
                        
                        if gotoobj is None:
                            msg = config.NO_MORE_OBJ_TIP
                            QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
                    
            else:
                self.scene()._sceneViewMode = config.IMG_VIEW_MODE
                self._mainwindow.currentDisplayContentChanged.emit(True, self._current_image) 
                self.scene().setCurrentImage(self._current_image, flush = True, display = True)
                
 
                 
    def setConnectLabelMode(self, enabled = False):
        if (self.scene()._sceneViewMode == config.IMG_VIEW_MODE):
            self.setAutoConnectLabelMode(enabled)
        elif (self.scene()._sceneViewMode == config.OBJ_VIEW_MODE):
            self.setAutoConnectLabelMode(True)
            if not enabled:
                msg = config.MANNUAL_CONNECT_COMMAND_NOT_ALLOWED_IN_OBJ_VIEW_MODE_TIP
                QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)        
 

    def setAutoConnectLabelMode(self, enabled = False):
        self._enableAutoConnectLabelMode = enabled
        # print "_enableAutoConnectLabelMode is set to {}".format(self._enableAutoConnectLabelMode) 
        desc = config.GUI_AUTO_CONNECT_MODE_DISPLAY_TEXT if enabled else config.GUI_MANNUAL_CONNECT_MODE_DISPLAY_TEXT
        if not enabled:
            add = ""
            if (self.scene()._selectedDisplayItemsList is not None) and (len(self.scene()._selectedDisplayItemsList) > 0):
                name, displayText = self.scene()._selectedDisplayItemsList[-1][annotationscene.SELECTED_DISPLAYED_ITEMS_LIST_MODELITEM_INDEX].getNameNText()
                if displayText:
                    add += "," + displayText
            desc += add
        LOG.debug(u"setAutoConnectLabelMode ... {} {}".format(self._enableAutoConnectLabelMode, desc))
        self.mainWindow().displayAutoConnectLabelMode(desc)    
        


    def getPreviousImage(self, cur_image, step = 1):
        prev_image = None    
        LOG.info("getPreviousImage... self._model = {} cur_image = {}".format(self._model, cur_image ))   
        if self._model is not None:
            for i in xrange(step):
                exitLoop = False
                while True:
                   if cur_image is not None:
                       prev_image = cur_image.getPreviousSiblingX()
                       LOG.info("getPreviousImage... cur_image = {} prev_image = {}".format(cur_image, prev_image ))   
                                  
                   cur_image = prev_image
                   LOG.info("getPreviousImage... cur_image is updated with prev_image = {}".format(prev_image ))  
                   if prev_image is None:    
                       exitLoop = True
                       break

                   isUnlabeled = prev_image['unlabeled']
                   if isUnlabeled:
                      cur_image = prev_image
                      continue
                   
                   break
				
                if exitLoop:
                    break
				    
        return prev_image
 
        
    def gotoPreviousImage(self, step=1, display = True, popTipDialog = True):
        LOG.info("gotoPreviousImage ... self._current_image = {} step = {}".format(self._current_image, step ))
        prev_image = self.getPreviousImage(self._current_image, step)

        if prev_image is not None:
            LOG.info("AnnotationScene.gotoPreviousImage call setCurrentImage ( {} ) ...".format( prev_image))
            self.setCurrentImage(prev_image, flush = False, display = True)
        else:
            if popTipDialog:
                msg = config.LAST_OR_FIRST_FRAME_OR_IMAGE_TIP.format(config.FIRST_TIP)
                QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)

        return prev_image
                        

    def gotoPrevious(self, step=1):
        LOG.info("gotoPrevious ... self.scene()._sceneViewMode = {} step = {}".format(self.scene()._sceneViewMode, step ))
        if (self.scene()._sceneViewMode == config.IMG_VIEW_MODE):
            return self.gotoPreviousImage(step, display = True)
        elif (self.scene()._sceneViewMode == config.OBJ_VIEW_MODE):
            return self.gotoPreviousObjWithFilter(self._view_filters, step)
        
        return None

    def gotoPreviousObjWithFilter(self, filter, step=1, popTipDialog = True):
        # print "\n=== filters {} ===".format(filter)
        if filter:
            prevObj = None
            while True:
                prevObj = self.gotoPreviousObj(step, popTipDialog, immediatelyDisplayObjImg = False)
                if not prevObj:
                    break
                # print "=== ModelItem {} ===".format(GET_ANNOTATION(prevObj))
                isMatch = statistics.applyFilterOnObj(GET_ANNOTATION(prevObj), filter)
                if isMatch:
                    # print "=== isMatch {} ===".format(isMatch)
                    self.displayObj(prevObj)
                    break
            return prevObj

        return self.gotoPreviousObj(step, popTipDialog, immediatelyDisplayObjImg = True)
                
                    
    def gotoPreviousObj(self, step=1, popTipDialog = True, immediatelyDisplayObjImg = True):
        gotoobj = None
        cur_image = self._current_image
        if (self._model is None) or (cur_image is None):
            return gotoobj
        LOG.info("1: cur_image = {} rowindex = {}".format(cur_image, cur_image.row() if cur_image else None))
        imgend = self.scene().update_objViewModeTopModelItemRowIdxInParent(delta = -1)
        LOG.info("imgend = {} _objViewModeTopModelItemRowIdxInParent = {} ".format(imgend, self.scene()._objViewModeTopModelItemRowIdxInParent))
        parentModelItem = None
        prev_image = None
        if imgend: # imgend means there are no any object on current image    
            if config.AUTO_SWITCH_TO_IMGVIEW_MODE_WHEN_LAST_OR_FIRST_OBJ:
                self.scene().reset_objViewMode()
                self.toggleDisplayView()
                return None
                
            prev_image = cur_image
            while True:
                org = prev_image
                LOG.info("cur_image = {} rowindex = {}".format(org, org.row() if org else None))
                prev_image = self.getPreviousImage(prev_image)
                LOG.info("prev_image = {} rowindex = {}".format(prev_image, prev_image.row() if prev_image else None))
                if (prev_image is None):
                    if popTipDialog:
                        # if isinstance(cur_image, FrameModelItem):
                        #     videoFileName, videoFileItem = self.getFrmParentVideo(cur_image)
                        #     msg = config.LAST_OR_FIRST_OBJ_IN_FRAME_TIP.format(config.LAST_TIP, os.path.basename(videoFileName) if videoFileName else '?')
                        # elif isinstance(cur_image, ImageFileModelItem):
                        #     msg = config.LAST_OR_FIRST_OBJ_IN_IMAGE_TIP.format(config.LAST_TIP)
                        msg = config.NO_MORE_OBJ_TIP
                        QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
                    return None
                else:
                    found = findModelItems(config.OBJ_VIEW_MODE_ALLOWED_TOP_LEVEL_OBJ_TYPE, 1, prev_image, 0, prev_image.rowCount() - 1, 1, reverse = True)
                    parentModelItem = found[-1] if found else None
                    LOG.info("parentModelItem.row() = {}".format(parentModelItem.row() if parentModelItem else None))
                    if parentModelItem:
                    	LOG.info("AnnotationScene.gotoPreviousObj call setCurrentImage ( {} ) ...".format( prev_image))
                    	self.setCurrentImage(prev_image, flush = False, display = False)
                    	break
                
            if parentModelItem:
                LOG.info("gotoPreviousObj... find a display item! parentModelItem = {}".format(parentModelItem)) 
                gotoobj = parentModelItem
                if immediatelyDisplayObjImg:
                    self.displayObj(gotoobj)
                return gotoobj
            
            return gotoobj
            
                    
        parentModeItem = self._current_image             
        childModelItem = parentModeItem.childAt(self.scene()._objViewModeTopModelItemRowIdxInParent) if parentModeItem else None
        gotoobj = childModelItem   
        if immediatelyDisplayObjImg:
            self.displayObj(gotoobj)

        return gotoobj 
        

    def updateModified(self):
        """update all GUI elements which depend on the state of the model,
        e.g. whether it has been modified since the last save"""
        #self.ui.action_Add_Image.setEnabled(self._model is not None)
        #self.ui.action_Add_Video.setEnabled(self._model is not None)
        # TODO also disable/enable other items
        #self.ui.actionSave.setEnabled(self.annotations.dirty())
        #self.setWindowModified(self.annotations.dirty())
        pass

    def getCurrentImageName(self):
        if self._current_image:
            return self._current_image.data()
        else:
            return None
        
    def currentImage(self):
        return self._current_image

    def onCurrentChanged(self, image):
        self.setCurrentImage(image, flush = False, display = True)
            
    def setCurrentImage(self, image, flush = False, display = True):
        # LOG.info("setCurrentImage 0 IMAGE {} ...".format(image))
        if isinstance(image, QModelIndex):
            image = self._model.itemFromIndex(image)

        if isinstance(image, RootModelItem):
            return

        LOG.info("setCurrentImage... IMAGE {} flush {} display {}...".format(image, flush, display))
        while (image is not None) and (not isinstance(image, ImageModelItem)):
            image = image.parent()
            
        # LOG.info("setCurrentImage 2 IMAGE {} self._current_image {} ...".format(image, self._current_image))  
        # if image is None:
        #    raise RuntimeError("Tried to set current image to item that has no Image or Frame as parent!")
            
                   
        if image and (image != self._current_image):
            self._current_image = image
            LOG.info("setCurrentImage emit currentImageChanged ...")
            self.currentImageChanged.emit(flush, display)

    def getImage(self, filedir, item):
        loadItem = None
        fileIsExist = False
        if item[config.METADATA_LABELCLASS_TOKEN] == config.ANNOTATION_FRAME_TOKEN:
            parent = item.parent()
            if os.path.isfile(parent[config.ANNOTATION_FILENAME_TOKEN]):
                filepath = parent[config.ANNOTATION_FILENAME_TOKEN]
            else:
                filepath = os.path.join(filedir, parent[config.ANNOTATION_FILENAME_TOKEN])
            (loadItem, fileIsExist) = self._container.loadFrame(filepath, item[config.ANNOTATION_VIDEO_FILE_FRAME_IDX_TOKEN])
        else:
            if os.path.isfile(item[config.ANNOTATION_FILENAME_TOKEN]):
                filepath = item[config.ANNOTATION_FILENAME_TOKEN]
            else:
                filepath = os.path.join(filedir, item[config.ANNOTATION_FILENAME_TOKEN])
            (loadItem, fileIsExist) = self._container.loadImage(filepath)
 
        if loadItem is None :
            filename = self.getMediaFileName(item)
            if fileIsExist:
                 msg = config.GUI_VIDEO_GET_IMAGE_FAILURE_TIP.format(item[config.ANNOTATION_VIDEO_FILE_FRAME_IDX_TOKEN], filename)
                 self.statusMessage.emit(msg, config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS)
                 QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
            
            else:
                 msg = config.GUI_MEDIA_FILE_DONT_EXIST_TEXT.format(filename)
                 # self.statusMessage.emit(msg, config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS)
                 QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
            
        return loadItem, fileIsExist

    # zxadd
    def getFrmParentVideo(self, item):
        if item[config.METADATA_LABELCLASS_TOKEN] == config.ANNOTATION_FRAME_TOKEN:
            parent = item.parent()
            return parent[config.ANNOTATION_FILENAME_TOKEN], parent
        else:
            return None, None

    def getMediaFileName(self, image_item):
        if image_item and (image_item.get(config.METADATA_LABELCLASS_TOKEN, None) == config.ANNOTATION_FRAME_TOKEN):
            video = image_item.parent()
            return video.get(config.ANNOTATION_FILENAME_TOKEN, None) if video else None
        else:
            return image_item.get(config.ANNOTATION_FILENAME_TOKEN, None)
                
    def getAnnotationFilePatterns(self):
        return self._container_factory.patterns()

    def addImageFile(self, fname):
        if not fname:
            return None, False
            
        dirname = os.path.dirname(fname)
        if not os.path.isdir(dirname):
            return None, False
            
        if not self._imgDir:
            imgDir = dirname
            self._imgDir = imgDir
        elif not os.path.isabs(self._imgDir):
            annoFilePath = self._container._filename
            imgDir = os.path.join(os.path.dirname(annoFilePath), self._imgDir)
        else:
            imgDir = self._imgDir

        try:
            relfname = os.path.join(os.path.relpath(dirname, imgDir), os.path.basename(fname))
        except:
            relfname = os.path.join(os.path.relpath(os.path.splitdrive(imgDir)[0], imgDir), "../", fname)
        
        # print "fname = {} _imgDir = {} relfname = {}".format(fname, self._imgDir, relfname)
        
        fileitem = {
            config.ANNOTATION_FILENAME_TOKEN: relfname,
            config.METADATA_LABELCLASS_TOKEN: config.ANNOTATION_IMAGE_TOKEN,
            'annotations': [],
        }
        
        try:
            # _fname = fname.encode('utf8')
            im = Image.open(fname)
        except Exception as e:
            im = None
        
        if (im is None):
            return None, False
            
        if config.ENABLE_TOP_OBJECT_MODE:
            width, height = im.size
            thisfrm_annos_newcontainer = {
                    "class": config.DEFAULT_TOP_OBJECT,
                    "height": height,
                    "width": width,
                    "x": 0,
                    "y": 0
                }
            fileitem['annotations'] = [ thisfrm_annos_newcontainer ]

        # LOG.info("addImageFile IS CALLED ... with imgdir {} fileitem {} ...".format(self._imgDir, fileitem))
        mediaFileItem, errorForFileHasBeenAdded = self._model._root.appendFileItem(self._imgDir, fileitem)
        return mediaFileItem, errorForFileHasBeenAdded
        
        
    def addVideoFile(self, _fname, frmInterval = 25):
        if not _fname:
            return None, False
            
        dirname = os.path.dirname(_fname)
        if not os.path.isdir(dirname):
            return None, False
            
        if not self._imgDir:
            imgDir = dirname
            self._imgDir = imgDir
        elif not os.path.isabs(self._imgDir):
            annoFilePath = self._container._filename
            imgDir = os.path.join(os.path.dirname(annoFilePath), self._imgDir)
        else:
            imgDir = self._imgDir

        try:
            relfname = os.path.join(os.path.relpath(dirname, imgDir), os.path.basename(_fname))
        except:
            relfname = os.path.join(os.path.relpath(os.path.splitdrive(imgDir)[0], imgDir), "../", _fname)
        
        fileitem = {
            config.ANNOTATION_FILENAME_TOKEN: relfname,
            config.METADATA_LABELCLASS_TOKEN: config.ANNOTATION_VIDEO_TOKEN,
            'frames': [],
        }

        msg = config.GUI_IMPORT_VIDEO_TIP.format(_fname, frmInterval)
        self.statusMessage.emit(msg, config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS)
        
        fname = _fname.encode('utf8')
        videosrchandle = cv2.VideoCapture(fname)
        iso = videosrchandle.isOpened()
        if iso is False:
            print "[ZXD] Video file '{}' fail to open!".format(fname)
        else:
            print "[ZXD] Video file '{}' has been opened successfully!".format(fname)
        
           
        if iso is True:
            frmNum = int(videosrchandle.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT ))
            frmw = int(videosrchandle.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
            frmh = int(videosrchandle.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
            # frmTimeStampInMs = int(videosrchandle.get(CV_CAP_PROP_POS_MSEC)) 
            LOG.info("Adding {} frames! Resolution {} * {}".format(frmNum, frmw, frmh))

            fileitem['frames'] = [{ 
                                    'annotations': [], 
                                    config.ANNOTATION_VIDEO_FILE_FRAME_IDX_TOKEN: i,
                                    config.ANNOTATION_VIDEO_FILE_FRAME_TIMESTAMP_TOKEN: 0,
                                    config.METADATA_LABELCLASS_TOKEN: config.ANNOTATION_FRAME_TOKEN
                                  } for i in xrange(0, frmNum, frmInterval) ]
    
            return self._model._root.appendFileItem(self._imgDir, fileitem)
    
        else:
            # print u"Video file '{}' fail to open!".format(_fname)
            return None, False

    ###
    ### GUI functions
    ###___________________________________________________________________________________________
    def mainWindow(self):
        return self._mainwindow

    ###
    ### PropertyEditor functions
    ###___________________________________________________________________________________________
    def propertyeditors(self):
        if self._mainwindow is None:
            return None
        else:
            return [self._mainwindow.property_editor1.propertyEditorWidget, self._mainwindow.personbike_pannel.propertyEditorWidget, self._mainwindow.property_editor2, \
                    self._mainwindow.property_editor3, self._mainwindow.property_editor6.propertyEditorWidget]

    def set_insert_mode_property_editor(self, editor):
        self.insert_mode_property_editor = editor

    
    ###16/7/2017 8:31PM
    ### Scene functions
    ###___________________________________________________________________________________________
    def scene(self):
        if self._mainwindow is None:
            return None
        else:
            return self._mainwindow.scene

    def view(self):
        if self._mainwindow is None:
            return None
        else:
            return self._mainwindow.view

    def selectNextAnnotation(self):
        if self._mainwindow is not None:
            return self._mainwindow.scene.selectNextItem()

    def selectPreviousAnnotation(self):
        if self._mainwindow is not None:
            return self._mainwindow.scene.selectNextItem(reverse=True)

    def selectAllAnnotations(self):
        if self._mainwindow is not None:
            return self._mainwindow.scene.selectAllItems()

    def deleteSelectedAnnotations(self):
        if self._mainwindow is not None:
            LOG.info("deleteSelectedAnnotations... deleteSelectedItems")
            self._mainwindow.scene.deleteSelectedItems()

    def exitInsertMode(self):
        LOG.debug("exitInsertMode...")
        self.exitInsertModeForAll()

    def exitInsertModeForCurInsertModeEditor(self):
        if self._mainwindow is not None:
            if self.insert_mode_property_editor is not None:
                LOG.info("exitInsertModeForCurInsertModeEditor ;;; curInsertModeEditor = {} endInsertionMode ...".format(self.insert_mode_property_editor))
                return self.insert_mode_property_editor.endInsertionMode()


    def exitInsertModeForAll(self):
        if self._mainwindow is not None:
            for i in self.propertyeditors():
                if i:
                    i.endInsertionMode()

    """
    def saveCurViewContentToImgFile(self):
        if self._mainwindow is not None:
            if (self.scene()._sceneViewMode == config.OBJ_VIEW_MODE):
                pixmap = self.scene()._image_objViewModeTopModelItem_pixmap
            else:    
                pixmap = self.scene()._img_pixmap

            if pixmap:
                saveDirName = os.path.dirname(os.path.realpath(__file__)) + "/../../savePic/"
                if not os.path.exists(saveDirName):
                    os.makedirs(saveDirName)          
                curImgFileName = self.getCurrentImageName() + ".bmp"      
                pixmap.save(os.path.join(saveDirName,  curImgFileName))
        return
    """


    def saveCurViewContentToImgFile(self, displayStatuMsge = True):
        saveDirName, curImgFileName = None, None
        if self._mainwindow is not None:
            # pixmap = self._mainwindow.view.grabWidget()
            pixmap = QPixmap.grabWidget(self._mainwindow.view)

            if pixmap:
                saveDirName = os.path.dirname(os.path.realpath(__file__)) + "/../../savePic/"
                if not os.path.exists(saveDirName):
                    os.makedirs(saveDirName)
                curImgFileName = self.getCurrentImageName() + ".bmp"
                filename = os.path.join(saveDirName, curImgFileName)
                pixmap.save(filename)
                if displayStatuMsge:
                    msg = config.GUI_SAVE_IMAGE_SUCCESS_TEXT.format(filename)
                    self.statusMessage.emit(msg, config.GUI_STATUS_BAR_DISPLAY_TIME_IN_MS)
        return saveDirName, curImgFileName


    def saveAllAnnotationViewContentToImgFiles(self):
        saveDirName, curImgFileName = None, None
        cur_image = self._current_image
        if not self._model:
            return
        if not self._model._root:
            return
            
        rowCount = self._model._root.rowCount()

        msg = config.GUI_BEGIN_PROCESS_IMAGES_TEXT.format(rowCount)
        QMessageBox.critical(None, config.GUI_TIP_TEXT, msg)
                
        self.gotoBeginImage()
        # print "self._model._root.rowCount() = {}".format(self._model._root.rowCount())
        processCnt = 0
        for row in xrange(rowCount):
            # print "Now process for {}th image...".format(row)
            child = self._model._root.childAt(row)
            saveDirName, curImgFileName = self.saveCurViewContentToImgFile(displayStatuMsge = False)
            nextImage = self.gotoNextImage(popTipDialog = False)
            processCnt += 1
            if not nextImage:
                break
                
        self.setCurrentImage(cur_image)

        msg = config.GUI_END_PROCESS_IMAGES_TEXT.format(processCnt, saveDirName)
        QMessageBox.critical(None, config.GUI_SUCCESS_TEXT, msg)
        return


    def clearObjViewFilter(self):
        self._view_filters = None
        return


    ###___________________________________________________________________________________________
    ###
    ### TreeView functions
    ###___________________________________________________________________________________________
    def treeview(self):
        if self._mainwindow is None:
            return None
        else:
            return self._mainwindow.treeview
       
            
            
class perpetualTimer():

   def __init__(self, timerIntervalInSeconds, hFunction):
      self.timerIntervalInSeconds = timerIntervalInSeconds
      self.hFunction = hFunction
      self.thread = threading.Timer(self.timerIntervalInSeconds, self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = threading.Timer(self.timerIntervalInSeconds, self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()
