# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import logging
from sloth.conf import config
from sloth.gui.statistics import statisticsForCurLoadedJsonFileDialog, statisticsForMultipleJsonFilesDialog
from sloth.gui.utilityPlugin import createJsonForSpecificImgFolderDialog, mergeMultipleJsonFilesDialog, cleanDuplicateDataInJsonFileDialog, SplitToMultipleJsonFilesDialog

LOG = logging.getLogger(config.LOG_FILE_NAME)

class StatisticForCurJsonFilePlugin(QObject):
    def __init__(self, labeltool, class_filter=None, frame_range=1, overlap_threshold=None, prefix=''):
        QObject.__init__(self)

        self._labeltool = labeltool
        self._wnd = labeltool.mainWindow() if labeltool else None
        self._sc = QAction(config.STATISTIC_OR_APPLY_OBJVIEWFILTER_FOR_CUR_JSON_FILE_PLUGIN_DISPLAYTEXT, self._wnd)
        self._sc.triggered.connect(self.statistics)

    def statistics(self):
        dlg = statisticsForCurLoadedJsonFileDialog(self._wnd, self._wnd)
        dlg.show()
        return
        
    def action(self):
        return self._sc


class StatisticForMultipleJsonFilesPlugin(QObject):
    def __init__(self, labeltool, class_filter=None, frame_range=1, overlap_threshold=None, prefix=''):
        QObject.__init__(self)

        self._labeltool = labeltool
        self._wnd = labeltool.mainWindow() if labeltool else None
        self._sc = QAction(config.STATISTIC_FOR_MULTIPLE_JSON_FILES_PLUGIN_DISPLAYTEXT, self._wnd) 
        self._sc.triggered.connect(self.statistics)

    def statistics(self):
        dlg = statisticsForMultipleJsonFilesDialog(self._wnd, self._wnd)
        dlg.show()
        return

    def action(self):
        return self._sc


class CreateJsonForSpecificImgFolderPlugin(QObject):
    def __init__(self, labeltool, class_filter=None, frame_range=1, overlap_threshold=None, prefix=''):
        QObject.__init__(self)

        self._labeltool = labeltool
        self._wnd = labeltool.mainWindow() if labeltool else None
        self._sc = QAction(config.CREATE_JSON_FILE_FOR_SPECIFIC_IMG_FOLDER_PLUGIN_DISPLAYTEXT, self._wnd)
        self._sc.triggered.connect(self.statistics)

    def statistics(self):
        dlg = createJsonForSpecificImgFolderDialog(self._wnd, self._wnd)
        # dlg.show()
        return

    def action(self):
        return self._sc


class MergeMultipleJsonFilesPlugin(QObject):
    def __init__(self, labeltool, class_filter=None, frame_range=1, overlap_threshold=None, prefix=''):
        QObject.__init__(self)

        self._labeltool = labeltool
        self._wnd = labeltool.mainWindow() if labeltool else None
        self._sc = QAction(config.MERGE_MULTIPLE_JSON_FILES_PLUGIN_DISPLAYTEXT, self._wnd)
        self._sc.triggered.connect(self.statistics)

    def statistics(self):
        dlg = mergeMultipleJsonFilesDialog(self._wnd, self._wnd)
        # dlg.show()
        return

    def action(self):
        return self._sc

class CleanDuplicateDataInJsonFilePlugin(QObject):
    def __init__(self, labeltool, class_filter=None, frame_range=1, overlap_threshold=None, prefix=''):
        QObject.__init__(self)

        self._labeltool = labeltool
        self._wnd = labeltool.mainWindow() if labeltool else None
        self._sc = QAction(config.CLEAN_DUPLICATE_DATA_IN_JSON_FILE_PLUGIN_DISPLAYTEXT, self._wnd)
        self._sc.triggered.connect(self.statistics)

    def statistics(self):
        dlg = cleanDuplicateDataInJsonFileDialog(self._wnd, self._wnd)
        # dlg.show()
        return

    def action(self):
        return self._sc
        
        
class CopyAnnotationsPlugin(QObject):
    def __init__(self, labeltool, class_filter=None, frame_range=1, overlap_threshold=None, prefix=''):
        QObject.__init__(self)

        self._class_filter = class_filter
        self._overlap_threshold = overlap_threshold
        self._frame_range = frame_range
        self._prefix = prefix

        self._labeltool = labeltool
        self._wnd = labeltool.mainWindow() if labeltool else None
        self._sc = QAction("Copy all annotations from previous image/frame to current image", self._wnd)
        self._sc.triggered.connect(self.copy)

    def copy(self):
        current = self._labeltool.currentImage()

        prev = current.getPreviousSibling()
        num_back = self._frame_range

        while num_back > 0 and prev is not None:
            for annotation in self.getAnnotationsFiltered(prev):
                LOG.debug("num_back: %d, annotation: %s", num_back, str(annotation))
                # check for overlap with annotations in current
                if self._overlap_threshold is not None:
                    r1 = self.getRect(annotation)
                    if r1 is not None:
                        cont = False
                        for curr_ann in self.getAnnotationsFiltered(current):
                            r2 = self.getRect(curr_ann)
                            if r2 is not None:
                                o = self.overlap(r1, r2)
                                LOG.debug("overlap between %s and %s: %f", str(r1), str(r2), o)
                                if o > self._overlap_threshold:
                                    cont = True
                                    break
                        if cont:
                            continue # do not copy

                # copy the annotation
                current.addAnnotation(annotation)

            prev = prev.getPreviousSibling()
            num_back -= 1

    def getAnnotationsFiltered(self, image_item):
        annotations = []
        for annotation in image_item.getAnnotations(recursive = True)['annotations']:
            # check class filter
            if self._class_filter is not None:
                if annotation.get(config.METADATA_LABELCLASS_TOKEN, None) not in self._class_filter:
                    continue  # do not copy
            annotations.append(annotation)
        return annotations

    def getRect(self, annotation):
        keys = ['x', 'y', 'width', 'height']
        for key in keys:
            if not self._prefix + key in annotation:
                return None
        return [annotation[self._prefix + key] for key in keys]

    def overlap(self, r1, r2):
        ia = float(self.area(self.intersect(r1, r2)))
        union = self.area(r1) + self.area(r2) - ia
        return ia / union

    def intersect(self, r1, r2):
        x = max(r1[0], r2[0])
        y = max(r1[1], r2[1])
        w = max(0, min(r1[0] + r1[2], r2[0] + r2[2]) - x)
        h = max(0, min(r1[1] + r1[3], r2[1] + r2[3]) - y)
        return (x, y, w, h)

    def area(self, r):
        return r[2]*r[3]

    def action(self):
        return self._sc

