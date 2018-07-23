# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

import os
import fnmatch
import time
import numpy as np
from sloth.core.exceptions import \
    ImproperlyConfigured, NotImplementedException, InvalidArgumentException
from sloth.core.utils import import_callable
import logging
from sloth.conf import config
import datetime
import cv2
from sloth.gui import utils
import copy

LOG = logging.getLogger(config.LOG_FILE_NAME)

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import json
except ImportError:
    pass
try:
    import yaml
except ImportError:
    pass
try:
    import okapy
    import okapy.videoio as okv
    _use_pil = False
except ImportError:
    try:
        from PIL import Image
        _use_pil = True
    except:
        raise RuntimeError("Could neither find PIL nor okapy.  Sloth needs one of them for loading images.")


class AnnotationContainerFactory:
    def __init__(self, containers):
        """
        Initialize the factory with the mappings between file pattern and
        the container.

        Parameters
        ==========
        containers: tuple of tuples (str, str/class)
            The mapping between file pattern and container class responsible
            for loading/saving.
        """
        self._containers = []
        for pattern, item in containers:
            if type(item) == str:
                item = import_callable(item)
            self._containers.append((pattern, item))

    def patterns(self):
        return [pattern for pattern, item in self._containers]

    def create(self, filename, *args, **kwargs):
        """
        Create a container for the filename.

        Parameters
        ==========
        filename: str
            Filename for which a matching container should be created.
        *args, **kwargs:
            Arguments passed to constructor of the container.
        """
        for pattern, container in self._containers:
            if fnmatch.fnmatch(filename, pattern):
                return container(*args, **kwargs)
        raise ImproperlyConfigured(
            "No container registered for filename %s" % filename
        )


