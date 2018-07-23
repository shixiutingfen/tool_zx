# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"


"""
The annotationmodel module contains the classes for the AnnotationModel.
"""
import os.path
import time
import logging
import copy
from collections import MutableMapping
from PyQt4.Qt import QColor, QRectF, QPolygonF, QLineF, QPointF
from PyQt4.QtGui import QTreeView, QItemSelection, QItemSelectionModel, QSortFilterProxyModel, QBrush
from PyQt4.QtCore import QModelIndex, QAbstractItemModel, Qt, pyqtSignal, QVariant
from sloth.conf import config
from compiler.ast import flatten

LOG = logging.getLogger(config.LOG_FILE_NAME)
ENABLE_MERGE_SAME_TYPE_ITEM_IN_SUBCLASS = False

ItemRole, DataRole, ImageRole = [Qt.UserRole + ur + 1 for ur in range(3)]


class ModelItem:
    def __init__(self):
        self._loaded = True
        self._model = None
        self._parent = None
        self._row = -1
        if not hasattr(self, "_children"):
            self._children = []

    def _load(self, index):
        pass

    def _ensureLoaded(self, index):
        if not self._loaded:
            if not isinstance(self._children[index], ModelItem):
                # Need to set the before actually loading to avoid
                # endless recursion...
                # print "index = {} self._children[index] = {}".format(index, self._children[index])
                self._load(index)
                return True
        return False

    def _ensureAllLoaded(self):
        if not self._loaded:
            for i in range(len(self._children)):
                self._ensureLoaded(i)
            return True
        return False

    def hasChildren(self):
        return len(self._children) > 0

    def childHasChildren(self, row):
        return self.childAt(row).hasChildren()

    def row(self):
        return self._row

    def rowCount(self):
        return len(self._children)

    def childRowCount(self, pos):
        return self.childAt(pos).rowCount()

    def children(self):
        self._ensureAllLoaded()
        return self._children

    def model(self):
        return self._model

    def parent(self):
        return self._parent

    def data(self, role=Qt.DisplayRole, column=0):
        if role == Qt.DisplayRole:
            return ""
        if role == Qt.BackgroundRole:
            c = self.getColor()
            if c is not None:
                return QBrush(c)
        if role == ItemRole:
            return self
        else:
            return None

    def childData(self, role=Qt.DisplayRole, row=0, column=0):
        return self.childAt(row).data(role, column)

    def flags(self, column):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def childFlags(self, row, column):
        return self.childAt(row).flags(column)

    def setData(self, value, role=Qt.DisplayRole, column=0):
        return False

    def childAt(self, pos):
        self._ensureLoaded(pos)
        return self._children[pos]

    def getPreviousSibling(self, step=1):
        return self.getSibling(self._row-step)

    # zx added @ 2016-08-03. don't warp to the ending item if start of item is reached compared to getPreviousSibling.
    def getPreviousSiblingX(self, step=1):
        if self._row < step:
            # print "Current item has been the first item! No prev item can be found!"
            return None
        return self.getSibling(self._row-step)

    def getNextSibling(self, step=1):
        return self.getSibling(self._row+step)

    # zx added @ 2016-08-03. don't warp to the beginning item if end of item is reached compared to getPreviousSibling.
    def getNextSiblingX(self, step=1):

        if (self._row + step) >= self._parent.rowCount():
            # print "Current item has been the last item! No next item can be found!"
            return None
        return self.getSibling(self._row+step)

    def getSibling(self, row):
        if self._parent is not None:
            try:
                return self._parent.childAt(row)
            except:
                pass
        return None

    def _attachToModel(self, model):
        #assert self.model() is None
        #assert self.parent() is not None
        #assert self.parent().model() is not None

        self._model = model
        for item in self._children:
            if isinstance(item, ModelItem):
                item._attachToModel(model)

    def index(self, column=0):
        if self._parent is None:
            return QModelIndex()
        if column >= self._model.columnCount():
            return QModelIndex()
        return self._model.createIndex(self._row, column, self._parent)

    def addChildSorted(self, item, signalModel=True):
        LOG.info("ModelItem.addChildSorted ...self = {} self.anno = {} item = {} item.anno = {} signalMode = {}".format(self, 
            GET_ANNOTATION(self), item, GET_ANNOTATION(item), signalMode))
        self.insertChild(-1, item, signalModel=signalModel)

    def appendChild(self, item, signalModel=True):
        # LOG.info("ModelItem.appendChild(item = {} anno = {})".format(item, item.getAnnotations(False) if hasattr(item, 'getAnnotations')  else None))
        self.insertChild(-1, item, signalModel=signalModel)

    def replaceChild(self, pos, item):
        item._parent = self
        item._row    = pos
        self._children[pos] = item
        if self._model is not None:
            self._children[pos]._attachToModel(self._model)
    
    def PRINT_CHILDREN(self, children_list):
        for i in children_list:
            if isinstance(i, AnnotationModelItem):
                LOG.info("child {} : item = {} anno = {}".format(i._row, i, i.getAnnotations()))
            
    def insertChild(self, pos, item, signalModel=True):
        # LOG.info("ModelItem.insertChild().. begin ... self = {} self.anno = {} pos = {}, item = {}, item.anno = {} signalMode = {})".format(self, self.getAnnotations(), pos, item, item.getAnnotations() if hasattr(item, 'getAnnotations') else None, signalModel))
        # LOG.info("ModelItem.insertChild().. begin ... self._children = {}".format(self._children))
        if pos >= 0:
            next_row = min(pos, len(self._children))
        else:
            next_row = len(self._children)

        if self._model is not None and signalModel:
            self._model.beginInsertRows(self.index(), next_row, next_row)
        # LOG.info("ModelItem.insertChild().. begin 1... self = {} self.anno = {} ".format(self, self.getAnnotations()))


        item._parent = self
        item._row    = next_row
        # LOG.info("ModelItem.insertChild().. begin 1-2... self = {} self.anno = {} type(self._children) = {} self._children = {}".format(self, self.getAnnotations(), type(self._children), self._children))
        # self.PRINT_CHILDREN(self._children)

        self._children.insert(next_row, item)
        # LOG.info("ModelItem.insertChild().. begin 2... self = {} self.anno = {} type(self._children) = {} self._children = {}".format(self, self.getAnnotations(), type(self._children), self._children))
        # self.PRINT_CHILDREN(self._children)

        if pos >= 0:
            for i, c in enumerate(self._children):
                c._row = i

        if self._model is not None:
            item._attachToModel(self._model)
            if signalModel:
                self._model.endInsertRows()
        # LOG.info("ModelItem.insertChild().. end ... parent_anno = {}".format(self.getAnnotations()))

    def appendChildren(self, items, signalModel=True):
        # LOG.info("ModelItem.appendChildren(items = {}, signalMode = {})... self._children = {}".format(items, signalModel, self._children))
        #for item in items:
            #assert isinstance(item, ModelItem)
            #assert item.model() is None
            #assert item.parent() is None

        next_row = len(self._children)
        if self._model is not None and signalModel:
            self._model.beginInsertRows(self.index(), next_row, next_row + len(items) - 1)

        for i, item in enumerate(items):
            item._parent = self
            item._row = next_row + i
            self._children.append(item)
            # LOG.info("ModelItem.appendChildren()... item = {} item._row = {} item.key() = {} item.parent = {}".format(item, item._row, item.key(), item.parent))

        if self._model is not None:
            for item in items:
                item._attachToModel(self._model)
            if signalModel:
                self._model.endInsertRows()

    def delete(self):
        if self._parent is None:
            raise RuntimeError("Trying to delete orphan")
        else:
            self._parent.deleteChild(self)

    def deleteChild(self, arg):
        # Grandchildren are considered deleted automatically
        if isinstance(arg, ModelItem):
            return self.deleteChild(self._children.index(arg))
        else:
            if arg < 0 or arg >= len(self._children):
                raise IndexError("child index out of range")
            self._ensureLoaded(arg)

            if self._model is not None:
                self._model.beginRemoveRows(self.index(), arg, arg)

            del self._children[arg]

            # Update cached row numbers
            for i, c in enumerate(self._children):
                c._row = i

            if self._model is not None:
                self._model.endRemoveRows()

    def deleteAllChildren(self):
        self._ensureAllLoaded()
        if self._model is not None:
            self._model.beginRemoveRows(self.index(), 0, len(self._children) - 1)

        self._children = []

        if self._model is not None:
            self._model.endRemoveRows()

    def getColor(self, outputAlpha = False):
        return None


class RootModelItem(ModelItem):
    def __init__(self, model, filedir, files):
        ModelItem.__init__(self)
        self._model = model
        self._toload = []
        self._filedir = filedir
        for f in files:
            self._toload.append(f)
            self._children.append(f)
        self._loaded = False

    def _load(self, index):
        # LOG.info(u"index {} self._children {} self._toload {} ...".format(index, self._children, self._toload))
        # LOG.info(u"[ZXD] self._children [{}] = {} ...".format(index, self._children[index]))
        if self._children[index] in self._toload:
            self._toload.remove(self._children[index])
        LOG.info(u"RootModelItem._load... create FileModelItem for {}, {}".format(index+1, self._children[index]))
        fi = FileModelItem.create(self._filedir, self._children[index], index+1)
        self.replaceChild(index, fi)
        if len(self._toload) == 0:
            self._loaded = True

    def childHasChildren(self, pos):
        if isinstance(self._children[pos], ModelItem):
            return self._children[pos].hasChildren()
        else:
            # Hack to speed things up...
            return True

    def childFlags(self, row, column):
        if isinstance(self._children[row], ModelItem):
            return self._children[row].flags(column)
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def appendChild(self, item, signalModel=True):
        if isinstance(item, FileModelItem):
            ModelItem.appendChild(self, item, signalModel=signalModel)
        else:
            raise TypeError("Only FileModelItems can be attached to RootModelItem")

    def appendFileItem(self, filedir, fileinfo):
        LOG.info(u"RootModelItem.appendFileItem... FileModelItem.create({}, {}, {}) ...".format(filedir, fileinfo, self._model.root().numFiles() + 1))
        
        errorForFileHasBeenAdded = False
        for c in self._children:
            if (c[config.ANNOTATION_FILENAME_TOKEN] == fileinfo[config.ANNOTATION_FILENAME_TOKEN]) and (c[config.METADATA_LABELCLASS_TOKEN] == fileinfo[config.METADATA_LABELCLASS_TOKEN]):
                errorForFileHasBeenAdded = True
                return None, errorForFileHasBeenAdded

        item = FileModelItem.create(filedir, fileinfo, self._model.root().numFiles() + 1)
        self.appendChild(item)
        return item, errorForFileHasBeenAdded

	
	
    def numFiles(self):
        return len(self.children())

    def numAnnotations(self):
        count = 0
        for ann in self._model.iterator(AnnotationModelItem):
            count += 1
        return count

    def updateAnnotation(self, annoKey, annoValue):
        pass
       
    def getAnnotations(self, recursive = True):
        return [child.getAnnotations(recursive) for child in self.children()
                if hasattr(child, 'getAnnotations')]

    # zx add @ 2016-10-12
    def getAnnotationsNum(self):
        cnt = 0
        for child in self.children():
            if hasattr(child, 'getAnnotationsNum'):
                # print self, child
                cnt += child.getAnnotationsNum()
        return cnt



    def get_label_class(self):
        return None
    def getSpecificLabelsNum(self, labelclassname, labelvalue):
        cnt = 0
        # raw_input("enter here 0")
        for child in self.children():
            if hasattr(child, 'getSpecificLabelsNum'):
                cnt += child.getSpecificLabelsNum(labelclassname, labelvalue)
        return cnt



