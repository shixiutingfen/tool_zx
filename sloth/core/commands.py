# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

import sys
import sloth
import shutil
from pprint import pprint
from sloth.core.cli import BaseCommand, CommandError
from sloth.annotations.container import *
from optparse import make_option
from operator import itemgetter
import logging
import numpy as np
import shutil
from PyQt4.QtGui import QMainWindow, QSizePolicy, QWidget, QVBoxLayout, QAction,\
        QKeySequence, QLabel, QItemSelectionModel, QMessageBox, QFileDialog, QFrame, \
        QDockWidget, QProgressBar
from sloth.conf import config
        
LOG = logging.getLogger(config.LOG_FILE_NAME)


class ConvertCommand(BaseCommand):
    """
    Converts a label file from one file format to another.
    """
    args = '<input> <output>'
    help = __doc__.strip()

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError("convert: Expecting exactly 2 arguments.")

        input, output = args[:]
        LOG.info("converting from %s to %s" % (input, output))

        LOG.debug("loading annotations from %s" % input)
        self.labeltool.loadAnnotations(input, popupErrorMsg = False)

        LOG.debug("saving annotations to %s" % output)
        self.labeltool.saveAnnotations(output)


class CreateConfigCommand(BaseCommand):
    """
    Creates a configuration file with default values.
    """
    args = '<output>'
    help = __doc__.strip()
    option_list = BaseCommand.option_list + (
        make_option('-f', '--force', action='store_true', default=False,
            help='Overwrite the file if it exists.'),
    )

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Expect exactly 1 argument.")

        template_dir = os.path.join(sloth.__path__[0], 'conf')
        config_template = os.path.join(template_dir, 'default_config.py')
        target = args[0]

        if os.path.exists(target) and not options['force']:
            sys.stderr.write("Error: %s exists.  Use -f to overwrite.\n" % target)
            return

        try:
            shutil.copy(config_template, target)
            _make_writeable(target)
        except OSError as e:
            sys.stderr.write("Notice: Couldn't set permission bits on %s.\n" % target)


class DumpLabelsCommand(BaseCommand):
    """
    Dumps the labels from a label file to stdout.
    """
    args = '<labelfile>'
    help = __doc__.strip()

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Expect exactly 1 argument.")

        self.labeltool.loadAnnotations(args[0], popupErrorMsg = False)
        pprint(self.labeltool.annotations())


class AppendFilesCommand(BaseCommand):
    """
    Append image or video files to a label file.  Creates the label file if it
    does not exist before.  If the image or video file is already in the label
    file, it will not be appended again.
    """
    args = '<labelfile> videoFrmInterval <file1> [<file2> ...]'
    help = __doc__.strip()
    option_list = BaseCommand.option_list

    video_extensions = ['.vob', '.idx', '.mpg', '.mpeg', '.avi', 'mp4', 'h264', 'ts']

    def handle(self, *args, **options):
        if len(args) < 3:
            raise CommandError("Expect at least 3 arguments. Commands: sloth.py append 10 video1 imag2...")

        self.labeltool.loadAnnotations(args[0], popupErrorMsg = False)
        present_filenames = {os.path.join(self.labeltool._imgDir, a[config.ANNOTATION_FILENAME_TOKEN]) for a in self.labeltool.annotations()}

        frmInterval = args[1]
        for filename in args[2:]:

            if filename in present_filenames:
                LOG.info("Not adding file again: %s" % filename)
                continue

            _, ext = os.path.splitext(filename)
            if (not options[config.ANNOTATION_IMAGE_TOKEN] and ext.lower() in self.video_extensions) or options[config.ANNOTATION_VIDEO_TOKEN]:
                LOG.debug("Adding video file: %s" % filename)
                item, errorForFileHasBeenAdded = self.labeltool.addVideoFile(filename, frmInterval)
            else:
                LOG.debug("Adding image file: %s" % filename)
                item, errorForFileHasBeenAdded = self.labeltool.addImageFile(filename)
            
            if item:
                present_filenames.add(filename)

                if options['unlabeled']:
                    item.setUnlabeled(True)
                    
        self.labeltool.saveAnnotations(args[0])
        return