class AnnotationContainer:
    """
    Annotation Container base class.
    """

    def __init__(self):
        self.clear()


    def filename(self):
        """The current filename."""
        return self._filename

    def clear(self):
        self._annotations = []  # TODO Why isn't this used? Annotations are passed as parameters instead. Let's have encapsulation.
        self._filename = None
        self._video_cache = {}
        self._imgdir = ""
        self._version = ""
        self._versiondesc = ""
        self._date = ""
        self._has_imgDir = False


    # ==========================================================================
    # zx comment: load() return contents in labels fields in format of list from file
    # ==========================================================================
    def load(self, filename):
        """
        Load the annotations.
        """
        if not filename:
            raise InvalidArgumentException("filename cannot be empty")
        self._filename = filename

        start = time.time()
        ann = self.parseFromFile(filename)
        diff = time.time() - start
 
        filenameutf = utils.toUTFStr(filename)
                        
        LOG.info(u"Loaded annotations from {} in {:.2f}... ann = {}".format(filenameutf, diff, ann))
        return ann

    def parseFromFile(self, filename):
        """
        Read the annotations from disk. Must be implemented in the subclass.
        """
        raise NotImplementedException(
            "You need to implement parseFromFile() in your subclass " +
            "if you use the default implementation of " +
            "AnnotationContainer.load()"
        )

    def save(self, annotations, filename="", customImgDir = ""):
        """
        Save the annotations.
        """
        if not filename:
            filename = self.filename()
        self._filename = filename
        self.serializeToFile(filename, annotations, customImgDir)

    def serializeToFile(self, filename, annotations, customImgDir = ''):
        """
        Serialize the annotations to disk. Must be implemented in the subclass.
        """
        raise NotImplementedException(
            "You need to implement serializeToFile() in your subclass " +
            "if you use the default implementation of " +
            "AnnotationContainer.save()"
        )

    def _fullpath(self, filename):
        """
        Calculate the fullpath to the file, assuming that
        the filename is given relative to the label file's
        directory.
        """
        if self.filename() is not None:
            basedir = os.path.dirname(self.filename())
            fullpath = os.path.join(basedir, filename)
        else:
            fullpath = filename
        return fullpath

    def loadImage(self, filename):
        """
        Load and return the image referenced to by the filename.  In the
        default implementation this will try to load the image from a path
        relative to the label file's directory.
        """
        try:
            fileIsExist = True
            fullpath = self._fullpath(filename)
            # LOG.info(u"loadImage... filename = {} fullpath = {}".format(filename, fullpath))
            
            if not os.path.isfile(fullpath):
                LOG.warn("Image file %s does not exist." % fullpath)
                fileIsExist = False
                return None, fileIsExist
            
            if _use_pil:
                _fullpath = fullpath.encode('utf8')
                LOG.info(u"loadImage... Image.open({})".format(fullpath))
                im = Image.open(fullpath)
                imarr = np.asarray(im)
                return imarr, fileIsExist
            else:
                retcode = okapy.loadImage(fullpath)
                return retcode, fileIsExist
        except Exception as e:
            return None, False


    def loadFrame(self, filename, frame_number):
        try:
            fileIsExist = True
            _filename = filename # filename.decode('utf8')
            
            if not os.path.isfile(_filename):
                LOG.warning(u"video file '{}' doesn't exist!".format(_filename))
                fileIsExist = False
                return None, fileIsExist
                
            nfilename = os.path.realpath(filename)
            videosrchandle = None
            videosrcinfo   = None
            # LOG.info(u"nfilename = {} _video_cache = {}".format(nfilename, self._video_cache))
            
            if nfilename in self._video_cache:
                videosrcinfo   = self._video_cache[nfilename]
                videosrchandle = videosrcinfo[0]
                frmNum = videosrcinfo[2]
            else:
                nfilenamec = nfilename.encode('utf8')
                videosrchandle = cv2.VideoCapture(nfilenamec)
                fps = videosrchandle.get(cv2.cv.CV_CAP_PROP_FPS)
                frmNum = int(videosrchandle.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
                frmWidth = int(videosrchandle.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
                frmHeight= int(videosrchandle.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
                self._video_cache[nfilename] = [videosrchandle, fps, frmNum, frmWidth, frmHeight]
            
            if frame_number >= frmNum:
                LOG.warning(u"Target frame idx {} exceed video's frame number {}!".format(frame_number, frmNum))
                return None, fileIsExist
            
            success = videosrchandle.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, frame_number)
            if not success:
                LOG.warning(u"Video file '{}' cannot seek to target frame idx {}!".format(filename, frame_number))
                return None, fileIsExist
            
            success, frame = videosrchandle.read()
            if not success:
                LOG.warning(u"Video file '{}' cannot seek to target frame idx {}!".format(filename, frame_number))
                return None, fileIsExist
            
            # convert BGR => RGB
            frmRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            frmArr = np.asarray(frmRGB)
            
            return frmArr, fileIsExist
        except Exception as e:
            return None, False

class PickleContainer(AnnotationContainer):
    """
    Simple container which pickles the annotations to disk.
    """

    def parseFromFile(self, fname):
        """
        Overwritten to read pickle files.
        """
        f = open(fname, "rb")
        return pickle.load(f)

    def serializeToFile(self, fname, annotations, customImgDir = ''):
        """
        Overwritten to write pickle files.
        """
        f = open(fname, "wb")
        pickle.dump(annotations, f)


class OkapiAnnotationContainer(AnnotationContainer):
    """
    Simple container which writes the annotations to disk using okapy.AnnotationContainer.
    """

    def convertAnnotationPropertiesMapToDict(self, properties):
        """
        Converts a AnnotationPropertiesMap to a dict
        """
        propdict = {}
        for k, v in properties.items():
            propdict[k] = v
        return propdict

    def parseFromFile(self, filename):
        """
        Overwritten to read Okapi::Annotation files.
        """
        container = okapy.AnnotationContainer()
        container.ReadFromFile(filename)

        annotations = []
        for f in container.files():
            fileitem = self.convertAnnotationPropertiesMapToDict(f.properties())
            fileitem[config.METADATA_LABELCLASS_TOKEN] = fileitem['type']
            del fileitem['type']
            if f.isImage():
                fileitem['annotations'] = []
                for annotation in f.annotations():
                    ann = self.convertAnnotationPropertiesMapToDict(annotation.properties())
                    fileitem['annotations'].append(ann)
            elif f.isVideo():
                fileitem['frames'] = []
                for frame in f.frames():
                    frameitem = self.convertAnnotationPropertiesMapToDict(frame.properties())
                    frameitem['annotations'] = []
                    for annotation in frame.annotations():
                        ann = self.convertAnnotationPropertiesMapToDict(annotation.properties())
                        frameitem['annotations'].append(ann)
                    fileitem['frames'].append(frameitem)
            annotations.append(fileitem)

        return annotations

    def convertDictToAnnotationPropertiesMap(self, annotation, propdict):
        """
        Converts a dict to a AnnotationPropertiesMap
        """
        for k, v in propdict.items():
            if k != 'annotations' or k != 'frames':
                annotation.set_str(k, str(v))
        return annotation

    def serializeToFile(self, fname, annotations, customImgDir = ''):
        """
        Overwritten to write Okapi::Annotation files.
        """
        container = okapy.AnnotationContainer()

        for f in annotations:
            fileitem = okapy.AnnotationFileItem()
            if f.has_key(config.METADATA_LABELCLASS_TOKEN):
                f['type'] = f[config.METADATA_LABELCLASS_TOKEN]
                del f[config.METADATA_LABELCLASS_TOKEN]
            fileitem = self.convertDictToAnnotationPropertiesMap(fileitem, f)
            if fileitem.isImage():
                if f.has_key('annotations'):
                    for annotation in f['annotations']:
                        annoitem = okapy.AnnotationItem()
                        annoitem = self.convertDictToAnnotationPropertiesMap(annoitem, annotation)
                        fileitem.annotations().push_back(annoitem)
            elif fileitem.isVideo():
                if f.has_key('frames'):
                    for frame in f['frames']:
                        frameitem = okapy.AnnotationFrameItem()
                        frameitem = self.convertDictToAnnotationPropertiesMap(frameitem, frame)
                        if frame.has_key('annotations'):
                            for annotation in frame['annotations']:
                                annoitem = okapy.AnnotationItem()
                                annoitem = self.convertDictToAnnotationPropertiesMap(annoitem, annotation)
                                frameitem.annotations().push_back(annoitem)
                        fileitem.frames().push_back(frameitem)
            container.files().push_back(fileitem)

        container.WriteToFile(fname)


class JsonContainer(AnnotationContainer):
    """
    Simple container which writes the annotations to disk in JSON format.
    """

    def parseFromFile(self, _fname):
        """
        Overwritten to read JSON files.
        """
        fname = utils.toUTFStr(_fname)
                    
        f = open(_fname, "r")

        LOG.info(u"load json annotation file {}...".format(fname))

        anno = json.load(f)
        LOG.info(u"load json annotation file {} anno {}...".format(fname, anno))
        v = anno.get('version', None)
        vd = anno.get('versiondesc', None)
        d = anno.get('date', None)
        datelatest = str(datetime.datetime.now())
        self._version = config.VERSION if not v else v
        self._versiondesc = config.VERSIONDESC if not vd else vd
        self._date = datelatest if not d else d
        self._has_imgDir = False

        if "imgdir" in anno:
            self._imgdir = anno['imgdir']
            del anno['imgdir']
            self._has_imgDir = True
        anno = anno['labels']
        """
        for a in anno:
            if self._has_imgDir is True:
                #orgFileName = a[config.ANNOTATION_FILENAME_TOKEN]
                a[config.ANNOTATION_FILENAME_TOKEN] = os.path.join(self._imgdir, a[config.ANNOTATION_FILENAME_TOKEN])
                LOG.info(u"fileName was replaced from {} => {}".format(orgFileName, a[config.ANNOTATION_FILENAME_TOKEN]))
        """
        return anno

    def postprocessAnno(self, frmseq_annos_list):

        for index1, value in enumerate(frmseq_annos_list):
            thisfrm_annos_list = value.get('annotations', None)
            # print "postprocessAnno enter 2... thisfrm_annos_list = {}".format(thisfrm_annos_list)
            
            if ( (len(thisfrm_annos_list) == 1) and (thisfrm_annos_list[0].get('class', None) == config.DEFAULT_TOP_OBJECT)):
                thisfrm_annos_new = thisfrm_annos_list[0].get('subclass', [])
                # print "postprocessAnno 0 thisfrm_annos_new = {}".format(thisfrm_annos_new)

                other_item = None
                # other_item = [{key:v} for key, v in thisfrm_annos_list[0].iteritems() if key != 'x' and key != 'y' and key != 'width' and key != 'height' and key != 'class' and key != 'subclass']
                # print "postprocessAnno 1 other_item = {}".format(other_item)
                if other_item:
                    thisfrm_annos_new += other_item
                value['annotations'] = thisfrm_annos_new if thisfrm_annos_new else ''

        # print "postprocessAnno frmseq_annos_list = {}".format(frmseq_annos_list)
        return frmseq_annos_list
                

    def serializeToFile(self, fname, _annotations, _customImgDir = ''):
        """
        Overwritten to write JSON files.
        """
        annotations = copy.deepcopy(_annotations)
        
        utils.delUnusedAnnotation(annotations)
        
        # ============== [POSTPROCESSING START] =======================
        if config.ENABLE_TOP_OBJECT_MODE:
            # post-process annotations ready to saving to file
            # print "before postprocess... anno = {}".format(annotations)
            annotations = self.postprocessAnno(annotations)
            # print "after  postprocess... anno = {}".format(annotations)
        # ============== [POSTPROCESSING END  ] =======================        


        customImgdir = _customImgDir.strip()
        # print "_customImgDir = {} customImgdir = {}".format(_customImgDir, customImgdir)
        ann = {'version':config.VERSION, 'versiondesc':config.VERSIONDESC, 'date':str(datetime.datetime.now()), 'imgdir': customImgdir if customImgdir else self._imgdir, 'labels': annotations}

        f = open(fname, "w")
        json.dump(ann, f, indent=4, separators=(',', ': '), sort_keys=True)
        f.write("\n")
        return

class MsgpackContainer(AnnotationContainer):
    """
    Simple container which writes the annotations to disk in Msgpack format.
    """

    def parseFromFile(self, fname):
        """
        Overwritten to read Msgpack files.
        """
        import msgpack
        f = open(fname, "r")
        return msgpack.load(f)

    def serializeToFile(self, fname, annotations, customImgDir = ''):
        """
        Overwritten to write Msgpack files.
        """
        # TODO make all image filenames relative to the label file
        import msgpack
        f = open(fname, "w")


        msgpack.dump(annotations, f)


class YamlContainer(AnnotationContainer):
    """
    Simple container which writes the annotations to disk in YAML format.
    """

    def parseFromFile(self, fname):
        """
        Overwritten to read YAML files.
        """
        f = open(fname, "r")
        return yaml.load(f)

    def serializeToFile(self, fname, annotations, customImgDir = ''):
        """
        Overwritten to write YAML files.
        """
        f = open(fname, "w")
        yaml.dump(annotations, f)


class FileNameListContainer(AnnotationContainer):
    """
    Simple container to initialize the files to be annotated.
    """

    def parseFromFile(self, filename):
        self._basedir = os.path.dirname(filename)
        f = open(filename, "r")

        annotations = []
        for line in f:
            line = line.strip()
            relfilename = os.path.join(os.path.relpath(os.path.dirname(line), self._imgdir), os.path.basename(line))
            fileitem = {
                config.ANNOTATION_FILENAME_TOKEN: relfilename,
                config.METADATA_LABELCLASS_TOKEN: config.ANNOTATION_IMAGE_TOKEN,
                'annotations': [],
            }
            annotations.append(fileitem)

        return annotations

    def serializeToFile(self, filename, annotations, customImgDir = ''):
        raise NotImplemented("FileNameListContainer.save() is not implemented yet.")


class FeretContainer(AnnotationContainer):
    """
    Container for Feret labels.
    """

    def parseFromFile(self, filename):
        """
        Overwritten to read Feret label files.
        """
        f = open(filename)

        annotations = []
        for line in f:
            s = line.split()
            relfilename = os.path.join(os.path.relpath(os.path.dirname(s[0]), self._imgdir), os.path.basename(s[0]))
            fileitem = {
                config.ANNOTATION_FILENAME_TOKEN: relfilename + ".bmp",
                config.METADATA_LABELCLASS_TOKEN: config.ANNOTATION_IMAGE_TOKEN,
                'annotations': [
                    {config.METADATA_LABELCLASS_TOKEN: 'left_eye',  'x': int(s[1]), 'y': int(s[2])},
                    {config.METADATA_LABELCLASS_TOKEN: 'right_eye', 'x': int(s[3]), 'y': int(s[4])},
                    {config.METADATA_LABELCLASS_TOKEN: 'mouth',     'x': int(s[5]), 'y': int(s[6])}
                ]
            }
            annotations.append(fileitem)

        return annotations

    def serializeToFile(self, filename, annotations, customImgDir = ''):
        """
        Not implemented yet.
        """
        raise NotImplemented(
            "FeretContainer.serializeToFile() is not implemented yet."
        )