class KeyValueModelItem(ModelItem, MutableMapping):

    def printThisItem(self):
        LOG.info("KeyValueModelItem {} - printThisItem info =====START====================== ".format(self))
        for itemkey, itemval in self._items.iteritems():
            LOG.info("item.key() = {} item.val() = {}....".format(itemkey, itemval))
            if itemkey == 'subclass':
                LOG.info("!!!!!!!!!!!!!! item.key = Subclass .... !!!!!!!!!!!!!!")
                for childitem in itemval:
                    childitem.printThisItem()
            else:
               LOG.info("itemkey = {} itemval = {} itemdata = {} itemparent() = {}".format(itemkey, itemval, itemval.data(role=Qt.DisplayRole, column = 1), itemval._parent))
 
        LOG.info("KeyValueModelItem {} - printThisItem info ======END =====================\n ".format(self))

    def determineChildKeyValueModelItemInsertPos(self, childKeyValueModelItemName):
        thisorder = config.ANNOTATION_KEYS_ORDER.get(childKeyValueModelItemName, -1) if childKeyValueModelItemName else -1
        thisinsertpos = len(self._children)
        for idx, child in enumerate(self._children):
            siblingname = child.data(role=Qt.DisplayRole, column=0) if child else None 
            siblingorder = config.ANNOTATION_KEYS_ORDER.get(siblingname, -1) if siblingname else -1
            if ( thisorder < siblingorder ):
                thisinsertpos = idx
                break
        thisinsertpos = len(self._children) if thisinsertpos < 0 else thisinsertpos     
        # print "childKeyValueModelItemName = {} thisinsertpos = {}".format(childKeyValueModelItemName, thisinsertpos)
        return thisinsertpos
                            
    # zx999
    def generateRowModelItems(self, dict, rowModelItemsList):
        modelItemsList = []
        # LOG.info("Parent KeyValueModelItem {} - generateModelItems(dict = {}, rowModelItemsList = {}) ... ".format(self, dict, rowModelItemsList))
        for key in dict.keys():
            if key not in self._hidden and key is not None:
                # LOG.info("Parent key = {} .. under processing... dict = {}".format(key, dict[key]))
                
                if key == 'subclass':
                    
                    for k in dict[key]:
                        
                        childdict = k
                        # LOG.info("Child {} .. under processing... ".format(childdict))
                        childmodelItem = self.spawnThisLevelModelItem(self._hidden, childdict)
                        
                        # LOG.info("create KeyValueModelItem(childdict = {}) ...childmodelItem = {} ".format(childdict, childmodelItem))
                        
                        if self._items.has_key(key):
                            self._items[key].append(childmodelItem)
                        else:
                            self._items[key] = [childmodelItem]

                        # zx comment: please exchange below codes if you find inserchild is not safe
                        # if 0
                        # self.appendChild(childmodelItem, True)
                        # else
                        """
                        order = config.ANNOTATION_KEYS_ORDER.get(childdict.get(config.METADATA_LABELCLASS_TOKEN, ''), None)
                        if order is not None:
                            self.insertChild(order, childmodelItem, True)
                        else:
                            self.appendChild(childmodelItem, True)
                        """
                        # endif

                        childmodelItem_insertPos = self.determineChildKeyValueModelItemInsertPos(childdict.get(config.METADATA_LABELCLASS_TOKEN, None))
                        self.insertChild(childmodelItem_insertPos, childmodelItem, True)
                        
                        # LOG.info("*** Parent KeyValueModelItem {} appendChild KeyValueModelItem(chilRowModelItemsList = {}, signalMode = {})!".format(self, rowModelItem, False))


                else:
                    rowModelItem = KeyValueRowModelItem(key)
                    self._items[key] = rowModelItem
                    
                    # zx comment: please exchange below codes if you find insertChild is not safe
                    # if 0
                    # self.appendChild(rowModelItem, False)
                    # else
                    """
                    order = config.ANNOTATION_KEYS_ORDER.get(key, None)
                    if order is not None:
                        self.insertChild(order, rowModelItem, False)
                    else:
                        self.appendChild(rowModelItem, False)
                    """
                    # endif
                    modelItem_insertPos = self.determineChildKeyValueModelItemInsertPos(key)
                    self.insertChild(modelItem_insertPos, rowModelItem, False)

                                                
                    # LOG.info("*** Parent KeyValueModelItem {} appendChild KeyValueRowModelItem(chilRowModelItemsList = {}, signalMode = {})!".format(self, rowModelItem, False))
            # else:
            #     LOG.info("Parent key = {} .. skipped for hidden...".format(key))

        # LOG.info("Parent KeyValueModelItem {} - generateModelItems(dict = {}, rowModelItemsList = {}) ok!\n ".format(self, dict, rowModelItemsList))
        return modelItemsList


 
    def spawnThisLevelModelItem(self, hidden=None, properties=None, rowModelItemsList = []):
        LOG.info("**** call KeyValueModelItem.spawnThisLevelModelItem(anno = {})...".format(properties))
        t = KeyValueModelItem(hidden, properties, rowModelItemsList)
        LOG.info("*** call KeyValueModelItem.spawnThisLevelModelItem(anno = {})... ok! AnnotationModelItem = {}".format(properties, t))



    def __init__(self, filedir=None, hidden=None, properties=None, rowModelItemsList = []):
        # LOG.info("\nKeyValueModelItem.init 1 (properties = {}) ... ".format(properties))
        ModelItem.__init__(self)
        self._dict = {}
        self._items = {}
        self._hidden = set(hidden or [])
        # LOG.info("\nKeyValueModelItem.init 2 (properties = {}) ... ".format(properties))
        hiddentset = config.DISPLAY_HIDEN_METADATAS_IN_ANNOTATION_SET
        hiddentset.add(None)
        self._hidden.update(hiddentset)

        # LOG.info("\nKeyValueModelItem.init 3 (properties = {}) ... ".format(properties))

        # dummy key/value so that pyqt does not convert the dict
        # into a QVariantMap while communicating with the Views
        self._dict[None] = None
        # LOG.info("\nKeyValueModelItem.init(properties = {}) ... ".format(properties))
        if properties is not None:
            for key, value in properties.items():
                if key != 'subclass':
                    # if (key == config.ANNOTATION_FILENAME_TOKEN) and (filedir):
                    #    value = os.path.join(filedir, value)
                    self._dict.update({key:value})
                    
            # LOG.info("\nKeyValueModelItem.init(properties = {}) dict = {}..".format(properties, self._dict))
            rowModelItemsList = self.generateRowModelItems(properties, rowModelItemsList)
          
        # self.printThisItem()       



    # def addChildSorted(self, item, signalModel=True):
    #     LOG.info("KeyValueModelItem.addChildSorted ...self = {} self.anno = {} item = {} item.anno = {} signalMode = {}".format(self, 
    #         self.getAnnotations() if hasattr(self, 'getAnnotations') else None, item, item.getAnnotations() if hasattr(item, 'getAnnotations') else None, signalModel))
    #     if isinstance(item, KeyValueRowModelItem):
    #         next_row = 0
    #         for child in self._children:
    #             if not isinstance(child, KeyValueRowModelItem) or child.key() > item.key():
    #                 break
    #             next_row += 1
    # 
    #         self.insertChild(next_row, item, signalModel)
    #     else:
    #         LOG.info("KeyValueModelItem.appendChild ... call appendChild ( item = {} item.anno = {} )".format(item, item.getAnnotations()))
    #         self.appendChild(item, signalModel)


    def addChildSorted(self, item, signalModel=True):
        LOG.info("KeyValueModelItem.addChildSorted ...self = {} self.anno = {} item = {} item.anno = {} signalMode = {}".format(self, 
            self.getAnnotations() if hasattr(self, 'getAnnotations') else None, item, item.getAnnotations() if hasattr(item, 'getAnnotations') else None, signalModel))
    
        itempos = self.determineChildKeyValueModelItemInsertPos(item.data(role=Qt.DisplayRole, column=0) if item else None)
        self.insertChild(itempos, item, signalModel)
       


    # Methods for MutableMapping
    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict.keys())

    def __getitem__(self, key):
        return self._dict.get(key, None)

    def _emitDataChanged(self, key=None):
        if self.model() is not None:
            if key is not None and key in self._items:
                index_tl = self._items[key].index()
                index_br = self._items[key].index(1)
            else:
                index_tl = self.index()
                index_br = self.index(1)
            # LOG.info(u"KeyValueModelItem {} emit dataChanged ...".format(self.getAnnotations()))
            self.model().dataChanged.emit(index_tl, index_br)

    def __setitem__(self, key, value, signalModel=True):
        if key not in self._dict:
            self._dict[key] = value
            if key not in self._hidden:
                self._items[key] = KeyValueRowModelItem(key)
                self.addChildSorted(self._items[key], signalModel=signalModel)
            if signalModel:
                self._emitDataChanged(key)
        elif self._dict[key] != value:
            self._dict[key] = value
            # TODO: Emit for hidden key/values?
            if signalModel:
                self._emitDataChanged(key)

    def __delitem__(self, key):
        if key in self._dict:
            del self._dict[key]
            if key in self._items:
                self.deleteChild(self._items[key])

    # # zx added
    # def updateX(self, kvs, needEmitDatachanged = True):
    #     self._dict = {}
    #     for key, value in kvs.iteritems():
    #         self.__setitem__(key, value, False)
    #     if needEmitDatachanged:
    #         print "[ZXD] KeyValueModelItem {} update() call  _emitDataChanged...".format(self.getAnnotations())
    #         self._emitDataChanged()
                
    def update(self, kvs, needEmitDatachanged = True):
        for key, value in kvs.iteritems():
            self.__setitem__(key, value, False)
        if needEmitDatachanged:
            # LOG.info(u"KeyValueModelItem {} update() call  _emitDataChanged...".format(self.getAnnotations()))
            self._emitDataChanged()

    def has_key(self, key):
        return key in self._dict

    def clear(self):
        if len(self._dict) > 0:
            MutableMapping.clear(self)

    # zx999
    # def getAnnotations(self):
    #     res = copy.deepcopy(self._dict)
    #     if None in res: del res[None]
    #     return res

    # def getAnnotations(self, recursive = True):
    #     resdict = copy.deepcopy(self._dict)
    #     if None in resdict: del resdict[None]
    #     # LOG.debug( "== cur anno == {} == recursive {} ==".format(resdict, recursive))
    #     
    #     if recursive:
    #         for child in self.children():
    #             if hasattr(child, 'getAnnotations'):
    #                 tmpresdict = child.getAnnotations(recursive)   
    #                 if None in tmpresdict: del tmpresdict[None]
    #                 # LOG.debug( "== child anno == {}".format(tmpresdict))
    #                 if tmpresdict:
    #                     t = resdict.get(config.CHILD_ITEM_CLASS_TOKEN, None)
    #                     # LOG.debug( "cur's subclass anno: {}".format(t))
    #                     if t is None:
    #                         resdict[config.CHILD_ITEM_CLASS_TOKEN] = [tmpresdict]
    #                     else:
    #                         # Note that, 'subclass' value fields are a list of dicts
    #                         match = False
    #                         
    #                         if ENABLE_MERGE_SAME_TYPE_ITEM_IN_SUBCLASS:
    #                             # merge dicts. 
    #                             for k in resdict[config.CHILD_ITEM_CLASS_TOKEN]:
    #                                 if k[config.METADATA_LABELCLASS_TOKEN] == tmpresdict[config.METADATA_LABELCLASS_TOKEN]:
    #                                         # they have same labels. merge them
    #                                         k.update(tmpresdict)
    #                                         match = True
    #                                        
    #                         
    #                         if not match:
    #                             resdict[config.CHILD_ITEM_CLASS_TOKEN].append(tmpresdict)
    #                                 
    #                     # LOG.debug( "After apending this child: cur's subclass anno: {}".format(resdict[config.CHILD_ITEM_CLASS_TOKEN]))
    #         
    #     # LOG.debug( "== cur anno result == {}".format(resdict))
    #     return resdict

    
    def updateAnnotation(self, annoKey, annoValue):
        if annoKey and self._dict:
            self._dict[annoKey] = annoValue
        return
    
    def getAnnotations(self, recursive = True):
        thisdict = copy.deepcopy(self._dict)
        if None in thisdict: del thisdict[None]
        # LOG.debug( "== cur anno == {} == recursive {} ==".format(thisdict, recursive))
        
        
        if recursive:
            # Note that, 'subclass' field are a list of dicts
            subdictslist = thisdict.get(config.CHILD_ITEM_CLASS_TOKEN, None)
            # LOG.debug( "cur's subclass anno: {}".format(subdictslist))

            for child in self.children():
                if hasattr(child, 'getAnnotations'):
                    subdict = child.getAnnotations(recursive)   
                    if None in subdict: del subdict[None]
                    # LOG.debug( "== child anno == {}".format(subdict))
                    
                    if subdict:
                           
                        if subdictslist is None:
                            thisdict[config.CHILD_ITEM_CLASS_TOKEN] = []
                            subdictslist = thisdict[config.CHILD_ITEM_CLASS_TOKEN]
                
                        subdictslist.append(subdict)
                        # LOG.debug( "After apending this child: cur's subclass anno: {}".format(thisdict[config.CHILD_ITEM_CLASS_TOKEN]))
            
        # LOG.debug( "== cur anno result == {}".format(thisdict))
        return thisdict        
   
        
    # zx add @ 2016-10-12
    def getAnnotationsNum(self):
        return len(self._dict)

    # zx add @ 2016-11-17
    # if labelvalue is None    : just get number of items which has key of "labelclassname"
    # if labelvalue is not None: get number of items which has key of "labelclassname" and value of "labelvalue"
    def getSpecificLabelsNum(self, labelclassname, labelvalue):
        # LOG.info(u"KeyValueModelItem.getSpecificLabelsNum({}, {}) .. self._dict {} get({}) {}".format(
        #     labelclassname, labelvalue, self._dict, labelclassname, self._dict.get(labelclassname)))
        if labelvalue is not None:
            if self._dict.get(labelclassname, None) == labelvalue:
                return 1
            else:
                return 0
        else:
            if labelclassname in self._dict.keys():
                return 1
            else:
                return 0
            


    def isUnlabeled(self):
        return 'unlabeled' in self._dict and self._dict['unlabeled']

    def setUnlabeled(self, val):
        if val:
            self._dict['unlabeled'] = val
        else:
            if 'unlabeled' in self._dict:
                del self['unlabeled']
                self._emitDataChanged('unlabeled')

    def flipUnlabeled(self):
        if 'unlabeled' in self._dict:
            val = self._dict['unlabeled'] 
            val = not val
        else:
            val = True
        self.setUnlabeled(val)
                
    def setDeleted(self, val):
        if val:
            self._dict['deleted'] = val
        else:
            self._emitDataChanged('deleted')

    def isUnconfirmed(self):
        return 'unconfirmed' in self._dict and self._dict['unconfirmed']

    def setUnconfirmed(self, val):
        if val:
            self._dict['unconfirmed'] = val
        else:
            if 'unconfirmed' in self._dict:
                del self['unconfirmed']
                self._emitDataChanged('unconfirmed')

        