class CreateDatasetAnnotationCommand(BaseCommand):
    """
    Append image or video files to a label file.  Creates the label file if it
    does not exist before.  If the image or video file is already in the label
    file, it will not be appended again.
    """
    args = '<labelfile> <file1> [<file2> ...]'
    help = __doc__.strip()
    option_list = BaseCommand.option_list + (
        make_option('-u', '--unlabeled', action='store_true', default=False,
            help='Mark appended files as unlabeled.'),
        make_option(      '--image', action='store_true', default=False,
            help='Force appended files to be recognized as images.'),
        make_option(      '--video', action='store_true', default=False,
            help='Force appended files to be recognized as videos.'),
    )


    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("python slothx.py create <IMG_DIR>")

        import json

        data_path = args[0]
        if not os.path.isdir(data_path):
            QMessageBox.critical(None, config.GUI_CRITIAL_ERROR_TEXT,config.GUI_INVALID_PATH_TEXT.format(data_path ))
            sys.exit(1)
            
        data_path = os.path.normpath(data_path)    
        imgdir = "." # os.path.normpath(data_path)  # Note that, it is better use relative path to json file as imagedir
        filebasename = os.path.splitext(os.path.basename(data_path))[0]
        # print filebasename
        out_json = os.path.join(data_path, "{}.json".format(filebasename))
        # print out_json

        lines = []
        for root, dirs, files in os.walk(data_path):
            files = [ fi for fi in files if (fi.endswith(".jpg") or fi.endswith(".png") or fi.endswith(".bmp") or fi.endswith(".png"))]
            for name in sorted(files):
                lines.append(name)

        annotations = []

        # save to current dir
        for i in xrange(len(lines)):
            record = {config.METADATA_LABELCLASS_TOKEN:config.ANNOTATION_IMAGE_TOKEN, config.ANNOTATION_FILENAME_TOKEN:lines[i],'annotations':[]}
            # print "{}: filename {}".format(i, lines[i])
            annotations.append(record)
 
        json_data = {'version':config.VERSION, 'versiondesc':config.VERSIONDESC, 'date':str(datetime.datetime.now()), 'imgdir': imgdir, 'labels': annotations}

        f = open(out_json, "w")
        json.dump(json_data, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=True, encoding='gbk')
        f.write("\n")

        msg = config.GUI_CREATE_JSON_FILE_SUCCESS_TEXT.format(imgdir.decode('gbk'), len(lines), out_json.decode('gbk'), out_json.decode('gbk') )
        QMessageBox.critical(None, config.GUI_SUCCESS_TEXT, msg)

 

class statForMultipleJsonFileUnderSpecificFolderAnnotationCommand(BaseCommand):
    """
    Append image or video files to a label file.  Creates the label file if it
    does not exist before.  If the image or video file is already in the label
    file, it will not be appended again.
    """
    args = '<labelfile> <file1> [<file2> ...]'
    help = __doc__.strip()
    option_list = BaseCommand.option_list


    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("python slothx.py stat <JSON_FILES_DIR>")

        import json

        data_path = args[0]
        if not os.path.isdir(data_path):
            QMessageBox.critical(None, config.GUI_CRITIAL_ERROR_TEXT,config.GUI_INVALID_PATH_TEXT.format(data_path ))
            sys.exit(1)
            
        data_path = os.path.normpath(data_path)    
        jsonFiles = []
        for root, dirs, files in os.walk(data_path):
            files = [ fi for fi in files if (fi.endswith(".json"))]
            for name in sorted(files):
                jsonFiles.append(name)
                statisticForOneJsonFile(name)
 
                    
