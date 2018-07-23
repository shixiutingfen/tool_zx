# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

import os
import sys
import importlib
from sloth.conf import default_config


class Config:

    # ----------------------------------------------------------------------------------------------------------------
    # Usage
    # e.g.1: getFieldsInClassOptions(ANNOTATION_UPPER_COLOR_TOKEN, 'tag') to get all color tag names for upperBody
    # e.g.2: getFieldsInClassOptions(ANNOTATION_UPPER_CLOTH_TOKEN, 'tag') to get all cloth tag names for upperCloth
    # ----------------------------------------------------------------------------------------------------------------
    def getFieldsInClassOptions(self, className, fieldTokenInOption):
        fieldsList = None
        classConfig = self._class_configInfo.get(className, None)
        classOptions = classConfig.get('option', None) if classConfig else None
        # print "className = {} classOPtion = {}".format(className, classOptions)
        if classOptions:
            fieldsList = [ i.get(fieldTokenInOption, None) for i in classOptions ]
        return fieldsList
    
    def __init__(self):
        # init the configuration with the default config
        for setting in dir(default_config):
            if setting == setting.upper():
                setattr(self, setting, getattr(default_config, setting))

        self._class_color = {}
        self._class_text = []
        self._class_name = []
        self._class_pannelName = {}  # records BUTTONGROUP name which each label control belongs to
        self._class_configInfo = {}  # records all info configuration in default_config.py (BUTTONGROUP1 ~ BUTTONGROUP6)

        for val in iter(default_config.PANNELPROPERTY_LIST):
            pannelName = val[1]
            for element in val[0]:
                optionGroupName = element.get('name', None)
                inserterProperty = element.get('attributes', None)
                if optionGroupName:
                    self._class_configInfo[optionGroupName] = element
                    # LOG.info(u"_class_configInfo[{}] = {}".format(optionGroupName, element))
                    for b in element['option']:
                        self._class_text.append(b[default_config.METADATA_DISPLAYTEXT_TOKEN])
                        self._class_name.append(b['tag'])
                        self._class_color[b['tag']] = b.get('rgb', None) if b.get(
                            default_config.METADATA_DISPLAYCOLOR_TOKEN, None) is None else b.get(
                            default_config.METADATA_DISPLAYCOLOR_TOKEN, None)
                        self._class_pannelName[optionGroupName + ":" + b['tag']] = pannelName
                elif inserterProperty:
                    labelName = inserterProperty[default_config.METADATA_LABELCLASS_TOKEN]
                    labelText = inserterProperty[default_config.METADATA_DISPLAYTEXT_TOKEN]
                    optionInfo = inserterProperty.get('optioninfo', None)
                    if optionInfo:
                        defaultLabelName = None
                        options = optionInfo['option']
                        for o in options:
                            newLabelName = o['tag']
                            newLabelText = o[default_config.METADATA_DISPLAYTEXT_TOKEN]
                            newLabelColor = o[default_config.METADATA_DISPLAYCOLOR_TOKEN]
                            isDefaultOption = o.get(default_config.METADATA_IS_DEFAULT_TOKEN, False)
                            if isDefaultOption:
                                defaultLabelName = newLabelName
                                dfeaultLabelText = newLabelText

                            newInserterProperty = inserterProperty.copy()
                            newInserterProperty.pop('optioninfo')
                            newInserterProperty.update(o)
                            newInserterProperty.pop('tag')
                            self._class_text.append(newLabelText)
                            self._class_name.append(newLabelName)
                            self._class_color[newLabelName] = newLabelColor
                            self._class_configInfo[newLabelName] = newInserterProperty
                            self._class_pannelName[newLabelName] = pannelName

                        if not defaultLabelName:
                            defaultLabelName = options[0]['tag']
                            dfeaultLabelText = options[0][default_config.METADATA_DISPLAYTEXT_TOKEN]
                        labelColor = self._class_color[defaultLabelName]
                        labelText  = dfeaultLabelText
                        inserterProperty = self._class_configInfo[defaultLabelName]
                    else:
                        labelColor = inserterProperty[default_config.METADATA_DISPLAYCOLOR_TOKEN]

                    self._class_text.append(labelText)
                    self._class_name.append(labelName)
                    self._class_color[labelName] = labelColor
                    self._class_configInfo[labelName] = inserterProperty
                    self._class_pannelName[labelName] = pannelName
        return
        
        
    def update(self, module_path):
        try:
            oldpath = sys.path
            module_path = os.path.abspath(module_path)
            if module_path.endswith('.py'):
                module_path = module_path[:-3]
            module_dir, module_name = os.path.split(module_path)
            sys.path = [module_dir, ] + sys.path
            mod = importlib.import_module(module_name)
        except ImportError as e:
            raise ImportError("Could not import configuration '%s' (Is it on sys.path?): %s" % (module_path, e))
        finally:
            sys.path = oldpath

        for setting in dir(mod):
            if setting == setting.upper():
                setting_value = getattr(mod, setting)
                setattr(self, setting, setting_value)
        
    def getLabelText(self, clsName):
        from sloth.conf import config
        att_class = config._class_name
        for a in xrange(len(att_class)):
            if(att_class[a] ==clsName):
                return config._class_text[a]
        return None
        
    def getLabelColor(self, clsName):
        from sloth.conf import config
        return self._class_color.get(clsName, None)
  
    def getSpecificLabelInfo(self, clsName, keyOfLabelInfo):
        from sloth.conf import config
        labelInfo = self._class_configInfo.get(clsName, None)    
        if labelInfo is not None:
            return labelInfo.get(keyOfLabelInfo, None)
        return None
      
    def getLabelBelongingGroupName(self, clsName):
        from sloth.conf import config
        return self._class_pannelName.get(clsName, None)    
   
    def getColorGroupSpecificLabelInfo(self, colorGroupName, colorName):
        from sloth.conf import config
        colorText = None
        labelInfo = self._class_configInfo.get(colorGroupName, None)
        if labelInfo is not None:
            colorOptions = labelInfo.get('option', None)
            for opt in colorOptions:
                colorTag = opt.get('tag', None)
                if (colorTag is not None) and (colorTag == colorName):
                     colorText = opt.get('displaytext', None)
        return colorText
   
    
    
    
config = Config()