class FileModelItem(KeyValueModelItem):

    def __init__(self, filedir, fileinfo, id, hidden=None):
        if not hidden: hidden = [config.ANNOTATION_FILENAME_TOKEN]
        KeyValueModelItem.__init__(self, filedir, hidden=hidden, properties=fileinfo)
        self.id = id

    def data(self, role=Qt.DisplayRole, column=0):
        if role == Qt.DisplayRole:
            if column == 0:
                return "("+str(self.id)+") "+os.path.basename(self[config.ANNOTATION_FILENAME_TOKEN])
            elif column == 1 and self.isUnlabeled():
                return '[unlabeled]'
        return ModelItem.data(self, role, column)

    def getColor(self, outputAlpha = False):
        if self.isUnlabeled():
            return Qt.red
        return None

    @staticmethod
    def create(filedir, fileinfo, imgIdx):
        LOG.info(u"FileModelItem.init({}, {}, {}) with instance {} ...".format(filedir, fileinfo, imgIdx, fileinfo[config.METADATA_LABELCLASS_TOKEN]))
        if fileinfo[config.METADATA_LABELCLASS_TOKEN] == config.ANNOTATION_IMAGE_TOKEN:
           return ImageFileModelItem(filedir, fileinfo, imgIdx)
        elif fileinfo[config.METADATA_LABELCLASS_TOKEN] == config.ANNOTATION_VIDEO_TOKEN:
            return VideoFileModelItem(filedir, fileinfo, imgIdx)


class ImageModelItem(ModelItem):
    def __init__(self, annotations):
        ModelItem.__init__(self)
        items_to_add = [AnnotationModelItem(ann) for ann in annotations]
        self.appendChildren(items_to_add, False)

    def addAnnotation(self, parent_modelItem, ann, signalModel=True):
        LOG.info("ImageModelItem.addAnnotation(parent_modelItem = {}, parentanno = {}, ann = {}, signalModel = {}) call addChildSorted...".format(
            parent_modelItem, parent_modelItem.getAnnotations()  if hasattr(parent_modelItem, 'getAnnotations') else None, ann, signalModel))
        if parent_modelItem is None:
            LOG.info("ImageModelItem.addAnnotation() call ImageModelItem.addChildSorted...")
            self.addChildSorted(AnnotationModelItem(ann), signalModel=signalModel)
        else:
            LOG.info("ImageModelItem.addAnnotation() call parent_modelItem.addChildSorted...")
            parent_modelItem.addChildSorted(AnnotationModelItem(ann), signalModel=signalModel)
        LOG.info("ImageModelItem.addAnnotation... after add: parentanno = {}".format(GET_ANNOTATION(parent_modelItem)))

    def annotations(self):
        for child in self._children:
            if isinstance(child, AnnotationModelItem):
                yield child

    def confirmAll(self):
        for ann in self.annotations():
            ann.setUnconfirmed(False)


class ImageFileModelItem(FileModelItem, ImageModelItem):

    def __init__(self, filedir, fileinfo, imgIdx):
        self._annotation_data = fileinfo.get("annotations", [])
 
        if "annotations" in fileinfo:
            del fileinfo["annotations"]

        LOG.info(u"FileModelItem.INIT({}, {}) ..".format(fileinfo, imgIdx))
        FileModelItem.__init__(self, filedir, fileinfo, imgIdx)
        
        
        LOG.info(u"ImageFileModelItem.INIT({}, {}) ..".format(fileinfo, imgIdx))
        ImageModelItem.__init__(self, [])
        self._toload = []
        for ann in self._annotation_data:
            self._children.append(ann)
            self._toload.append(ann)
        self._loaded = False

    def _load(self, index):
        self._toload.remove(self._children[index])
        ann = AnnotationModelItem(self._children[index])
        self.replaceChild(index, ann)
        if len(self._toload) == 0:
            self._loaded = True

    def data(self, role=Qt.DisplayRole, column=0):
        if role == DataRole:
            return self._dict
        return FileModelItem.data(self, role, column)

    def updateAnnotation(self, annoKey, annoValue):
        if annoKey and KeyValueModelItem._dict:
            KeyValueModelItem._dict[annoKey] = annoValue
        return

    def getAnnotations(self, dummy = None):
        self._ensureAllLoaded()
        LOG.info("ImageFileModelItem.getAnntations .... start")
        # zx999
        fi = KeyValueModelItem.getAnnotations(self, False)
        LOG.info("ImageFileModelItem.getAnntations ....1... fi = {}".format(fi))

        fi['annotations'] = [child.getAnnotations(True) for child in self.children()
                             if hasattr(child, 'getAnnotations')]
        LOG.info("ImageFileModelItem.getAnntations ....2... fi = {}".format(fi))
        return fi

    # zx add @ 2016-10-12
    def getAnnotationsNum(self):
        cnt = 0
        for child in self.children():
            if hasattr(child, 'getAnnotationsNum'):
                cnt += child.getAnnotationsNum()
        return cnt

    def get_label_class(self):
        return self[config.METADATA_LABELCLASS_TOKEN]

    # zx add @ 2016-10-12
    def getSpecificLabelsNum(self, labelclassname, labelvalue):
        cnt = 0
        for child in self.children():
            # print "child {}".format(child)
            if hasattr(child, 'getSpecificLabelsNum'):
                t = child.getSpecificLabelsNum(labelclassname, labelvalue)
                cnt += t
        # print "2: {}".format(cnt)
        return cnt


class VideoFileModelItem(FileModelItem):
    def __init__(self, filedir, fileinfo, frmNum):
        frameinfos = fileinfo.get("frames", [])
        if "frames" in fileinfo:
            del fileinfo["frames"]
        FileModelItem.__init__(self, filedir, fileinfo, frmNum)

        items_to_add = [FrameModelItem(frameinfo) for frameinfo in frameinfos]
        self.appendChildren(items_to_add, False)

    def updateAnnotation(self, annoKey, annoValue):
        if annoKey and KeyValueModelItem._dict:
            KeyValueModelItem._dict[annoKey] = annoValue
        return
        
    def getAnnotations(self, dummy = None):
        self._ensureAllLoaded()
        # zx999
        fi = KeyValueModelItem.getAnnotations(self, False)
        fi['frames'] = [child.getAnnotations(True) for child in self.children()]
        return fi

    # zx add @ 2016-10-12
    def getAnnotationsNum(self):
        cnt = 0
        return 0

        for child in self.children():
            if hasattr(child, 'getAnnotationsNum'):
                cnt += child.getAnnotationsNum()
        return cnt

    def get_label_class(self):
        return self[config.METADATA_LABELCLASS_TOKEN]


    # zx add @ 2016-10-12
    def getSpecificLabelsNum(self, labelclassname, labelvalue):
        cnt = 0
        for child in self.children():
            if hasattr(child, 'getSpecificLabelsNum'):
                cnt += child.getSpecificLabelsNum(labelclassname, labelvalue)
        # print "3: {}".format(cnt)
        return cnt