# remove annotation fields with 0 element for specific json file
class RemoveEmptyCommand(BaseCommand):


    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("python slothx.py removeempty <JSON>")

        import json
        json_file = os.path.join(args[0],args[0]+".json")
        f = open(json_file, "r")
        parse_json = json.load(f)
        anno = parse_json['labels']


        for i in xrange(len(anno)):
            uanno = []
            for an in anno[i]["annotations"]:
                if(config.METADATA_LABELCLASS_TOKEN in an):
                    uanno.append(an)
            anno[i]["annotations"] = uanno


        n_anno = []
        for i in xrange(len(anno)):
           if(len(anno[i]["annotations"]) > 0):
                n_anno.append(anno[i])
           else:
                os.remove(os.path.join(args[0], anno[i]["filename"]))

        json_data = {'version':config.VERSION, 'versiondesc':config.VERSIONDESC, 'date':str(datetime.datetime.now())}
        json_data.append(n_anno)
        f.close()

        f = open(json_file, "w")
        json.dump(json_data, f, indent=4, separators=(',', ': '), sort_keys=True)
        f.write("\n")
        print "before remove", len(anno)
        print "after remove", len(n_anno)



# reorder annotation items as per filename field for json annotation file
class ReorderCommand(BaseCommand):


    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("python slothx.py reoder <JSON>")

        import json
        import numpy
        json_file = os.path.join(args[0],args[0]+".json")
        f = open(json_file, "r")
        parse_json = json.load(f)
        anno = parse_json['labels']

        fid = []
        for i in xrange(len(anno)):
            temp = anno[i]["filename"]
            toks = temp.split("_")[-1].split(".")[0]
            fid.append(int(toks))

        sort_index = numpy.argsort(fid)

        nanno = []
        for i in xrange(len(sort_index)):
            nanno.append(anno[sort_index[i]])

        json_data = {'version':config.VERSION, 'versiondesc':config.VERSIONDESC, 'date':str(datetime.datetime.now())}
        json_data.append(nanno)
        f.close()

        f = open(json_file, "w")
        json.dump(json_data, f, indent=4, separators=(',', ': '), sort_keys=True)
        f.write("\n")
        print "reorder done"

class ShowStatsCommand(BaseCommand):
    """
   show stats of the json
    """

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("python slothx.py showstats <JSON>")

        import json
        json_file = os.path.join(args[0],args[0]+".json")
        f = open(json_file, "r")
        anno = json.load(f)
        anno = anno['labels']

        from sloth.conf import config
        classes =  config._class_name
        count = []
        for c in classes:
            count.append(0)

        for i in xrange(len(anno)):
            print anno[i]["filename"]


            for an in anno[i]["annotations"]:
                if(an[config.METADATA_LABELCLASS_TOKEN] == "Ignore"): continue
                ind = classes.index(an[config.METADATA_LABELCLASS_TOKEN])
                count[ind] = count[ind]+1

        import cv2
        img_sz = cv2.imread(os.path.join(args[0], anno[i]["filename"]))
        print "Image width = ", img_sz.shape[1], " height = ", img_sz.shape[0]
        print "#Images in", args[0], " = ",  len(anno)
        for i in xrange(len(classes)):
            print count[i], classes[i]
        print "Total", sum(count), "objects"