# zx added @ 2016-08-03 for copying all annoatations in current frame to all other images
class CopyAnnotationsToAllOtherFrmsPlugin(QObject):
    def __init__(self, labeltool):
        QObject.__init__(self)

        self._labeltool = labeltool
        self._wnd = labeltool.mainWindow() if labeltool else None
        self._sc = QAction("Copy all annotations in current image to all other images", self._wnd)
        self._sc.triggered.connect(self.copy)

    def copy(self):

        current = self._labeltool.currentImage()
        if self.getAnnotationsNum(current) <= 0:
            print "No label button is selected! Bypass CopyCurrentLabelToAllPlugin!"
            return
            


        # ===============================================
        # copy current labels to prev images
        # ===============================================
        prev = current.getPreviousSiblingX()
        next = current.getNextSiblingX()
        cnt = 0

        for annotation in self.getAnnotations(current): 
        
            # copy current labels to prev images
            while prev is not None:
                # copy the annotation to prev
                cnt += 1
                prev.addAnnotation(annotation)
                prev = prev.getPreviousSiblingX()

            # copy current labels to next images
            while next is not None:
                # copy the annotation to next
                cnt += 1
                next.addAnnotation(annotation)
                next = next.getNextSiblingX()

        print "Totally %d frames have been copyed from current image's annotations!" % cnt


    def getAnnotationsNum(self, image_item):
        return image_item.getAnnotationsNum()
        
    def getAnnotations(self, image_item):
        # print "image_item = {}".format(image_item)
        return image_item.getAnnotations()['annotations']


    def action(self):
        return self._sc


# zx added @ 2016-09-03 for copying current selected annotations in current frame to all other images
class CopySelectedAnnotationsToAllOtherFrmsPlugin(QObject):
    def __init__(self, labeltool):
        QObject.__init__(self)

        self._labeltool = labeltool
        self._wnd = labeltool.mainWindow() if labeltool else None

        self._sc = QAction("Copy selected label in current frame to all other images", self._wnd)
        self._sc.triggered.connect(self.copy)


    def copy(self):

        if len(self._wnd.scene.selectedItems()) <= 0:
            print "No label button is selected! Bypass CopyCurrentLabelToAllPlugin!"
            return

               
        current = self._labeltool.currentImage()

        # ===============================================
        
        # ===============================================
        prev = current.getPreviousSiblingX()
        next = next.getNextSiblingX()
        cnt = 0

        for sitem in self._wnd.scene.selectedItems():
            for anno in sitem.modelItem().getAnnotations():
            
                # copy current labels to prev images   
                while prev is not None:
                    # copy the annotation to prev
                    cnt += 1
                    prev.addAnnotation(anno)
                    prev = prev.getPreviousSiblingX()

                # copy current labels to next images   
                while next is not None:
                    # copy the annotation to next
                    cnt += 1
                    next.addAnnotation(anno)
                    next = next.getNextSiblingX()                

        print "Totally %d frames have been copyed from current image's annotations!" % cnt

    def action(self):
        return self._sc
        

class PolygonEnumeratorPlugin(QObject):
    """Enumerate the corners of polygons."""

    def __init__(self, labeltool):
        QObject.__init__(self)

        # Decorate the paint() method with our enumerating paint:
        from sloth.items import PolygonItem
        oldpaint = PolygonItem.paint

        def paint(self, painter, option, widget=None):
            oldpaint(self, painter, option, widget)
            for i, p in enumerate(self._polygon):
                painter.drawText(p, str(i))

        import functools
        functools.update_wrapper(paint, oldpaint)

        PolygonItem.paint = paint

    def action(self):
        return None



class SplitToMultipleJsonFilesPlugin(QObject):
    def __init__(self, labeltool, class_filter=None, frame_range=1, overlap_threshold=None, prefix=''):
        QObject.__init__(self)

        self._labeltool = labeltool
        self._wnd = labeltool.mainWindow() if labeltool else None
        self._sc = QAction(config.SPLIT_TO_MULTIPLE_JSON_FILES_PLUGIN_DISPLAYTEXT, self._wnd)
        self._sc.triggered.connect(self.statistics)

    def statistics(self):
        dlg = SplitToMultipleJsonFilesDialog(self._wnd, self._wnd) 
        # dlg.show()
        return

    def action(self):
        return self._sc