class FrameModelItem(ImageModelItem, KeyValueModelItem):
    def __init__(self, frameinfo):
        annotations = frameinfo.get("annotations", [])
        if "annotations" in frameinfo:
            del frameinfo["annotations"]
        KeyValueModelItem.__init__(self, properties=frameinfo)
        ImageModelItem.__init__(self, annotations)

    def frameidx(self):
        return int(self.get(config.ANNOTATION_VIDEO_FILE_FRAME_IDX_TOKEN, -1))

    def timestamp(self):
        return float(self.get(config.ANNOTATION_VIDEO_FILE_FRAME_TIMESTAMP_TOKEN, -1))

    def data(self, role=Qt.DisplayRole, column=0):
        if role == Qt.DisplayRole:
            if column == 0:
                # zx modify @ 20161119
                # return "%d / %.3f" % (self.frameidx(), self.timestamp())
                return  "Frame %d" % (self.frameidx())
            elif column == 1 and self.isUnlabeled():
                return '[unlabeled]'
        return ImageModelItem.data(self, role, column)

    def getColor(self, outputAlpha = False):
        if self.isUnlabeled():
            return Qt.red
        return None

    def updateAnnotation(self, annoKey, annoValue):
        if annoKey and KeyValueModelItem._dict:
            KeyValueModelItem._dict[annoKey] = annoValue
        return

    def getAnnotations(self, dummy = None):
        fi = KeyValueModelItem.getAnnotations(self, False)
        fi['annotations'] = [child.getAnnotations(True) for child in self.children()
                             if hasattr(child, 'getAnnotations')]
        return fi

    # zx add @ 2016-10-12
    def getAnnotationsNum(self):
        cnt = 0
        return 0

        for child in self.children():
            if hasattr(child, 'getAnnotationsNum'):
                cnt += child.getAnnotationsNum()
        return cnt

    def get_label_class(self):
        return self[config.METADATA_LABELCLASS_TOKEN]


    # zx add @ 2016-10-12
    def getSpecificLabelsNum(self, labelclassname, labelvalue):
        cnt = 0
        # raw_input("enter here 4")
        for child in self.children():
            if hasattr(child, 'getSpecificLabelsNum'):
                cnt += child.getSpecificLabelsNum(labelclassname, labelvalue)
        # print "4: {}".format(cnt)
        return cnt

        
class AnnotationModelItem(KeyValueModelItem):
    def __init__(self, annotation):
        KeyValueModelItem.__init__(self, None, properties=annotation)
    
    def spawnThisLevelModelItem(self, hidden=None, properties=None, rowModelItemsList = []):
        LOG.info("call AnnotationModelItem.spawnThisLevelModelItem(anno = {})...".format(properties))
        t = AnnotationModelItem(properties)
        LOG.info("call AnnotationModelItem.spawnThisLevelModelItem(anno = {})... ok! AnnotationModelItem = {}".format(properties, t))
        return t
       
    # zx999
    def hasChildOfAnnoModelItem(self):
        for i in xrange(len(self.rowCount())): 
            if isinstance(self.childAt(i), AnnotationModelItem):
                return True
                
    # zx999
    def getChildsOfAnnoModelItem(self):
        childlist = []
        for i in xrange(self.rowCount()):
            child = self.childAt(i)
            if isinstance(child, AnnotationModelItem):
                childlist.append(child)
        return childlist
     


    # Delegated from QAbstractItemModel
    def data(self, role=Qt.DisplayRole, column=0):
        if role == Qt.DisplayRole:
            if column == 0:
                try:
                    return self[config.METADATA_LABELCLASS_TOKEN]
                except KeyError:
                    LOG.error('Could not find key class in annotation item. Please check your label file.')
                    return '<error - no class set>'
            elif column == 1 and self.isUnconfirmed():
                return '[unconfirmed]'
            else:
                return ""
        elif role == DataRole:
            return self._annotation
        return ModelItem.data(self, role, column)

    def getLabelText(self):
        return config.getLabelText(self[config.METADATA_LABELCLASS_TOKEN])

    def getColor(self, outputAlpha = False):
        from sloth.gui.utils import colorTagToQtColor
        from sloth.conf import config
        if self.isUnconfirmed():
            return QColor(Qt.red)
        _cls_color = config._class_color.get(self[config.METADATA_LABELCLASS_TOKEN], None)
        try:
            qcolor = colorTagToQtColor(_cls_color, outputAlpha)
        except Exception as e:
            qcolor = QColor(Qt.yellow)
            
        return qcolor

    def getNameNText(self):
        name = self.get_label_name()
        text = None
        if name:
            text = config.getLabelText(name)
        return name, text
        
    def get_label_class(self):
        return self.get(config.METADATA_LABELCLASS_TOKEN, None)
    
    def get_label_name(self):
        return self.get(config.METADATA_LABELCLASS_TOKEN, None)
    
    def get_label_displaytext(self):
        return self.get('displaytext', None)  

    def parseUpperColorAttrs(self):
        rgb0Value = None
        rgb1Value = None
        rgb2Value = None
        thisItemLabelClass = self.get_label_class()
        if thisItemLabelClass == config.ANNOTATION_UPPER_BODY_TOKEN:
            rgb0Value = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '0', None)
            rgb1Value = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '1', None) if rgb0Value is not None else None
            rgb2Value = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '2', None) if rgb1Value is not None else None
            rgb0Tag   = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '0Tag', None)
            rgb1Tag   = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '1Tag', None) if rgb0Tag is not None else None
            rgb2Tag   = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '2Tag', None) if rgb1Tag is not None else None
            return [rgb0Value, rgb1Value, rgb2Value], [rgb0Tag, rgb1Tag, rgb2Tag], thisItemLabelClass
        else:
            return [None, None, None], [None, None, None], thisItemLabelClass


            
    def parseLowerColorAttrs(self):
        rgb0Value = None
        rgb1Value = None
        rgb2Value = None
        thisItemLabelClass = self.get_label_class()
        if thisItemLabelClass == config.ANNOTATION_LOWER_BODY_TOKEN:
            rgb0Value = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '0', None)
            rgb1Value = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '1', None) if rgb0Value is not None else None
            rgb2Value = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '2', None) if rgb1Value is not None else None
            rgb0Tag   = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '0Tag', None)
            rgb1Tag   = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '1Tag', None) if rgb0Tag is not None else None
            rgb2Tag   = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '2Tag', None) if rgb1Tag is not None else None
            return [rgb0Value, rgb1Value, rgb2Value], [rgb0Tag, rgb1Tag, rgb2Tag], thisItemLabelClass
        else:
            return [None, None, None], [None, None, None], thisItemLabelClass
 
    def parseHelmetColorAttrs(self):
        rgb0Value = None
        rgb1Value = None
        rgb2Value = None
        thisItemLabelClass = self.get_label_class()
        if thisItemLabelClass == config.ANNOTATION_HELMET_WIDGET_TOKEN:
            rgb0Value = self.get(config.ANNOTATION_HELMET_COLOR_TOKEN, None)
            rgb0Tag   = self.get(config.ANNOTATION_HELMET_COLOR_TOKEN + 'Tag', None)
            return [rgb0Value], [rgb0Tag], thisItemLabelClass
        else:
            return [None], [None], thisItemLabelClass
             
    def parseColorAttrs(self, useMyLabelName = False):
        thisItemLabelClass = self.get_label_class()
        rgbTagListOfList = []
        rgbValueListOfList = []
        attrNameList = []
        
        if config.OBJ_TO_CHILDOBJ_AND_ATTR_DICT.get(config.ANNOTATION_UPPER_BODY_TOKEN, None) == None:
            # ------------------------------------------
            # Below branch is the case that for annotation format which has color attributes under upperbody/lowerbody objects ,
            # and we want to tell pedestrain/personbike these color attriutes and let pedestrain/personbike own these color attributes
            # ------------------------------------------
            if (thisItemLabelClass == config.ANNOTATION_PEDESTRAIN_TOKEN) or (thisItemLabelClass == config.ANNOTATION_PERSONBIKE_TOKEN) :
                foundModelItemsAndIterativeLevelsNum = findModelItemsWithSpecificClassName(config.ANNOTATION_UPPER_BODY_TOKEN, self)
                if foundModelItemsAndIterativeLevelsNum:
                    rgbValueList, rgbTagList, attrName = foundModelItemsAndIterativeLevelsNum[0][0].parseUpperColorAttrs()
                    rgbValueListOfList.append(rgbValueList)
                    rgbTagListOfList.append(rgbTagList)
                    # if useParentLabelName:
                    attrNameList.append(config.ANNOTATION_UPPER_COLOR_TOKEN)
                    
                                             
            if (thisItemLabelClass == config.ANNOTATION_PEDESTRAIN_TOKEN) :
                foundModelItemsAndIterativeLevelsNum = findModelItemsWithSpecificClassName(config.ANNOTATION_LOWER_BODY_TOKEN, self)
                if foundModelItemsAndIterativeLevelsNum:
                    rgbValueList, rgbTagList, attrName = foundModelItemsAndIterativeLevelsNum[0][0].parseLowerColorAttrs()
                    rgbValueListOfList.append(rgbValueList)
                    rgbTagListOfList.append(rgbTagList)
                    attrNameList.append(config.ANNOTATION_LOWER_COLOR_TOKEN)

        else:   
        
            if (thisItemLabelClass == config.ANNOTATION_UPPER_BODY_TOKEN) :
                rgbValueList, rgbTagList, attrName = self.parseUpperColorAttrs()
                rgbValueListOfList.append(rgbValueList)
                rgbTagListOfList.append(rgbTagList)
                attrNameList.append(config.ANNOTATION_UPPER_COLOR_TOKEN)
                    
            if (thisItemLabelClass == config.ANNOTATION_LOWER_BODY_TOKEN) :
                rgbValueList, rgbTagList, attrName = self.parseLowerColorAttrs()
                rgbValueListOfList.append(rgbValueList)
                rgbTagListOfList.append(rgbTagList)
                attrNameList.append(config.ANNOTATION_LOWER_COLOR_TOKEN)
                    
                    
        if config.OBJ_TO_CHILDOBJ_AND_ATTR_DICT.get(config.ANNOTATION_HELMET_WIDGET_TOKEN, None) == None:
            # ------------------------------------------
            # Below branch is the case that for annotation format which has helmetcolor attributes under helmet objects ,
            # and we want to tell pedestrain/personbike these color attriutes and let pedestrain/personbike own these color attributes
            # ------------------------------------------
            if (thisItemLabelClass == config.ANNOTATION_PERSONBIKE_TOKEN) :
                foundModelItemsAndIterativeLevelsNum = findModelItemsWithSpecificClassName(config.ANNOTATION_HELMET_WIDGET_TOKEN, self)
                if foundModelItemsAndIterativeLevelsNum:
                    rgbValueList, rgbTagList, attrName = foundModelItemsAndIterativeLevelsNum[0][0].parseHelmetColorAttrs()
                    # print "================= rgbValueList = {} rgbTagList = {} attrName = {} =========".format( rgbValueList, rgbTagList, attrName )
                    rgbValueListOfList.append(rgbValueList)
                    rgbTagListOfList.append(rgbTagList)
                    attrNameList.append(config.ANNOTATION_HELMET_COLOR_TOKEN)

        else:

            if (thisItemLabelClass == config.ANNOTATION_HELMET_WIDGET_TOKEN) :
                rgbValueList, rgbTagList, attrName = self.parseHelmetColorAttrs()
                rgbValueListOfList.append(rgbValueList)
                rgbTagListOfList.append(rgbTagList)
                attrNameList.append(config.ANNOTATION_HELMET_COLOR_TOKEN)
                                             
                  

        if (thisItemLabelClass == config.ANNOTATION_VEHICLE_TOKEN) : 
            rgb0Value = self.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '0', None)
            rgb1Value = self.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '1', None) if rgb0Value is not None else None
            rgb2Value = self.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '2', None) if rgb1Value is not None else None
            rgb0Tag   = self.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '0Tag', None)
            rgb1Tag   = self.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '1Tag', None) if rgb0Tag is not None else None
            rgb2Tag   = self.get(config.ANNOTATION_VEHICLE_COLOR_TOKEN + '2Tag', None) if rgb1Tag is not None else None
            rgbValueListOfList = [[rgb0Value, rgb1Value, rgb2Value]]
            rgbTagListOfList = [[rgb0Tag, rgb1Tag, rgb2Tag]]
            attrNameList.append(config.ANNOTATION_VEHICLE_COLOR_TOKEN)


        # ------------------------------------------
        # Below branch is for annotation format which has color attributes under pedestrain/personbike objects, not under upperbody/lowerbody objects
        # ------------------------------------------
        if not rgbTagListOfList:
            if (thisItemLabelClass == config.ANNOTATION_PEDESTRAIN_TOKEN) or (thisItemLabelClass == config.ANNOTATION_PERSONBIKE_TOKEN) :
                rgb0Value = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '0', None)
                rgb1Value = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '1', None) if rgb0Value is not None else None
                rgb2Value = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '2', None) if rgb1Value is not None else None
                rgb0Tag   = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '0Tag', None)
                rgb1Tag   = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '1Tag', None) if rgb0Tag is not None else None
                rgb2Tag   = self.get(config.ANNOTATION_UPPER_COLOR_TOKEN + '2Tag', None) if rgb1Tag is not None else None
                attrNameList = [config.ANNOTATION_UPPER_COLOR_TOKEN]
                rgbValueListOfList = [[rgb0Value, rgb1Value, rgb2Value]]
                rgbTagListOfList = [[rgb0Tag, rgb1Tag, rgb2Tag]]

            if (thisItemLabelClass == config.ANNOTATION_PEDESTRAIN_TOKEN) :
                rgb0Value = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '0', None)
                rgb1Value = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '1', None) if rgb0Value is not None else None
                rgb2Value = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '2', None) if rgb1Value is not None else None
                rgb0Tag   = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '0Tag', None)
                rgb1Tag   = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '1Tag', None) if rgb0Tag is not None else None
                rgb2Tag   = self.get(config.ANNOTATION_LOWER_COLOR_TOKEN + '2Tag', None) if rgb1Tag is not None else None
                attrNameList.append(config.ANNOTATION_LOWER_COLOR_TOKEN)
                rgbValueListOfList.append([rgb0Value, rgb1Value, rgb2Value])
                rgbTagListOfList.append([rgb0Tag, rgb1Tag, rgb2Tag])

            if (thisItemLabelClass == config.ANNOTATION_HELMET_WIDGET_TOKEN) :
                rgb0Value = self.get(config.ANNOTATION_HELMET_COLOR_TOKEN, None)
                rgb0Tag   = self.get(config.ANNOTATION_HELMET_COLOR_TOKEN + '0Tag', None)
                attrNameList.append(config.ANNOTATION_HELMET_COLOR_TOKEN)
                rgbValueListOfList.append([rgb0Value])
                rgbTagListOfList.append([rgb0Tag])

        return rgbValueListOfList, rgbTagListOfList, attrNameList
        
        