class MergeFilesCommand(BaseCommand):
    """
    Merge annotations of two label files and create a new one from it.
    If both input files have annotations for the same frame number, the result
    will contain the union of both annotations.

    Output format will be determined by the file suffix of output.
    """
    args = '<labelfile 1> <labelfile 2> <output>'
    help = __doc__.strip()

    def handle(self, *args, **options):
        if len(args) != 3:
            raise CommandError("Usage: %s" % self.args)

        input1, input2, output = args[:]
        LOG.info("merging %s and %s into %s" % (input1, input2, output))
        LOG.debug("loading annotations from %s" % input1)
        container1 = self.labeltool._container_factory.create(input1)
        an1 = container1.load(input1)

        LOG.debug("loading annotations from %s" % input2)
        container2 = self.labeltool._container_factory.create(input2)
        an2 = container2.load(input2)

        LOG.debug("merging annotations of %s and %s" % (input1, input2))
        an3 = self.merge_annotations(an1, an2)

        nanno = []
        try:
            fid = []
            for i in xrange(len(an3)):
                temp = an3[i]["filename"]
                toks = temp.split("_")[-1].split(".")[0]
                fid.append(int(toks))
                sort_index = np.argsort(fid)
                for i in xrange(len(sort_index)):
                    nanno.append(an3[sort_index[i]])
        except:
            fid = []
            nanno = sorted(an3, key=lambda x:x["filename"])
        
            
        LOG.debug("saving annotations to %s" % output)
        out_container = self.labeltool._container_factory.create(output)
        # out_container.save(an3, output)
        out_container.save(nanno, output)

    def merge_annotations(self, an1, an2, match_key=config.ANNOTATION_FILENAME_TOKEN):
        """This merges all annotations from an2 into an1."""

        for item in an2:
            matching_items = []
            if an1:
                matching_items = [it1 for it1 in an1 if
                              it1 and
                              it1[config.METADATA_LABELCLASS_TOKEN] == item[config.METADATA_LABELCLASS_TOKEN] and
                              it1[match_key] == item[match_key]]

            # If we can't find a match, we just append the item to an1.
            if len(matching_items) == 0:
                an1.append(item)
                continue

            # We found at least one match, just take the first.
            # But put out a warning if there were multiple possible matches.
            if len(matching_items) > 1:
                LOG.warning('Found %d possible matches for %s',
                               len(matching_items), item[config.ANNOTATION_FILENAME_TOKEN])
            
            match_item = matching_items[0]

            # Update the keys first.
            for key, value in item.iteritems():
                if key == 'annotations':
                    continue
                if match_item[config.METADATA_LABELCLASS_TOKEN] == config.ANNOTATION_VIDEO_TOKEN and key == 'frames':
                    continue
                if key in match_item and match_item[key] != value:
                    LOG.warning('found matching key %s, but values differ: %s <-> %s',
                                   key, str(value), str(value))
                    continue

                match_item[key] = value

            # Merge frames.
            if match_item[config.METADATA_LABELCLASS_TOKEN] == config.ANNOTATION_VIDEO_TOKEN:
                match_item['frames'] = self.merge_annotations(match_item['frames'], item['frames'], config.ANNOTATION_VIDEO_FILE_FRAME_IDX_TOKEN)
                match_item['frames'].sort(key=itemgetter(config.ANNOTATION_VIDEO_FILE_FRAME_IDX_TOKEN))

            # Merge annotations.
            if 'annotations' in match_item:
                match_item['annotations'].extend(item.get('annotations', []))

        return an1


# ==========================================================================================
# zx comment:
# clean annotation fields for duplicated images or frames data for specific json file
# ==========================================================================================
class CleanDuplicateDataCommand(BaseCommand):

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError("python slothx.py cleanduplicate <SRC_JSON> <DST_JSON>")

        import json
        
        # print "args = {}".format(args)
        input, output = args[:]
        LOG.info("Cleaning duplicate data in %s to %s" % (input, output))
        # print "loading annotations from {}".format(input)
        container1 = self.labeltool._container_factory.create(input)
        anno = container1.load(input)
        # print "anno = {}".format(anno)
        unique_data = {}     
        mediaFileIndex = 0      
        for i in xrange(len(anno)):
            if anno[i][config.METADATA_LABELCLASS_TOKEN] == config.ANNOTATION_VIDEO_TOKEN:
                key = "video, {}".format(anno[i][config.ANNOTATION_FILENAME_TOKEN])
                # print "unique_data = {}".format(unique_data)
                if (key in unique_data.keys()):
                    frames_record = unique_data[key][0]
                    # print "frames_record = {}".format(frames_record)
                else:
                    frames_record = {}
                for frame in anno[i]['frames']:
                    frmanno = frame.get('annotations', None)
                    frmidx = int(frame['frmidx'])
                    if (key in unique_data.keys()) and (frmidx in frames_record.keys()):
                        if not frmanno:
                            continue
                        # print "frmidx = {}".format(frmidx)
                        # print "frames_record[{}] = {}".format(frmidx, frames_record[frmidx])
                        frames_record[frmidx][0] += frame['annotations']
                    else:
                        # note that, we use frameidx as frameRecordOder
                        frames_record[frmidx] = [frame['annotations'], frmidx]

                unique_data[key] = [frames_record, mediaFileIndex]
                # print "mediaFileIndex = {} : after unique_data = {}".format(mediaFileIndex, unique_data)
                mediaFileIndex += 1
            elif anno[i][config.METADATA_LABELCLASS_TOKEN] == config.ANNOTATION_IMAGE_TOKEN:
                key = "image, {}".format(anno[i][config.ANNOTATION_FILENAME_TOKEN])
                image_record = anno[i].get('annotations', None)
                # print "image_record = {}".format(image_record)
                if key in unique_data.keys():
                    if not image_record:
                        continue
                    unique_data[key][0] += image_record
                    # print u"unique_data[{}] = {}".format(key, unique_data[key])
                else:
                    unique_data[key] = [image_record, mediaFileIndex]
                    mediaFileIndex += 1
       
        # ==============================================================
        # convert unique_data to annotation style data
        # ==============================================================
        # unique_data example1 (video):
        # uique_data = {'video, E:/colorAnno/sz2/192.168.1.62_01_20160311174825130_1/192.168.1.62_01_20160311174825130_1.mp4': 
        # [{0:  [[], 0], 
        #  450: [[{u'subclass': [{u'y': 651.8255869054859, u'height': 151.58734579197346, u'width': 149.90304194984037, u'uppercolor0': u'#863C05', u'x': 1087.2181300968764, u'uppercolor0Tag': u'Brown', u'class': u'upper'}, {u'height': 189.4841822399668, u'width': 117.90126894931268, u'lowercolor0': u'#02107F', u'lowercolor0Tag': u'SapphireBlue', u'y': 805.939388460659, u'x': 1088.0602820179429, u'class': u'lower'}], u'height': 421.0759605332596, u'width': 165.06177652903784, u'y': 581.0848255358983, u'x': 1072.059395517679, u'class': u'pedestrain'}], 3], 
        # 5700: [[], 0], 
        # 300:  [[{u'subclass': [{u'y': 377, u'height': 77, u'width': 177, u'uppercolor0': u'#ff0000', u'x': 277, u'uppercolor0Tag': u'Red', u'class': u'upper'}], u'height': 55, u'width': 177.0, u'y': 377, u'x': 277, u'class': u'pedestrain'}, {u'subclass': [{u'y': 497.52663138185187, u'height': 134.98321571704503, u'width': 119.45417320092486, u'x': 547.1001132602356, u'uppercolor0': u'#0432FF', u'uppercolor1': u'#000000', u'uppercolor0Tag': u'Blue', u'uppercolor1Tag': u'Black', u'class': u'upper'}, {u'height': 187.5430519254519, u'width': 81.2288377766289, u'lowercolor0': u'#505050', u'lowercolor0Tag': u'DarkGray', u'y': 634.8989305629154, u'x': 568.6018644364021, u'class': u'lower'}], u'height': 382.850625108964, u'width': 122.44052753094797, u'y': 445.5640660394496, u'x': 546.502842394231, u'class': u'pedestrain'}], 2], 
        # 500: [[], 4], 
        # 150: [[{u'subclass': [{u'y': 388, u'height': 88, u'width': 188, u'uppercolor0': u'#ff0000', u'x': 288, u'uppercolor0Tag': u'Red', u'class': u'upper'}], u'height': 66, u'width': 166.0, u'y': 366, u'x': 266, u'class': u'pedestrain'}, {u'subclass': [{u'y': 488, u'height': 288, u'width': 288, u'uppercolor0': u'#ff0000', u'x': 388, u'uppercolor0Tag': u'Red', u'class': u'upper'}], u'height': 266, u'width': 266.0, u'y': 466, u'x': 366, u'class': u'pedestrain'}], 1], 
        # 5850: [[{u'subclass': [{u'y': 155.31914893617042, u'height': 83.68794326241144, u'width': 48.936170212766, u'uppercolor0': u'#C4AE85', u'x': 817.7304964539018, u'uppercolor0Tag': u'Khaki', u'class': u'upper'}, {u'height': 119.85815602836894, u'width': 81.5602836879433, u'lowercolor0': u'#000000', u'lowercolor0Tag': u'Black', u'y': 241.13475177304994, u'x': 793.6170212765968, u'class': u'lower'}], u'height': 249.6453900709223, u'width': 100.00000000000011, u'y': 114.18439716312072, u'x': 778.7234042553201, u'class': u'pedestrain'}], 1], 
        # 1500: [[{u'subclass': [{u'y': 627.0000000000002, u'height': 149.0000000000001, u'width': 114.00000000000011, u'uppercolor0': u'#000000', u'x': 815.0000000000003, u'uppercolor0Tag': u'Black', u'class': u'upper'}, {u'height': 216.0000000000001, u'width': 89.00000000000011, u'lowercolor0': u'#000000', u'lowercolor0Tag': u'Black', u'y': 777.0000000000003, u'x': 831.0000000000003, u'class': u'lower'}], u'height': 444.0000000000002, u'width': 123.00000000000011, u'y': 555.0000000000002, u'x': 812.0000000000003, u'class': u'pedestrain'}], 5]
        # }, 1]}
        # ==============================================================
        fileitemsList = []
        # valuelist format: [[mediaFileAnnotations, mediaFileDisplayOrder, mediaFilePathWithPrefix] ...]
        valuelist = [ [value[0], value[1], key] for key, value in unique_data.iteritems() ]
        valuelist = sorted(valuelist, key = lambda d: d[1], reverse = 0)
        for index, item in enumerate(valuelist):
            mediatype = item[2][0:5]
            mediafilename = item[2][7:]
            mediaFileAnnotations = item[0]

            if mediatype == config.ANNOTATION_VIDEO_TOKEN:
                fileitem = {
                    config.ANNOTATION_FILENAME_TOKEN: mediafilename,
                    config.METADATA_LABELCLASS_TOKEN: config.ANNOTATION_VIDEO_TOKEN,
                    config.ANNOTATION_FRAMES_TOKEN: [],
                }

                # fitemlist format: [[frameAnnotations,frameRecordOrder, frmIdx] ...]
                fitemlist = [[value[0], value[1], key] for key, value in mediaFileAnnotations.iteritems()]
                fitemlist = sorted(fitemlist, key=lambda d: d[1], reverse=0)
                fileitem['frames'] = [{
                                      'annotations': fitem[0],
                                      config.ANNOTATION_VIDEO_FILE_FRAME_IDX_TOKEN: fitem[2],
                                      config.ANNOTATION_VIDEO_FILE_FRAME_TIMESTAMP_TOKEN: 0,
                                      config.METADATA_LABELCLASS_TOKEN: config.ANNOTATION_FRAME_TOKEN
                                  } for index, fitem in enumerate(fitemlist) ]

            elif mediatype == config.ANNOTATION_IMAGE_TOKEN:
                fileitem = {
                    config.ANNOTATION_FILENAME_TOKEN: mediafilename,
                    config.METADATA_LABELCLASS_TOKEN: config.ANNOTATION_IMAGE_TOKEN,
                    'annotations' : mediaFileAnnotations
                }

            fileitemsList.append(fileitem)

        # ==============================================================
        # dump annotation_style data to file
        # ==============================================================
        # print "saving annotations to {}".format(output)
        out_container = self.labeltool._container_factory.create(output)
        out_container.save(fileitemsList, output)

        return

        
        