class KeyValueRowModelItem(ModelItem):
    def __init__(self, key, read_only=True):
        ModelItem.__init__(self)
        self._key = key
        self._read_only = read_only

    def key(self):
        return self._key

    def data(self, role=Qt.DisplayRole, column=0):
        if role == Qt.DisplayRole:
            if column == 0:
                return self._key
            elif column == 1:
                return self.parent()[self._key]
            else:
                return None
        else:
            return ModelItem.data(self, role, column)

    def flags(self, column):
        if self._read_only:
            return Qt.NoItemFlags
        else:
            if column == 1:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable
            else:
                return Qt.ItemIsEnabled

    def setData(self, value, role=Qt.DisplayRole, column=0):
        if column == 1:
            if isinstance(value, QVariant):
                value = value.toPyObject()
            self._parent[self._key] = value
            return True
        return False

        
class AnnotationModel(QAbstractItemModel):
    # signals
    dirtyChanged = pyqtSignal(bool, name='dirtyChanged')

    def __init__(self, filedir, annotations, parent=None):
        QAbstractItemModel.__init__(self, parent)
        start = time.time()
        self._annotations = annotations
        LOG.info(u"AnnotationModel init .. annotations {} self {}".format(self._annotations, self))
        self._dirty = False
        self._root = RootModelItem(self, filedir, annotations)
        diff = time.time() - start
        LOG.info("Created AnnotationModel in %.2fs" % (diff, ))

        self.dataChanged.connect(self.onDataChanged)
        self.rowsInserted.connect(self.onDataChanged)
        self.rowsRemoved.connect(self.onDataChanged)

    def isEmpty(self):
        return False if self._annotation else True
        
    # QAbstractItemModel overloads
    def hasChildren(self, index=QModelIndex()):
        if index.column() > 0:
            return 0
        if not index.isValid():
            return self._root.hasChildren()

        parent = self.parentFromIndex(index)
        return parent.childHasChildren(index.row())

    def columnCount(self, index=QModelIndex()):
        return 2

    def rowCount(self, index=QModelIndex()):
        # Only items with column==1 can have children
        if index.column() > 0:
            return 0
        if not index.isValid():
            return self._root.rowCount()

        parent = self.parentFromIndex(index)
        return parent.childRowCount(index.row())

    def parent(self, index):
        if index is None:
            return QModelIndex()
        return self.parentFromIndex(index).index()

    def index(self, row, column, parent_idx=QModelIndex()):
        # Handle invalid rows/columns
        if row < 0 or column < 0:
            return QModelIndex()

        # Only items with column == 0 can have children
        if parent_idx.isValid() and parent_idx.column() > 0:
            return QModelIndex()

        # Get parent. This returns the root if parent_idx is invalid.
        parent = self.itemFromIndex(parent_idx)
        if row < 0 or row >= parent.rowCount():
            return QModelIndex()
        if column < 0 or column >= self.columnCount():
            return QModelIndex()
        return self.createIndex(row, column, parent)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        parent = self.parentFromIndex(index)

        return parent.childData(role, index.row(), index.column())

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        item = self.itemFromIndex(index)

        return item.setData(value, role, index.column())

    def flags(self, index):
        if not index.isValid():
            return self._root.flags(index.column())
        parent = self.parentFromIndex(index)
        return parent.childFlags(index.row(), index.column())

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return config.GUI_ANNOTATION_MODEL_HEAD_COL0_DISPLAYTEXT
            elif section == 1:
                return config.GUI_ANNOTATION_MODEL_HEAD_COL1_DISPLAYTEXT
        return None

    # Own methods
    def root(self):
        return self._root

    def dirty(self):
        return self._dirty

    def setDirty(self, dirty=True):
        if dirty != self._dirty:
            LOG.info(u"Setting model state to dirty = {}".format(dirty))
            self._dirty = dirty
            self.dirtyChanged.emit(self._dirty)

    def onDataChanged(self, *args):
        self.setDirty()

    def itemFromIndex(self, index):
        index = QModelIndex(index)  # explicitly convert from QPersistentModelIndex
        if index.isValid():
            return index.internalPointer().childAt(index.row())
        return self._root

    def parentFromIndex(self, index):
        index = QModelIndex(index)  # explicitly convert from QPersistentModelIndex
        if index.isValid():
            return index.internalPointer()
        return self._root

    def iterator(self, _class=None, predicate=None, start=None, maxlevels=10000):
        # Visit all nodes
        level = 0
        item = start if start is not None else self.root()
        # LOG.info(u"ITEM = {} _class = {}".format(item, _class))
        while item is not None:
            # Return item
            # LOG.info(u"isinstance(item, {}) = {}".format(_class, isinstance(item, _class) if _class is not None else False))
            if _class is None or isinstance(item, _class):

                if predicate is None or predicate(item):
                    yield item

            # Get next item
            if item.rowCount() > 0 and level < maxlevels:
                level += 1
                item = item.childAt(0)
                # LOG.info(u"item 1 = {}".format(item))
            else:
                next_sibling = item.getNextSibling()
                if next_sibling is not None:
                    item = next_sibling
                    # LOG.info(u"[ZXD] item 2 = {}".format(item))
                else:
                    level -= 1
                    ancestor = item.parent()
                    item = None
                    # LOG.info(u"item 3 = {} ancestor = {}".format(item, ancestor))
                    while ancestor is not None:
                        ancestor_sibling = ancestor.getNextSibling()
                        # LOG.info(u"[ZXD] ancestor = {}, ancestor_sibling = {}".format(ancestor, ancestor_sibling))
                        if ancestor_sibling is not None:
                            item = ancestor_sibling
                            # LOG.info(u"item 4 = {}".format(item))
                            break
                        level -= 1
                        ancestor = ancestor.parent()


#######################################################################################
# proxy model
#######################################################################################

class AnnotationSortFilterProxyModel(QSortFilterProxyModel):
    """Adds sorting and filtering support to the AnnotationModel without basically
    any implementation effort.  Special functions such as ``insertPoint()`` just
    call the source models respective functions."""
    def __init__(self, parent=None):
        super(AnnotationSortFilterProxyModel, self).__init__(parent)

    def fileIndex(self, index):
        fi = self.sourceModel().fileIndex(self.mapToSource(index))
        return self.mapFromSource(fi)

    def itemFromIndex(self, index):
        return self.sourceModel().itemFromIndex(self.mapToSource(index))

    def baseDir(self):
        return self.sourceModel().baseDir()

    def insertPoint(self, pos, parent, **kwargs):
        return self.sourceModel().insertPoint(pos, self.mapToSource(parent), **kwargs)

    def insertRect(self, rect, parent, **kwargs):
        return self.sourceModel().insertRect(rect, self.mapToSource(parent), **kwargs)

    def insertMask(self, fname, parent, **kwargs):
        return self.sourceModel().insertMask(fname, self.mapToSource(parent), **kwargs)

    def insertFile(self, filename):
        return self.sourceModel().insertFile(filename)


#######################################################################################
# view
#######################################################################################

class AnnotationTreeView(QTreeView):
    selectedItemsChanged = pyqtSignal(object)

    def __init__(self, parent=None):
        super(AnnotationTreeView, self).__init__(parent)

        self.setUniformRowHeights(True)
        self.setSelectionMode(QTreeView.ExtendedSelection)
        self.setSelectionBehavior(QTreeView.SelectRows)
        self.setAllColumnsShowFocus(True)
        self.setAlternatingRowColors(True)
        #self.setEditTriggers(QAbstractItemView.SelectedClicked)
        self.setSortingEnabled(True)
        self.setAnimated(True)
        self.expanded.connect(self.onExpanded)

    def resizeColumns(self):
        for column in range(self.model().columnCount(QModelIndex())):
            self.resizeColumnToContents(column)

    def onExpanded(self):
        self.resizeColumns()

    def setModel(self, model):
        QTreeView.setModel(self, model)
        LOG.info(u"AnnotationTreeView.setModel... model = {} model._root.rowCount() = {}...".format(model, model._root.rowCount()))
        self.resizeColumns()

    def rowsInserted(self, index, start, end):
        LOG.info(u"rowsInserted ... AnnotationTreeView.rowsInserted(index = {}, start = {}, end = {})...".format(index, start, end))
        QTreeView.rowsInserted(self, index, start, end)
        LOG.info(u"rowsInserted ... AnnotationTreeView.rowsInserted(index = {}, start = {}, end = {})... ok".format(index, start, end))
        self.resizeColumns()

    def setSelectedItems(self, items):
        LOG.info(u"AnnotationTreeView.setSelectedItems... items{}...".format(items))
        block = self.blockSignals(True)
        sel = QItemSelection()
        for item in items:
            sel.merge(QItemSelection(item.index(), item.index(1)), QItemSelectionModel.SelectCurrent)
        if set(sel) != set(self.selectionModel().selection()):
            self.selectionModel().clear()
            self.selectionModel().select(sel, QItemSelectionModel.Select)
        self.blockSignals(block)

    def itemClicked(self, clickedItem, column):
        # print "clickedItem = {} column = {}".format(clickedItem, column)
        return
        
    def selectionChanged(self, selected, deselected):
        LOG.info(u"AnnotationTreeView.selectionChanged... selected {} deselected {} ...".format(selected, deselected))
        items = [ self.model().itemFromIndex(index) for index in self.selectionModel().selectedIndexes()]
        self.selectedItemsChanged.emit(items)
        QTreeView.selectionChanged(self, selected, deselected)


def getQRectFFromModelItem(modelitem, prefix = ''):
    if modelitem is None:
        return None
    x = modelitem.get(prefix + 'x', None)
    y = modelitem.get(prefix + 'y', None)
    w = modelitem.get(prefix + 'width',  None)
    h = modelitem.get(prefix + 'height', None)
    if (x is not None) and (y is not None) and (w is not None) and (h is not None):
        return QRectF(x, y, w, h)
    return None



def convertQRectFToModelItemKeyValues(qRectF, prefix = ''):
    modeldesc = {
            prefix + 'x':      float(qRectF.topLeft().x()),
            prefix + 'y':      float(qRectF.topLeft().y()),
            prefix + 'width':  float(qRectF.width()),
            prefix + 'height': float(qRectF.height()),
             }
    return modeldesc


def getQPointFFromModelItem(modelitem, prefix = ''):
    if modelitem is None:
        return None
    x = modelitem.get(prefix + 'x', None)
    y = modelitem.get(prefix + 'y', None)
    if (x is not None) and (y is not None):
        return QPointF(x, y)
    return None
   

def convertQPointFToModelItemKeyValues(qPointF, prefix = ''):
    modeldesc = {
            prefix + 'x':      float(qPointF.x()),
            prefix + 'y':      float(qPointF.y())
             }
    return modeldesc    


def getFace5PointsFromModelItemOrAnnotation(modelitem, prefix = ''):
    if modelitem is None:
        return None
    lecx = modelitem.get(prefix + 'lecx', None)
    lecy = modelitem.get(prefix + 'lecy', None)
    lec = QPointF(lecx, lecy)
    recx = modelitem.get(prefix + 'recx', None)
    recy = modelitem.get(prefix + 'recy', None)
    rec = QPointF(recx, recy)
    lmcx = modelitem.get(prefix + 'lmcx', None)
    lmcy = modelitem.get(prefix + 'lmcy', None)
    lmc = QPointF(lmcx, lmcy)
    rmcx = modelitem.get(prefix + 'rmcx', None)
    rmcy = modelitem.get(prefix + 'rmcy', None)
    rmc = QPointF(rmcx, rmcy)
    ntx = modelitem.get(prefix + 'ntx', None)
    nty = modelitem.get(prefix + 'nty', None)
    nt = QPointF(ntx, nty)
    return lec, rec, lmc, rmc, nt
   

def convertFace5PointsToModelItemKeyValues(lecQPointF, recQPointF, lmcQPointF, rmcQPointF, ntQPointF, prefix = ''):
    modeldesc = {
            prefix + 'lecx':      float(lecQPointF.x()),
            prefix + 'lecy':      float(lecQPointF.y()),
            prefix + 'recx':      float(recQPointF.x()),
            prefix + 'recy':      float(recQPointF.y()),
            prefix + 'lmcx':      float(lmcQPointF.x()),
            prefix + 'lmcy':      float(lmcQPointF.y()),
            prefix + 'rmcx':      float(rmcQPointF.x()),
            prefix + 'rmcy':      float(rmcQPointF.y()),
            prefix + 'ntx':       float(ntQPointF.x()),
            prefix + 'nty':       float(ntQPointF.y())
             }
    return modeldesc    
    
    
def getQLineFFromModelItem(modelitem, prefix = ''):
    if modelitem is None:
        return None
    x0 = modelitem.get(prefix + 'x0', None)
    y0 = modelitem.get(prefix + 'y0', None)
    x1 = modelitem.get(prefix + 'x1', None)
    y1 = modelitem.get(prefix + 'y1', None)
    if (x0 is not None) and (y0 is not None) and (x1 is not None) and (y1 is not None):
        return QLineF(x0, y0, x1, y1)
    return None
   

def convertQLineFToModelItemKeyValues(qLineF, prefix = ''):
    modeldesc = {
            prefix + 'x0':      float(qLineF.x1()),
            prefix + 'y0':      float(qLineF.y1()),
            prefix + 'x1':      float(qLineF.x2()),
            prefix + 'y1':      float(qLineF.y2()),

             }
    return modeldesc              
 


def getQPolygonFFromModelItem(modelitem, prefix = ''):
    if modelitem is None:
        return None
    
    polygon = QPolygonF()
    xn = [float(x) for x in model_item["xn"].split(";")]
    yn = [float(y) for y in model_item["yn"].split(";")]
    for x, y in zip(xn, yn):
        polygon.append(QPointF(x, y))
    return polygon

def convertQPolygonFToModelItemKeyValues(qPolygonF, prefix = ''):
    xn = ';'.join([str(p.x()) for p in qPolygonF])
    yn = ';'.join([str(p.y()) for p in qPolygonF])
    modeldesc = {
            prefix + 'xn':      xn,
            prefix + 'yn':      yn
             }

    return modeldesc

                             
# =======================================================================================
# find parent modelItem for current modelItem(named ItemQRectF) with type of QRectF.
# so-called parent modelItem is such type of:
# (1) that has max overlap size with current ItemQRectF among all candidate modelItems with type of QRectF.
#     and
# (2) that has mimnum rect size among (1)                                              
#     and
# (3) that are latest modelItems among (2)
# =======================================================================================
def findAllowedConnectSourceOfRectModelItem(itemLabelClassName, parentModelItem, exclueParentModelItem = True, iterativeLevelsNum = 1):
    foundModelItemsAndIterativeLevelsNum = []
    if itemLabelClassName in config.AUTO_CONNECT_SOURCE.keys():
        # print "config.AUTO_CONNECT_SOURCE[{}] = {}".format(itemLabelClassName, config.AUTO_CONNECT_SOURCE[itemLabelClassName])
        for i in config.AUTO_CONNECT_SOURCE[itemLabelClassName]:
            if not exclueParentModelItem:
                if ( i == parentModelItem.get_label_class() ):
                    LOG.debug(
                        "@@@@@ 2 -- itemLabelClassName {} -  {} is == parentModelItem {} ..".format(
                            itemLabelClassName, i,
                            parentModelItem.get_label_class()))
                    foundModelItemsAndIterativeLevelsNum += [(parentModelItem, iterativeLevelsNum+1)]
            LOG.debug(
                "@@@@@ 2 -- itemLabelClassName {} - check {} is under parentModelItem {} ..".format(itemLabelClassName, i,
                                                                                                    parentModelItem.get_label_class()))

            _foundModelItemsAndIterativeLevelsNum = findModelItemsWithSpecificClassName(i, parentModelItem, iterativeLevelsNum)
            LOG.debug(
                "@@@@@ 2 -- itemLabelClassName {} - check {} is under parentModelItem {} -- result {}..".format(itemLabelClassName, i,
                                                                                                    parentModelItem.get_label_class(), _foundModelItemsAndIterativeLevelsNum))
            if  _foundModelItemsAndIterativeLevelsNum:
                foundModelItemsAndIterativeLevelsNum += _foundModelItemsAndIterativeLevelsNum
    return foundModelItemsAndIterativeLevelsNum


def findRectModelItemWithMinimumSizeAndMaxOverlapWithRect(ItemQRectF, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = True):

    maxIntersect = -1
    maxIntersectMinCandidateSize = -1
    targetItem = None if enableSelectMinimumSize else []
    if not foundModelItemsAndIterativeLevelsNum:
        return targetItem
    for x in foundModelItemsAndIterativeLevelsNum:
        mi = x[0]
        levelcnt = x[1]
        candidate = getQRectFFromModelItem(mi)
        # print "foundModelItem[][] = {} class = {} rect = {}".format(mi, mi.get_label_class(), candidate)
        if candidate is not None:
            candidateSize = candidate.width() * candidate.height()
            rect = ItemQRectF.intersected(candidate)
            intersect = rect.width() * rect.height()
            if (intersect > 0):
                if enableSelectMinimumSize:
                    if (maxIntersect < intersect):
                        maxIntersect = intersect
                        maxIntersectCandidateSize = candidateSize
                        targetItem = (mi, levelcnt)
                        # print "1: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem)
                    elif maxIntersect == intersect:
                        if (maxIntersectMinCandidateSize > candidateSize) and (candidateSize > 0):
                            maxIntersectMinCandidateSize = candidateSize
                            targetItem = (mi, levelcnt)
                            # print "2: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem)
                        elif maxIntersectMinCandidateSize == candidateSize:
                            targetItem = (mi, levelcnt) if targetItem.row() < mi.row() else targetItem
                            # print "3: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem)
            else:
                pass
                # targetItem += (mi, levelcnt)
                
    return targetItem

def findConnectSourceOfRectModelItemForRectModelItem(ItemQRectF, itemLabelClassName, curImg_imageModelItem):
    # print "ItemQRectF {} itemLabelClassName {} curImg_imageModelItem {} ..".format(ItemQRectF, itemLabelClassName, curImg_imageModelItem)
    
    if (ItemQRectF is None) or (ItemQRectF.width() <= 0) or (ItemQRectF.height() <= 0) or (itemLabelClassName is None) or (curImg_imageModelItem is None):
        return []

    foundModelItemsAndIterativeLevelsNum = findAllowedConnectSourceOfRectModelItem(itemLabelClassName, curImg_imageModelItem)
    # print "foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum)

    targetItem = findRectModelItemWithMinimumSizeAndMaxOverlapWithRect(ItemQRectF, foundModelItemsAndIterativeLevelsNum)
    # print "targetItem = {} class = {}".format(targetItem, targetItem[0].get_label_class() if targetItem else None)
    return targetItem[0] if targetItem else None        


def findRectModelItemWithMinimumSizeAndMaxOverlapWithPolygon(ItemQPolygonF, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = True):

    maxIntersect = -1
    maxIntersectMinCandidateSize = -1
    targetItem = None if enableSelectMinimumSize else []
    if not foundModelItemsAndIterativeLevelsNum:
        return targetItem
    for x in foundModelItemsAndIterativeLevelsNum:
        mi = x[0]
        levelcnt = x[1]
        candidate = getQRectFFromModelItem(mi)
        # print "foundModelItem[][] = {} class = {} rect = {}".format(mi, mi.get_label_class(), candidate)
        if candidate is not None:
            candidateSize = candidate.width() * candidate.height()
            poly = ItemQPolygonF.intersected(QPolygonF(candidate))
            br = poly.boundingRect()
            intersect = (br.width() * br.height()) if br else 0
            if (intersect > 0):
                if enableSelectMinimumSize:
                    if (maxIntersect < intersect):
                        maxIntersect = intersect
                        maxIntersectCandidateSize = candidateSize
                        targetItem = (mi, levelcnt)
                        # print "1: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem)
                    elif maxIntersect == intersect:
                        if (maxIntersectMinCandidateSize > candidateSize) and (candidateSize > 0):
                            maxIntersectMinCandidateSize = candidateSize
                            targetItem = (mi, levelcnt)
                            # print "2: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem)
                        elif maxIntersectMinCandidateSize == candidateSize:
                            targetItem = (mi, levelcnt) if targetItem.row() < mi.row() else targetItem
                            # print "3: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem)
            else:
                pass
                # targetItem += (mi, levelcnt)
                
    return targetItem
                