# read "labels" fields in annotation file
def readAnnoFromAnnotationFile(annotationFilePath):
    _container_factory = AnnotationContainerFactory(config.CONTAINERS)
    container1 = _container_factory.create(annotationFilePath)
    if not container1: 
        return None
    an1 = container1.load(annotationFilePath)
    return an1

def _make_writeable(filename):
    """
    Make sure that the file is writeable. Useful if our source is
    read-only.
    """
    import stat
    if sys.platform.startswith('java'):
        # On Jython there is no os.access()
        return
    if not os.access(filename, os.W_OK):
        st = os.stat(filename)
        new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
        os.chmod(filename, new_permissions)

# command dictionary str -> Command
_commands = {}


def register_command(name, command):
    global _commands
    _commands[name] = command


def get_commands():
    global _commands
    return _commands

class setDefaultPersonBikeTypeToLightMotor(BaseCommand):

    def handle(self, *args, **options):
       if len(args) != 1:
           raise CommandError("python slothx.py setDefaultPersonBikeTypeToLightMotor <JSON>")

       import json
       json_file = args[0]

       self.labeltool.loadAnnotations(args[0], popupErrorMsg = False)
       annos = self.labeltool.annotations()
       for index, frmAnno in enumerate(annos):
           anno = frmAnno['annotations']
           if not anno:
               continue
           for objindex, objanno in enumerate(anno):
               objclass = objanno.get('class', '')
               if objclass.lower() == 'personbike':
                   objtype = objanno.get('Type', '')
                   if objtype.lower() == '':
                       objanno['Type'] = 'lightmotor'
                       print "set ..."
           print "anno = {}".format(anno)
           frmAnno['annotations'] = anno

       self.labeltool._container.save(annos, "C:\\Users\\zx\\Desktop\\convert.json")



# ==========================================================================================
# zx comment:
# clean annotation fields for duplicated images or frames data for specific json file
# ==========================================================================================
class SplitAnnoFileToMulitpleFiles(BaseCommand):

    def handle(self, *args, **options):
        if (len(args) != 3) and (len(args) != 4):
            raise CommandError("python slothx.py split <SRC_JSON> <DST_JSONS_BASEFILENAME> <PIC_NUM_IN_EACH_FILE> <CopyMediaFilesToSubFolder>")

        import json
        
        print "args = {}".format(args)
        input, output_fbasename, picNum = args[:3]
        enableCopyMediaFilesToSubFolder = int(args[3]) if (len(args) == 4) else 0
        # enableCopyMediaFilesToSubFolder= 1
        picNum = int(picNum)
        LOG.info("split annotation data from %s to %s with filter and picNum %d" % (input, output_fbasename, picNum))

        outtopdir = os.path.dirname(output_fbasename)
        if not os.path.exists(outtopdir):
            print "Error: output dir \'{}\' doesn't exist!".format(outtopdir)

        # print "loading annotations from {}".format(input)
        container1 = self.labeltool._container_factory.create(input)

        # get fields of "label" key
        anno_org = container1.load(input)
        mediaDir = container1._imgdir
        # print "anno_org = {}".format(anno_org)
        unique_data = {}     
        mediaFileIndex = 0

        fidx = 0
        fnum = 0
        imgsAnnoList = []
        topAnnoDict = {}
        icnt = 0
        outpartdir = None
        for i in xrange(len(anno_org)):
            if anno_org[i][config.METADATA_LABELCLASS_TOKEN] == config.ANNOTATION_VIDEO_TOKEN:
                framesAnno = anno_org[i].get('frames', None) 
                fnum = len(framesAnno) if framesAnno else 0
                
                frms = {} 
                for p in xrange(0, fnum, picNum):
                    topAnnoDict = { k : v for k, v in anno_org[i].iteritems() if k != 'frames' }
                    topAnnoDict['frames'] = framesAnno[p : p + picNum]
                    outJsonFileName = output_fbasename + "_{}.json".format(fidx)
                    out_container = self.labeltool._container_factory.create(outJsonFileName)
                    out_container.save([topAnnoDict], outJsonFileName, mediaDir)
                    
                    fidx += 1
                    
            elif anno_org[i][config.METADATA_LABELCLASS_TOKEN] == config.ANNOTATION_IMAGE_TOKEN:
                framesAnno = anno_org[i].get('annotations', None)
                fnum = len(framesAnno) if framesAnno else 0

                icnt += 1
                print "icnt = {} ... append".format(icnt)
                imgsAnnoList.append(anno_org[i])

                outpartdir = output_fbasename # + "{}".format(fidx)
                outpartdir_abs = os.path.abspath(outpartdir)
                pos = outpartdir_abs.rfind("\\")
                if not pos:
                    pos = outpartdir_abs.rfind("/")
                outpartparentname = os.path.abspath(outpartdir)[pos+1:]
                
                outpartparentname = outpartparentname + "{}".format(fidx) 

                if not os.path.exists(outpartdir):
                    os.makedirs(outpartdir)

                if enableCopyMediaFilesToSubFolder:
                    mediafilepath = os.path.join(mediaDir, anno_org[i].get('filename', None))
                    if not os.path.exists(mediafilepath):
                        mediafilepath = os.path.join(os.path.dirname(input), mediafilepath)
                    mediafilename = os.path.basename(mediafilepath)

                    # copy media files to partdir
                    outpart_mediafilepath = os.path.join(outpartdir, mediafilename)
                    print "copy {} => {} ...".format(mediafilepath, outpart_mediafilepath)
                    shutil.copy(mediafilepath, outpart_mediafilepath)

                if ((icnt % picNum) == 0):
                    print "icnt = {} ... dump".format(icnt)

                    """
                    mediaAbsDir = os.path.abspath(mediaDir)
                    print "outpartdir = {} mediaDir = {} ".format(outpartdir, mediaAbsDir)
                    try:
                        outpart_imgdir = os.path.join(os.path.relpath(outpartdir, mediaAbsDir), mediaDir)
                    except:
                        outpart_imgdir = os.path.join(os.path.relpath(os.path.splitdrive(mediaAbsDir)[0], mediaAbsDir),
                                                      "../", outpartdir)
                    """
                    outpart_imgdir = "."
                    outJsonFileName = os.path.join(outpartdir, outpartparentname +".json".format(fidx))
                    out_container = self.labeltool._container_factory.create(outJsonFileName)
                    out_container.save(imgsAnnoList, outJsonFileName, outpart_imgdir)

                    imgsAnnoList = []
                    fidx += 1

        # write left data
        if imgsAnnoList:
            outpart_imgdir = "."
            outJsonFileName = os.path.join(outpartdir, outpartparentname + ".json".format(fidx))
            out_container = self.labeltool._container_factory.create(outJsonFileName)
            out_container.save(imgsAnnoList, outJsonFileName, outpart_imgdir)
            imgsAnnoList = []
            fidx += 1

        return



# TODO automatically discover these
register_command('convert', ConvertCommand())
register_command('createconfig', CreateConfigCommand())
register_command('dumplabels', DumpLabelsCommand())
register_command('appendfiles', AppendFilesCommand())
register_command('mergefiles', MergeFilesCommand())
register_command('cleanduplicate', CleanDuplicateDataCommand())
register_command('create', CreateDatasetAnnotationCommand())
register_command('stat', CreateDatasetAnnotationCommand())
register_command('showstats', ShowStatsCommand())
register_command('removeempty', RemoveEmptyCommand())
register_command('reorder', ReorderCommand())
register_command('setDefaultPersonBikeTypeToLightMotor', setDefaultPersonBikeTypeToLightMotor())
register_command('split', SplitAnnoFileToMulitpleFiles())