def findConnectSourceOfRectModelItemForPolygonModelItem(ItemQPolygonF, itemLabelClassName, curImg_imageModelItem):
    # print "ItemQPolygonF {} itemLabelClassName {} curImg_imageModelItem {} ..".format(ItemQPolygonF, itemLabelClassName, curImg_imageModelItem)
    
    if (ItemQPolygonF is None) or (itemLabelClassName is None) or (curImg_imageModelItem is None):
        return []

    foundModelItemsAndIterativeLevelsNum = findAllowedConnectSourceOfRectModelItem(itemLabelClassName, curImg_imageModelItem)
    # print "foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum)

    targetItem = findRectModelItemWithMinimumSizeAndMaxOverlapWithPolygon(ItemQPolygonF, foundModelItemsAndIterativeLevelsNum)
    # print "targetItem = {} class = {}".format(targetItem, targetItem[0].get_label_class() if targetItem else None)
    return targetItem[0] if targetItem else None        

def findClosestRectModelItemWithMinimumSizeAndMaxOverlapWithPolygon(ItemQPolygonF, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = True):
    maxIntersect = -1
    maxIntersectMinCandidateSize = -1
    targetItem = None if enableSelectMinimumSize else []
    if not foundModelItemsAndIterativeLevelsNum:
        return targetItem
    targetLevelCnt = foundModelItemsAndIterativeLevelsNum[0][1] if foundModelItemsAndIterativeLevelsNum else 0
    for x in foundModelItemsAndIterativeLevelsNum:
        mi = x[0]
        levelcnt = x[1]
        # print "enter  hhhhhhhhhhhhhh"
        if levelcnt != targetLevelCnt:
            break
        candidate = getQRectFFromModelItem(mi)
        LOG.debug(
            "findClosestRectModelItemWithMinimumSizeAndMaxOverlapWithPolygon .... [][] = {} class = {} rect = {}".format(
                mi, mi.get_label_class(), candidate))
        LOG.debug( "foundModelItem[][] = {} class = {} rect = {}".format(mi, mi.get_label_class(), candidate))
        if candidate is not None:
            candidateSize = candidate.width() * candidate.height()
            intersectPoly = ItemQPolygonF.intersected(QPolygonF(candidate))
            ir = intersectPoly.boundingRect()
            intersect = ir.width() * ir.height()        # rect.width() * rect.height()
            if (intersect > 0):
                if enableSelectMinimumSize:
                    if (maxIntersect < intersect):
                        maxIntersect = intersect
                        maxIntersectCandidateSize = candidateSize
                        targetItem = (mi, levelcnt) 
                        LOG.debug("1: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem))
                    elif maxIntersect == intersect:
                        if (maxIntersectMinCandidateSize > candidateSize) and (candidateSize > 0):
                            maxIntersectMinCandidateSize = candidateSize
                            targetItem = (mi, levelcnt) 
                            LOG.debug("2: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem))
                        elif maxIntersectMinCandidateSize == candidateSize:
                            targetItem = (mi, levelcnt)  if targetItem.row() < mi.row() else targetItem
                            LOG.debug("3: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem))
                else: 
                    pass
                    # targetItem += (mi, levelcnt)            

    return targetItem
    

def findClosestParentRectModelItemForPolygonModelItem(ItemQPolygonF, itemLabelClassName, grandParentModelItem):
    LOG.debug ("@@@@@ findClosestParentRectModelItemForPolygonModelItem - ItemQPolygonF {} itemLabelClassName {} grandParentModelItem {} ..".format(ItemQPolygonF, itemLabelClassName, grandParentModelItem.get_label_class()))
    
    if (ItemQPolygonF is None) or (itemLabelClassName is None) or (grandParentModelItem is None):
        return []

    foundModelItemsAndIterativeLevelsNum = findAllowedConnectSourceOfRectModelItem(itemLabelClassName, grandParentModelItem, exclueParentModelItem = False, iterativeLevelsNum = 5)
    LOG.debug ("findAllowedConnectSourceOfRectModelItem {} ..".format(foundModelItemsAndIterativeLevelsNum))
    if not foundModelItemsAndIterativeLevelsNum:
        return None
        
    LOG.debug ("findClosestParentRectModelItemForRectModelItem: foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum))
    foundModelItemsAndIterativeLevelsNum = sorted(foundModelItemsAndIterativeLevelsNum, key = lambda d: d[1], reverse = 1)
    LOG.debug ("findClosestParentRectModelItemForRectModelItem: sorted foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum))

    targetItem = findClosestRectModelItemWithMinimumSizeAndMaxOverlapWithPolygon(ItemQPolygonF, foundModelItemsAndIterativeLevelsNum)

    LOG.debug ("findClosestParentRectModelItemForRectModelItem: targetItem = {} class = {}".format(targetItem, targetItem[0].get_label_class() if targetItem else None))
    return targetItem[0] if targetItem else None 
                
# =======================================================================================
# find parent modelItem for current modelItem(named ItemQPointF) with type of QPointF.
# so-called parent modelItem is such type of:
# (1) that has type of QRectF
#     and
# (2) that contains ItemQPointF
#     and
# (3) that has mimnum rect size among (2)                                              
# =======================================================================================
def findRectModelItemWithMinimumSizeWhichContainPoint(ItemQPointF, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = True):
    minCandidateSize = -1
    targetItem = None if enableSelectMinimumSize else []
    if not foundModelItemsAndIterativeLevelsNum:
        return targetItem
    for x in foundModelItemsAndIterativeLevelsNum:
        mi = x[0]
        levelcnt = x[1]
        candidate = getQRectFFromModelItem(mi)
        # print "foundModelItem[][] = {} class = {} rect = {}".format(mi, mi.get_label_class(), candidate)
        if candidate is not None:
            candidateSize = candidate.width() * candidate.height()
            isContained = candidate.contains(ItemQPointF)
            if (isContained):
                if enableSelectMinimumSize:
                    minCandidateSize = candidateSize if candidateSize < minCandidateSize else minCandidateSize
                    targetItem = (mi, levelcnt)
                else:
                    targetItem += (mi, levelcnt)
    
    return targetItem
                
def findConnectSourceOfRectModelItemForPointModelItem(ItemQPointF, itemLabelClassName, curImg_imageModelItem):
    # print "ItemQPointF {} itemLabelClassName {} curImg_imageModelItem {} ..".format(ItemQPointF, itemLabelClassName, curImg_imageModelItem)
    
    if (ItemQPointF is None) or (itemLabelClassName is None) or (curImg_imageModelItem is None):
        return []

    foundModelItemsAndIterativeLevelsNum = findAllowedConnectSourceOfRectModelItem(itemLabelClassName, curImg_imageModelItem)
    # print "foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum)
    

    targetItem = findRectModelItemWithMinimumSizeWhichContainPoint(ItemQPointF, foundModelItemsAndIterativeLevelsNum)
    # print "targetItem = {} class = {}".format(targetItem, targetItem.get_label_class() if targetItem is not None else None)
    return targetItem[0] if targetItem else None
    
# =======================================================================================
# find closest parent modelItem for current modelItem(named ItemQRectF) with type of QRectF.
# =======================================================================================
def findClosestRectModelItemWithMinimumSizeAndMaxOverlapWithRect(ItemQRectF, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = True):
    maxIntersect = -1
    maxIntersectMinCandidateSize = -1
    targetItem = None if enableSelectMinimumSize else []
    if not foundModelItemsAndIterativeLevelsNum:
        return targetItem
    targetLevelCnt = foundModelItemsAndIterativeLevelsNum[0][1] if foundModelItemsAndIterativeLevelsNum else 0
    for x in foundModelItemsAndIterativeLevelsNum:
        mi = x[0]
        levelcnt = x[1]
        # print "enter  hhhhhhhhhhhhhh"
        if levelcnt != targetLevelCnt:
            break
        candidate = getQRectFFromModelItem(mi)
        LOG.debug(
            "findClosestRectModelItemWithMinimumSizeAndMaxOverlapWithRect .... [][] = {} class = {} rect = {}".format(
                mi, mi.get_label_class(), candidate))
        LOG.debug( "foundModelItem[][] = {} class = {} rect = {}".format(mi, mi.get_label_class(), candidate))
        if candidate is not None:
            candidateSize = candidate.width() * candidate.height()
            rect = ItemQRectF.intersected(candidate)
            intersect = rect.width() * rect.height()
            if (intersect > 0):
                if enableSelectMinimumSize:
                    if (maxIntersect < intersect):
                        maxIntersect = intersect
                        maxIntersectCandidateSize = candidateSize
                        targetItem = (mi, levelcnt) 
                        LOG.debug("1: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem))
                    elif maxIntersect == intersect:
                        if (maxIntersectMinCandidateSize > candidateSize) and (candidateSize > 0):
                            maxIntersectMinCandidateSize = candidateSize
                            targetItem = (mi, levelcnt) 
                            LOG.debug("2: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem))
                        elif maxIntersectMinCandidateSize == candidateSize:
                            targetItem = (mi, levelcnt)  if targetItem.row() < mi.row() else targetItem
                            LOG.debug("3: maxIntersect = {} maxIntersectCandidateSize = {} targetItem = {}".format(maxIntersect, maxIntersectCandidateSize, targetItem))
                else: 
                    pass
                    # targetItem += (mi, levelcnt)            

    return targetItem
    

def findClosestParentRectModelItemForRectModelItem(ItemQRectF, itemLabelClassName, grandParentModelItem):
    LOG.debug ("@@@@@ findClosestParentRectModelItemForRectModelItem - ItemQRectF {} itemLabelClassName {} grandParentModelItem {} ..".format(ItemQRectF, itemLabelClassName, grandParentModelItem.get_label_class()))
    
    if (ItemQRectF is None) or (ItemQRectF.width() <= 0) or (ItemQRectF.height() <= 0) or (itemLabelClassName is None) or (grandParentModelItem is None):
        return []

    foundModelItemsAndIterativeLevelsNum = findAllowedConnectSourceOfRectModelItem(itemLabelClassName, grandParentModelItem, exclueParentModelItem = False, iterativeLevelsNum = 5)
    LOG.debug ("findAllowedConnectSourceOfRectModelItem {} ..".format(foundModelItemsAndIterativeLevelsNum))
    if not foundModelItemsAndIterativeLevelsNum:
        return None
        
    LOG.debug ("findClosestParentRectModelItemForRectModelItem: foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum))
    foundModelItemsAndIterativeLevelsNum = sorted(foundModelItemsAndIterativeLevelsNum, key = lambda d: d[1], reverse = 1)
    LOG.debug ("findClosestParentRectModelItemForRectModelItem: sorted foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum))

    targetItem = findClosestRectModelItemWithMinimumSizeAndMaxOverlapWithRect(ItemQRectF, foundModelItemsAndIterativeLevelsNum)

    LOG.debug ("findClosestParentRectModelItemForRectModelItem: targetItem = {} class = {}".format(targetItem, targetItem[0].get_label_class() if targetItem else None))
    return targetItem[0] if targetItem else None            
    
    
# =======================================================================================
# find closest parent modelItem for current modelItem(named ItemQPointF) with type of QPointF.
# =======================================================================================
def findClosestRectModelItemWithMinimumSizeWhichContainPoint(ItemQPointF, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = True):
    minCandidateSize = -1
    targetItem = None if enableSelectMinimumSize else []
    if not foundModelItemsAndIterativeLevelsNum:
        return targetItem
    targetLevelCnt = foundModelItemsAndIterativeLevelsNum[0][1]
    for x in foundModelItemsAndIterativeLevelsNum:
        mi = x[0]
        levelcnt = x[1]
        if levelcnt != targetLevelCnt:
            break
        candidate = getQRectFFromModelItem(mi)
        LOG.debug("foundModelItem[][] = {} class = {} rect = {} point = {}".format(mi, mi.get_label_class(), candidate, ItemQPointF))
        if candidate is not None:
            candidateSize = candidate.width() * candidate.height()
            isContained = candidate.contains(ItemQPointF)
            if (isContained):
                if enableSelectMinimumSize:
                    minCandidateSize = candidateSize if candidateSize > minCandidateSize else minCandidateSize
                    targetItem = (mi, levelcnt)
                else:
                    targetItem.append((mi, levelcnt)) 
    return targetItem    

def findClosestParentRectModelItemForPointModelItem(ItemQPointF, itemLabelClassName, grandParentModelItem):
    LOG.debug("@@@@@ ItemQPointF {} itemLabelClassName {} grandParentModelItem {} ..".format(ItemQPointF, itemLabelClassName, grandParentModelItem))
    
    if (ItemQPointF is None) or (itemLabelClassName is None) or (grandParentModelItem is None):
        return []

    LOG.debug(
        "@@@@@ 1 -- itemLabelClassName {} grandParentModelItem {} ..".format(itemLabelClassName, grandParentModelItem.get_label_class()))

    foundModelItemsAndIterativeLevelsNum = findAllowedConnectSourceOfRectModelItem(itemLabelClassName, grandParentModelItem, exclueParentModelItem = False, iterativeLevelsNum = 5)
    if not foundModelItemsAndIterativeLevelsNum:
        return None
        
    LOG.debug("findClosestParentRectModelItemForPointModelItem: foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum))
    foundModelItemsAndIterativeLevelsNum = sorted(foundModelItemsAndIterativeLevelsNum, key = lambda d: d[1], reverse = 1)
    LOG.debug("findClosestParentRectModelItemForPointModelItem: sorted foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum))

    targetItem = findClosestRectModelItemWithMinimumSizeWhichContainPoint(ItemQPointF, foundModelItemsAndIterativeLevelsNum)
    LOG.debug("findClosestParentRectModelItemForPointModelItem: targetItem = {} class = {}".format(targetItem, targetItem[0].get_label_class() if targetItem else None))
    return targetItem[0] if targetItem else None         
        
# =======================================================================================
# find parent modelItem for current modelItem(named SequenceModelItem) with type of QPointF.
# so-called parent modelItem is such type of:
# (1) that has type of QRectF
#     and
# (2) that contains ItemQPointF
#     and
# (3) that has mimnum rect size among (2)                                              
# =======================================================================================
     
def findConnectSourceOfRectModelItemForSequenceModelItem(sequenceItemsPos, itemsLabelClassName, curImg_imageModelItem):
    # print "sequenceItemsPos {} itemLabelClassName {} curImg_imageModelItem {} ..".format(sequenceItemsPos, itemLabelClassName, curImg_imageModelItem)
    
    if (sequenceItemsPos is None) or (itemsLabelClassName is None) or (curImg_imageModelItem is None):
        return []

    foundModelItemsAndIterativeLevelsNum = findAllowedConnectSourceOfRectModelItem(itemsLabelClassName, curImg_imageModelItem)
    # print "foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum)

    # get all rectModelItem which have overlap with all items in sequenceItemsPos
    # get all rectModelItem which have overlap with all items in sequenceItemsPos
    # must use a dict for hashing instead of a set, because objects are not hashable
    targetItemsSet = {} # set()
    for i in sequenceItemsPos:
        if (i is not None) and isinstance(i, QRectF):
            targetItems = findRectModelItemWithMinimumSizeAndMaxOverlapWithRect(i, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = False)
        elif (i is not None) and isinstance(i, QPointF):
            targetItems = findRectModelItemWithMinimumSizeWhichContainPoint(i, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = False)
        elif (i is not None) and isinstance(i, QPolygonF):
            targetItems = findRectModelItemWithMinimumSizeAndMaxOverlapWithPolygon(i, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = False)
        
        if targetItems is not None:
            # for m in targetItems:
            #    if m is not None:
            #        # targetItemsSet.add(m[0])
            targetItemsSet = dict((id(m), m) for m in targetItems if m is not None)

    # select rectModelItem of minimum size from above rectModelItems
    min = 100000000
    targetItem = None
    for m in targetItemsSet.values():
       size = m.width() * m.height()
       if ( min > size):
           min = size
           targetItem = m
            
    # print "targetItem = {} class = {}".format(targetItem, targetItem.get_label_class() if targetItem is not None else None)
    return targetItem 
 
def findClosestParentRectModelItemForSequenceModelItem(sequenceItemsPos, itemLabelClassName, grandParentModelItem):
    LOG.debug("@@@@@ sequenceItemsPos {} itemLabelClassName {} grandParentModelItem {} ..".format(sequenceItemsPos, itemLabelClassName, grandParentModelItem))
    
    if (sequenceItemsPos is None) or (itemLabelClassName is None) or (grandParentModelItem is None):
        return []

    LOG.debug(
        "@@@@@ 3 -- itemLabelClassName {} grandParentModelItem {} ..".format(itemLabelClassName, grandParentModelItem.get_label_class()))

    foundModelItemsAndIterativeLevelsNum = findAllowedConnectSourceOfRectModelItem(itemLabelClassName, grandParentModelItem, exclueParentModelItem = False, iterativeLevelsNum = 5)
    if not foundModelItemsAndIterativeLevelsNum:
        return None
        
    LOG.debug("findClosestParentRectModelItemForSequenceModelItem: foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum))
    foundModelItemsAndIterativeLevelsNum = sorted(foundModelItemsAndIterativeLevelsNum, key = lambda d: d[1], reverse = 1)
    LOG.debug("findClosestParentRectModelItemForSequenceModelItem: sorted foundModelItemsAndIterativeLevelsNum = {}".format(foundModelItemsAndIterativeLevelsNum))

    # get all rectModelItem which have overlap with all items in sequenceItemsPos
    # must use a dict for hashing instead of a set, because objects are not hashable
    targetItemsSet = {} # set()
    for i in sequenceItemsPos:
        if (i is not None) and isinstance(i, QRectF):
            targetItems = findClosestRectModelItemWithMinimumSizeAndMaxOverlapWithRect(i, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = False)
        elif (i is not None) and isinstance(i, QPointF):
            targetItems = findClosestRectModelItemWithMinimumSizeWhichContainPoint(i, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = False)
        elif (i is not None) and isinstance(i, QPolygonF):
            targetItems = findClosestRectModelItemWithMinimumSizeAndMaxOverlapWithPolygon(i, foundModelItemsAndIterativeLevelsNum, enableSelectMinimumSize = False)
        
        if targetItems is not None:
            # for m in targetItems:
            #    if m is not None:
            #        # targetItemsSet.add(m[0])
            targetItemsSet = dict((id(m), m) for m in targetItems if m is not None )

    LOG.debug("targetItems = {}".format(targetItems))
    # select rectModelItem of minimum size from above targetItemsSet
    min = 100000000
    targetItem = None
    for m in targetItemsSet.values():
        rect = getQRectFFromModelItem(m[0])
        size = rect.width() * rect.height()
        if ( min > size):
            min = size
            targetItem = m[0]
            
    # print "targetItem = {} class = {}".format(targetItem, targetItem.get_label_class() if targetItem is not None else None)
    return targetItem 
     
     
# ================================================================        
# ================================================================        
def findModelItemsWithSpecificClassNameFromRoot(targetClasName, rootModeItem, iterativeLevelsNum = 1):
    foundItems = []
    if (rootModeItem is None):
        return foundItems
    foundItems = findModelItemWithSpecificClass(targetClasName, rootModeItem, 0, rootModeItem.rowCount()-1, iterativeLevelsNum)
    if hasattr(rootModeItem, 'get_label_class') and rootModeItem.get_label_class() == targetClasName:
        rootItem_ = [(rootModeItem, 0)]
        foundItems = rootItem_ + foundItems
    LOG.debug("findModelItemsWithSpecificClassNameFromRoot... targetClasName = {} foundItems = {} {}".format(targetClasName, foundItems, GET_ANNOTATION(foundItems[0][0]) if foundItems else None))
    return foundItems
 
                     
# ================================================================        
# ================================================================        
def findModelItemsWithSpecificClassName(targetClasName, parentModeItem, iterativeLevelsNum = 1):
    foundItems = []
    if (parentModeItem is None):
        return foundItems
    # for modelItem, levelCnt in findModelItemWithSpecificClass(targetClasName, parentModeItem, 0, parentModeItem.rowCount()-1, iterativeLevelsNum):
    #    foundItems.append((modelItem, levelCnt))
    foundItems = findModelItemWithSpecificClass(targetClasName, parentModeItem, 0, parentModeItem.rowCount()-1, iterativeLevelsNum)
    LOG.debug("findModelItemsWithSpecificClassName... targetClasName = {} foundItems = {} {}".format(targetClasName, foundItems, GET_ANNOTATION(foundItems[0][0]) if foundItems else None))
    return foundItems
        
         
     
      
# ================================================================        
# zx comment: this genreate a modelItem whose parents or grandfathers is parentModeItem and
# className == targetClassName
# ================================================================        
def findModelItemWithSpecificClass(targetClassName, parentModeItem, first, last, iterativeLevelsNum):
    found = []
    for row in range(first, last+1):
        child = parentModeItem.childAt(row)
        LOG.debug("@@ findModelItemWithSpecificClass : targetClassName = {} parentModeItem = {} row = {} iterativeLevelsNum = {} child = {}".format(targetClassName, parentModeItem.get_label_class(), row, iterativeLevelsNum, child._key if isinstance(child, KeyValueRowModelItem) else child.get_label_class()))

        if not hasattr(child, 'get_label_class'):
            continue

        if child.get_label_class() == targetClassName:
            LOG.debug("find (child = {}, child.name.get_label_class() = {}, iterativeLevelsNum = {})".format(child, child.get_label_class(), iterativeLevelsNum))
            found += [(child, iterativeLevelsNum)]
        
        _iterativeLevelsNum = iterativeLevelsNum - 1
        if _iterativeLevelsNum > 0:
            first = 0
            last = child.rowCount() - 1
            LOG.debug(
                "@@ findModelItemWithSpecificClass 2: targetClassName = {} parentModeItem = {} first = {} last ={} iterativeLevelsNum = {}".format(
                    targetClassName, child.get_label_class(), first, last, _iterativeLevelsNum))
            subfound = findModelItemWithSpecificClass(targetClassName, child, first, last, _iterativeLevelsNum)
            if subfound is not None:
                found += subfound

    return found
            
            
def findModelItems(targetClassNamesList, targetMaxNum, parentModeItem, first, last, iterativeLevelsNum, reverse = False):
    found = []
    leftNum = targetMaxNum - len(found)
    if (parentModeItem is None) or (targetMaxNum <= 0):
        return found
        
    start = last        if reverse else first     
    end   = (first - 1) if reverse else (last + 1)
    step  = -1          if reverse else 1         
    
    for row in range(start, end, step):
        child = parentModeItem.childAt(row)
        # print "parentModeItem = {} row = {} child = {}".format(parentModeItem, row, child)

        if not hasattr(child, 'get_label_class'):
            continue

        if child.get_label_class() in targetClassNamesList:
            leftNum -= 1
            found.append(child)
             
        if leftNum <= 0:
            return found   
        
    _iterativeLevelsNum = iterativeLevelsNum - 1
    if _iterativeLevelsNum <= 0:
        return found
        
    for row in range(start, end, step):
        child = parentModeItem.childAt(row)
        if child is None:
            continue
        first = 0
        last = child.rowCount() - 1
        subfound = findModelItems(targetClassNamesList, leftNum, child, first, last, _iterativeLevelsNum, reverse)
        found = found + subfound
        leftNum = leftNum - len(found)
    
    return found        
            
            
            
def GET_ANNOTATION(obj, recursive = True):
   return obj.getAnnotations(recursive) if hasattr(obj, 'getAnnotations') else None
                           