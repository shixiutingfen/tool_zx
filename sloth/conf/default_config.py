# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

from sloth.conf.hisense_config import HISENSE_7COLOR_OPTIONS, HISENSE_9COLOR_OPTIONS

# ================================================================
# User configuration
# ================================================================
CHINESE_VERSION                  = 1
DEFAULT_AUTO_CONNECT_LABELS_MODE = True
ENABLE_OUTPUT_LOG_INFO           = False
DEFAULT_OUTPUT_LOG_INFO_LEVEL    = "DEBUG"
ENABLE_SELECT_UNSET_FIELD        = True

DEFAULT_LABELTEXT_BKGCOLOR_ALPHA = 80
DEFAULT_BOX_LINE_WIDTH           = 1.5

BODY_COLOR_MUST_ATTACH_TO_BODY_PART = True

# ================================================================
# tokens setting
# ================================================================
COLOR_ATTR_RGB_VALUE_TOKEN                   = 'rgb'            
METADATA_DISPLAYTEXT_TOKEN                   = 'displaytext'
METADATA_DISPLAYCOLOR_TOKEN                  = 'displaycolor'  
METADATA_ATTR_VALUE_TOKEN                    = 'tag'
METADATA_FILL_TOKEN                          = 'fill'
METADATA_DRAW_DISPLAYTEXT_TOKEN              = 'drawtext'
CHILD_ITEM_CLASS_TOKEN                       = 'subclass'
METADATA_LABELCLASS_TOKEN                    = 'class'
METADATA_POS_X_TOKEN                         = 'x'
METADATA_POS_Y_TOKEN                         = 'y'
METADATA_SIZE_WIDTH_TOKEN                    = 'width'
METADATA_SIZE_HEIGHT_TOKEN                   = 'height'
METADATA_IS_DEFAULT_TOKEN                    = 'isDefault'

# objects
ANNOTATION_PEDESTRAIN_TOKEN                  = 'pedestrain'
ANNOTATION_PERSONBIKE_TOKEN                  = 'personbike'
ANNOTATION_VEHICLE_TOKEN                     = 'vehicle'
ANNOTATION_IGNORE_TOKEN                      = 'Ignore'
ANNOTATION_OBJTYPE_WIDGET_TOKEN              = 'ObjType'
ANNOTATION_UPPER_BODY_TOKEN                  = 'upper'
ANNOTATION_LOWER_BODY_TOKEN                  = 'lower'
ANNOTATION_UMBRELLA_TOKEN                    = 'umbrella'
ANNOTATION_BACKPACK_WIDGET_TOKEN             = 'backpack'
ANNOTATION_CARRINGBAG_WIDGET_TOKEN           = 'carringbag'
ANNOTATION_HAT_WIDGET_TOKEN                  = 'hat'
ANNOTATION_MASK_WIDGET_TOKEN                 = 'mask'
ANNOTATION_GLASSES_WIDGET_TOKEN              = 'glasses'
ANNOTATION_LUGGAGE_WIDGET_TOKEN              = 'luggage'
ANNOTATION_HELMET_WIDGET_TOKEN               = 'helmet'
ANNOTATION_PLATE_WIDGET_TOKEN                = 'plate'
ANNOTATION_PLATE_TYPE_GROUP_WIDGET_TOKEN     = 'platetype'
ANNOTATION_HELMET_COLOR_TOKEN                = 'helmetcolor'
ANNOTATION_BILLBOARD_OPTION_WIDGET_TOKEN     = 'billboard'
ANNOTATION_LICENSE_PLATE_OPTION_WIDGET_TOKEN = 'licenseplate'

ANNOTATION_FACE_TOKEN                        = 'face'
ANNOTATION_HEAD_TOKEN                        = 'head'
ANNOTATION_FACE5POINTS_TOKEN                 = 'face5points'
ANNOTATION_LEFT_EYE_TOKEN                    = 'lefteye'
ANNOTATION_RIGHT_EYE_TOKEN                   = 'righteye'
ANNOTATION_LEFT_MOUTH_TOKEN                  = 'leftmouth'
ANNOTATION_RIGHT_MOUTH_TOKEN                 = 'rightmouth'
ANNOTATION_NOSE_TOKEN                        = 'nose'

# attributes
ANNOTATION_HAIR_STYLE_TOKEN                  = 'hairstyle'
ANNOTATION_ANGLE_TOKEN                       = 'angle'
ANNOTATION_AGE_TOKEN                         = 'age'
ANNOTATION_GENDER_TOKEN                      = 'gender'
ANNOTATION_UPPER_COLOR_TOKEN                 = 'uppercolor'
ANNOTATION_LOWER_COLOR_TOKEN                 = 'lowercolor'
ANNOTATION_VEHICLE_COLOR_TOKEN               = 'vehiclecolor'
ANNOTATION_UPPER_CLOTH_TOKEN                 = 'uppercloth'
ANNOTATION_LOWER_CLOTH_TOKEN                 = 'lowercloth'
ANNOTATION_UPPER_TEXTURE_TOKEN               = 'uppertexture'
ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN       = 'type'
ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN          = 'vehicletype'
ANNOTATION_VEHICLE_ANGLE_TOKEN               = 'vehicleangle'

# attributes' option tag
TAG_PERSONBIKE_TYPE_OF_THREE_WHEEL_TOKEN     = 'ThreeWheel'           
TAG_PERSONBIKE_TYPE_OF_BICYCLE_TOKEN         = 'bicycle'    
TAG_PERSONBIKE_TYPE_OF_LIGHTMOTOR_TOKEN      = 'lightmotor'  
TAG_PERSONBIKE_TYPE_OF_MOTOR_TOKEN           = 'motor'          
TAG_PERSONBIKE_TYPE_OF_UNKNOWN_TOKEN         = 'unknown'      # 'PersonBikeTypeUnknown'   # As per sim's suggestion, blank string is enough to denote unknown, but currently I need a non-empty tag as label's ID
TAG_UNSET_TOKEN                              = 'unset'
TAG_VEHICLE_COLOR_OF_UNKNOWN_TOKEN           = 'unknown'
TAG_OTHER_CASE_TOKEN                         = 'other'

# sedan小轿车 SUV越野车 minibus面包车  coach 客车 van 货车 truck 卡车  engineering truck 工程车
TAG_VEHICLE_TYPE_OF_SEDAN_TOKEN              = 'sedan'
TAG_VEHICLE_TYPE_OF_SUV_TOKEN                = 'suv'
TAG_VEHICLE_TYPE_OF_MINIBUS_TOKEN            = 'minibus'
TAG_VEHICLE_TYPE_OF_LARGE_COACH_TOKEN        = 'largecoach'
TAG_VEHICLE_TYPE_OF_MEDIUM_COACH_TOKEN       = 'mediumcoach'
TAG_VEHICLE_TYPE_OF_HEAVY_VAN_TOKEN          = 'heavyvan'
TAG_VEHICLE_TYPE_OF_LIGHT_VAN_TOKEN          = 'lightvan'
TAG_VEHICLE_TYPE_OF_ENGINEERING_TRUCK_TOKEN  = 'engineeringTruck'
TAG_VEHICLE_TYPE_OF_UNKNOWN_TOKEN            = 'unknown' 


ANNOTATION_VEHICLE_LICENSE_PLATE_TOKEN       = "vehiclelicenseplate"


# cloth type
TAG_LONG_SLEEVE_TOKEN                        = "longsleeve"
TAG_SHORT_SLEEVE_TOKEN                       = "shortsleeve"
TAG_SLEEVELESS_TOKEN                         = "sleeveless"
TAG_UPPER_BARE_TOKEN                         = "bare"
TAG_LONG_PANTS_TOKEN                         = "longpants"
TAG_SHORT_PANTS_TOKEN                        = "shortpants"
TAG_SKIRT_TOKEN                              = "skirt"

TAG_UPPER_NO_TEXTURE_TOKEN                   = "notexture"
TAG_UPPER_STRIPE_TEXTURE_TOKEN               = "stripe"
TAG_UPPER_GRID_TEXTURE_TOKEN                 = "grid"

ANNOTATION_VIDEO_FILE_FRAME_IDX_TOKEN        = 'frmidx'
ANNOTATION_VIDEO_FILE_FRAME_TIMESTAMP_TOKEN  = 'timestamp'
ANNOTATION_FRAME_TOKEN                       = 'frame'
ANNOTATION_FRAMES_TOKEN                      = 'frames'
ANNOTATION_IMAGE_TOKEN                       = 'image'
ANNOTATION_VIDEO_TOKEN                       = 'video'
ANNOTATION_FILENAME_TOKEN                    = 'filename'

ANNOTATION_LEFT_EYE_OUTER_CORNER_TOKEN       = "leoc"
ANNOTATION_LEFT_EYE_INNER_CORNER_TOKEN       = "leic"
ANNOTATION_RIGHT_EYE_INNER_CORNER_TOKEN      = "reic"
ANNOTATION_RIGHT_EYE_OUTER_CORNER_TOKEN      = "reoc"
ANNOTATION_UPPER_LIP_CENTER_TOKEN            = "ulc"
ANNOTATION_LEFT_EYE_CENTER_TOKEN             = "lec"
ANNOTATION_RIGHT_EYE_CENTER_TOKEN            = "rec"
ANNOTATION_NOSE_TIP_TOKEN                    = "nt"  
ANNOTATION_LEFT_MOUTH_CORNER_TOKEN           = "lmc"
ANNOTATION_RIGHT_MOUTH_CORNER_TOKEN          = "rmc"
ANNOTATION_MOUTH_CENTER_TOKEN                = "mc"
ANNOTATION_LABELLING_BBOX_TOKEN              = "bbox"

ANNOTATION_BBOX_ANNOMODE_TOKEN               = "bbox"
ANNOTATION_ATTR_ANNOMODE_TOKEN               = "attr"

DEFAULT_DISPLAY_MODE_OF_OPTIONS              = ANNOTATION_BBOX_ANNOMODE_TOKEN

IMG_VIEW_MODE                                      = 0
OBJ_VIEW_MODE                                      = 1
OBJ_VIEW_MAX_EDGE                                  = 150  # 32
AUTO_SWITCH_TO_IMGVIEW_MODE_WHEN_LAST_OR_FIRST_OBJ = False

ENABLE_AUTO_SAVE_ANNOTATION_FILE                   = True
AUTO_SAVE_ANNOTATION_FILE_TIME_INTERVAL_IN_SECONDS = 180
LATEST_AUTO_SAVE_FILE_NUMBER                       = 3


DEFAULT_PERSONBIKE_TYPE_TOKEN                      = TAG_PERSONBIKE_TYPE_OF_MOTOR_TOKEN
ENABLE_EXIT_INSERT_MODE_AFTER_SWTICHING_IMG        = False

# ================================================================
# keyboard setting
# ================================================================
GUI_PEDESTRAIN_BUTTON_HOTKEY                     = '1'
GUI_UPPER_BODY_BUTTON_HOTKEY                     = 'Shift+1'
GUI_LOWER_BODY_BUTTON_HOTKEY                     = 'Shift+2'
GUI_HEAD_BUTTON_HOTKEY                           = 'Shift+3'
GUI_PERSONBIKE_BUTTON_HOTKEY                     = '2'   # Note that, default personbike type is configured by DEFAULT_PERSONBIKE_TYPE_TOKEN
GUI_INSERT_PERSONBIKE_TYPE_OF_LIGHT_MOTOR_HOTKEY = 'Shift+4'
GUI_INSERT_PERSONBIKE_TYPE_OF_MOTOR_HOTKEY       = 'Shift+5'
GUI_INSERT_PERSONBIKE_TYPE_OF_BICYCLE_HOTKEY     = 'Shift+6'
GUI_INSERT_PERSONBIKE_TYPE_OF_THREE_WHEEL_HOTKEY = 'Shift+7'
GUI_INSERT_PERSONBIKE_TYPE_OF_UNKNOWN_HOTKEY     = 'Shift+8'
GUI_VEHICLE_BUTTON_HOTKEY                        = 'v'

GUI_IGNORE_BUTTON_HOTKEY                         = '0'
GUI_HELMET_BUTTON_HOTKEY                         = 'Shift+a'
GUI_PERSONBIKE_LICENSE_PLATE_HOTKEY              = 'Shift+s'
GUI_VEHICLE_LICENSE_PLATE_HOTKEY                 = 'Shift+d'
GUI_FACE_BUTTON_HOTKEY                           = 'Shift+x'
GUI_LEFT_EYE_BUTTON_HOTKEY                       = 'Shift+j'
GUI_RIGHT_EYE_BUTTON_HOTKEY                      = 'Shift+m'
GUI_NOSE_BUTTON_HOTKEY                           = 'Shift+g'
GUI_LEFT_MOUTH_BUTTON_HOTKEY                     = 'Shift+v'
GUI_RIGHT_MOUTH_BUTTON_HOTKEY                    = 'Shift+b'
GUI_FACE5POINTS_BUTTON_HOTKEY                    = 'Shift+n'

GUI_UMBRELLA_BUTTON_HOTKEY                       = '3'
GUI_BACKPACK_BUTTON_HOTKEY                       = '4'
GUI_CARRYINGBAG_BUTTON_HOTKEY                    = '5'
GUI_GLASSES_BUTTON_HOTKEY                        = '6'
GUI_HAT_BUTTON_HOTKEY                            = '7'
GUI_MASK_BUTTON_HOTKEY                           = '8'
GUI_LUGGAGE_BUTTON_HOTKEY                        = '9'


HIDDEN_PANNELS = (
   # "BUTTONGROUP1"
   # "BUTTONGROUP2",
   # "BUTTONGROUP4",
  #  "BUTTONGROUP5",
  #  "BUTTONGROUP6",
  #  "COMBOGROUP_PERSONBIKE",
    "OBJINFO"
)

PANNELS_HIDDEN_GROUPS = {
#"BUTTONGROUP6" : ANNOTATION_VEHICLE_COLOR_TOKEN
}


# ================================================================
# utility setting
# ================================================================
ANNOTATION_KEYS_ORDER = {
'x'                :  0,
'y'                :  1,
'width'            :  2,
'height'           :  3,
'pedestrain'       :  4,
'personbike'       :  5,
'type'             :  6,
'personbiketype'   :  6,
'helmet'           :  7,
'licenseplate'     :  8,
'vehicle'          :  9,
'vehicletype'      : 10,
'vehiclecolor0'    : 11, 
'vehiclecolor0Tag' : 12,
'vehiclecolor1'    : 13, 
'vehiclecolor1Tag' : 14,
'vehiclecolor2'    : 15, 
'vehiclecolor2Tag' : 16,
'angle'            : 17,        
'age'              : 18,
'gender'           : 19,
'upper'            : 20,
'uppercolor0'      : 21,
'uppercolor0Tag'   : 22,
'uppercolor1'      : 23,
'uppercolor1Tag'   : 24,
'uppercolor2'      : 25,
'uppercolor2Tag'   : 26,  
'uppercloth'       : 27,
'lower'            : 28,
'lowercolor0'      : 29,
'lowercolor0Tag'   : 30,
'lowercolor1'      : 31,
'lowercolor1Tag'   : 32,
'lowercolor2'      : 33,
'lowercolor2Tag'   : 34,
'lowercloth'       : 35,
'uppercloth'       : 36, 
'lowercloth'       : 37,
'uppertexture'     : 38,
'helmet'           : 39,
'helmetcolor'      : 40,
'head'             : 41,
'hairstyle'        : 42,
'face'             : 43,
'face5points'      : 44,
"leocx"            : 45,      
"leocy"            : 46,
"leicx"            : 47,
"leicy"            : 48,
"reicx"            : 49,
"reicy"            : 50,
"reocx"            : 51,
"reocy"            : 52,
"lecx"             : 53,
"lecy"             : 54,
"recx"             : 55,
"recy"             : 56,
"ntx"              : 57,
"nty"              : 58,
"ulcx"             : 59,
"ulcy"             : 60,
"lmcx"             : 61,
"lmcy"             : 62,
"rmcx"             : 63,
"rmcy"             : 64,
"mcx"              : 65,
"mcy"              : 66,
'lefteye'          : 67,
'righteye'         : 68,
'nose'             : 69,
'leftmouth'        : 70,
'rightmouth'       : 71,
'hat'              : 72,
'mask'             : 73,
'glasses'          : 74,
'umbrella'         : 75,
'backpack'         : 76,
'carringbag'       : 77,
'backpack'         : 78,
'luggage'          : 79
}


AUTO_CONNECT_SOURCE = {
    ANNOTATION_UPPER_BODY_TOKEN : [
       ANNOTATION_PEDESTRAIN_TOKEN,
       ANNOTATION_PERSONBIKE_TOKEN
       ],
    ANNOTATION_LOWER_BODY_TOKEN : [
       ANNOTATION_PEDESTRAIN_TOKEN,
       ANNOTATION_PERSONBIKE_TOKEN
       ],   
    ANNOTATION_HELMET_WIDGET_TOKEN : [
       ANNOTATION_PERSONBIKE_TOKEN
       ], 
    ANNOTATION_LICENSE_PLATE_OPTION_WIDGET_TOKEN : [
       ANNOTATION_PERSONBIKE_TOKEN
       ], 
    ANNOTATION_BILLBOARD_OPTION_WIDGET_TOKEN : [
       ANNOTATION_PERSONBIKE_TOKEN
       ], 
    ANNOTATION_HEAD_TOKEN : [
       ANNOTATION_PEDESTRAIN_TOKEN,
       ANNOTATION_PERSONBIKE_TOKEN
       ],   
    ANNOTATION_FACE_TOKEN : [
       ANNOTATION_HEAD_TOKEN,
       ],   
    ANNOTATION_FACE5POINTS_TOKEN : [
       ANNOTATION_FACE_TOKEN,
       ],   
    ANNOTATION_VEHICLE_LICENSE_PLATE_TOKEN : (
       ANNOTATION_VEHICLE_TOKEN,
       ),
    ANNOTATION_UMBRELLA_TOKEN : [
       ANNOTATION_PEDESTRAIN_TOKEN,
       ANNOTATION_PERSONBIKE_TOKEN
       ],   
    ANNOTATION_BACKPACK_WIDGET_TOKEN : [
       ANNOTATION_PEDESTRAIN_TOKEN,
       ANNOTATION_PERSONBIKE_TOKEN
       ],   
    ANNOTATION_LUGGAGE_WIDGET_TOKEN : [
       ANNOTATION_PEDESTRAIN_TOKEN,
       ANNOTATION_PERSONBIKE_TOKEN
       ],   
    ANNOTATION_CARRINGBAG_WIDGET_TOKEN : [
       ANNOTATION_PEDESTRAIN_TOKEN,
       ANNOTATION_PERSONBIKE_TOKEN
       ],   
    ANNOTATION_HAT_WIDGET_TOKEN : [
       ANNOTATION_PEDESTRAIN_TOKEN,
       ANNOTATION_PERSONBIKE_TOKEN
       ],   
    ANNOTATION_MASK_WIDGET_TOKEN : [
       ANNOTATION_PEDESTRAIN_TOKEN,
       ANNOTATION_PERSONBIKE_TOKEN
       ],   
    ANNOTATION_GLASSES_WIDGET_TOKEN : [
       ANNOTATION_PEDESTRAIN_TOKEN,
       ANNOTATION_PERSONBIKE_TOKEN
       ],   
}


DISPLAY_HIDEN_METADATAS_IN_ANNOTATION_SET = {
'class', 
'unlabeled', 
'unconfirmed',
METADATA_DISPLAYCOLOR_TOKEN, 
METADATA_FILL_TOKEN,
METADATA_DISPLAYTEXT_TOKEN,
METADATA_DRAW_DISPLAYTEXT_TOKEN,
}


ENABLE_TOP_OBJECT_MODE = False
DEFAULT_TOP_OBJECT = ANNOTATION_PEDESTRAIN_TOKEN # ANNOTATION_PERSONBIKE_TOKEN

ENABLE_STATISTIC_OBJ_INFO = False


UNSAVED_METADATAS_IN_ANNOTATION_SET = {
# 'unlabeled', 
'unconfirmed',
'hotkey',
METADATA_IS_DEFAULT_TOKEN,
METADATA_DISPLAYCOLOR_TOKEN, 
METADATA_FILL_TOKEN,
METADATA_DISPLAYTEXT_TOKEN,
METADATA_DRAW_DISPLAYTEXT_TOKEN,
}

                                       
NON_EXCLUSIVE_ATTRS_TAG_LIST = (           
   ANNOTATION_UPPER_COLOR_TOKEN,
   ANNOTATION_LOWER_COLOR_TOKEN,
   ANNOTATION_VEHICLE_COLOR_TOKEN,
)                                      

# ---------------------------------------------------------------------------------------------------------------------
# format:
# ( OBJECT_TOKEN: ( ( CHILDOBJ_OR_ATTR_TOKEN, IS_CHILDOBJ_OR_ATTR ), ...),
#    ...
# )
# IS_CHILDOBJ_OR_ATTR : 
#   0 --- means attribute
#   1 --- means object        
# ---------------------------------------------------------------------------------------------------------------------
OBJ_TO_CHILDOBJ_AND_ATTR_DICT = {
   
    # -----------------------------------------------------------------------------------------------------------------
    # If you want to display color and cloth with attachement to pedestrain/persoonbike, should not enable these lines.
    # If you want to display color and cloth with attachement to upperbody/lowerbody, should enable these lines.
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------

    ANNOTATION_HELMET_WIDGET_TOKEN :
    [
        (ANNOTATION_HELMET_COLOR_TOKEN, 0),
    ],

    ANNOTATION_HEAD_TOKEN :
    [
        (ANNOTATION_HAIR_STYLE_TOKEN, 0),
    ],

    ANNOTATION_PEDESTRAIN_TOKEN :
    [
        (ANNOTATION_UPPER_BODY_TOKEN,        1),
        (ANNOTATION_LOWER_BODY_TOKEN,        1),
        (ANNOTATION_HEAD_TOKEN,              1),
        (ANNOTATION_UPPER_CLOTH_TOKEN,       0),
        (ANNOTATION_UPPER_TEXTURE_TOKEN,     0),
        (ANNOTATION_UPPER_COLOR_TOKEN,       0),
        (ANNOTATION_LOWER_CLOTH_TOKEN,       0),
        (ANNOTATION_LOWER_COLOR_TOKEN,       0),
        (ANNOTATION_GENDER_TOKEN,            0),
        (ANNOTATION_AGE_TOKEN,               0),
        (ANNOTATION_ANGLE_TOKEN,             0),
        (ANNOTATION_HAIR_STYLE_TOKEN,        0),
        (ANNOTATION_UMBRELLA_TOKEN,          0),
        (ANNOTATION_BACKPACK_WIDGET_TOKEN,   1),
        (ANNOTATION_CARRINGBAG_WIDGET_TOKEN, 1), 
        (ANNOTATION_LUGGAGE_WIDGET_TOKEN,    1),
        (ANNOTATION_HAT_WIDGET_TOKEN,        1),
        (ANNOTATION_MASK_WIDGET_TOKEN,       1),
        (ANNOTATION_GLASSES_WIDGET_TOKEN,    1),
    ],  
        
    ANNOTATION_PERSONBIKE_TOKEN :
    [   
        (ANNOTATION_UPPER_BODY_TOKEN,                  1),      
        (ANNOTATION_HELMET_WIDGET_TOKEN,               1),
        (ANNOTATION_LICENSE_PLATE_OPTION_WIDGET_TOKEN, 1),
        (ANNOTATION_BILLBOARD_OPTION_WIDGET_TOKEN,     1),
        (ANNOTATION_HEAD_TOKEN,                        1),
        (ANNOTATION_UPPER_CLOTH_TOKEN,                 0),
        (ANNOTATION_UPPER_COLOR_TOKEN,                 0),
        (ANNOTATION_UPPER_TEXTURE_TOKEN,               0),
        (ANNOTATION_GENDER_TOKEN,                      0),
        (ANNOTATION_AGE_TOKEN,                         0),
        (ANNOTATION_ANGLE_TOKEN,                       0),
        (ANNOTATION_HAIR_STYLE_TOKEN,                  0),
        (ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN,       0),
        (ANNOTATION_UMBRELLA_TOKEN,                    0),
        (ANNOTATION_BACKPACK_WIDGET_TOKEN,             1),
        (ANNOTATION_CARRINGBAG_WIDGET_TOKEN,           1),
        (ANNOTATION_LUGGAGE_WIDGET_TOKEN,              1),
        (ANNOTATION_HAT_WIDGET_TOKEN,                  1),
        (ANNOTATION_MASK_WIDGET_TOKEN,                 1),
        (ANNOTATION_GLASSES_WIDGET_TOKEN,              1),
    ],  
        
    ANNOTATION_VEHICLE_TOKEN :
    [
        (ANNOTATION_VEHICLE_COLOR_TOKEN,               0),
        (ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN,          0),
        (ANNOTATION_VEHICLE_LICENSE_PLATE_TOKEN,       1),
        (ANNOTATION_VEHICLE_ANGLE_TOKEN,               0),
    ],
    
    ANNOTATION_HEAD_TOKEN :
    [
        (ANNOTATION_FACE_TOKEN,                        1),    
        (ANNOTATION_FACE5POINTS_TOKEN,                 1),
        (ANNOTATION_LEFT_EYE_TOKEN,                    1),
        (ANNOTATION_RIGHT_EYE_TOKEN,                   1),
        (ANNOTATION_LEFT_MOUTH_TOKEN,                  1),
        (ANNOTATION_RIGHT_MOUTH_TOKEN,                 1),
        (ANNOTATION_NOSE_TOKEN,                        1),
    ],            
}

if BODY_COLOR_MUST_ATTACH_TO_BODY_PART:
    OBJ_TO_CHILDOBJ_AND_ATTR_DICT.update({
        ANNOTATION_UPPER_BODY_TOKEN :
        (
            (ANNOTATION_UPPER_CLOTH_TOKEN, 0),   
            (ANNOTATION_UPPER_COLOR_TOKEN, 0), 
            (ANNOTATION_UPPER_TEXTURE_TOKEN, 0),
        ),
        
        ANNOTATION_LOWER_BODY_TOKEN :
        [
            (ANNOTATION_LOWER_CLOTH_TOKEN, 0),
            (ANNOTATION_LOWER_COLOR_TOKEN, 0),
        ],
    })



CHILDOBJ_TO_OBJ_DICT = {
    ANNOTATION_UPPER_BODY_TOKEN :
    [
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],

    ANNOTATION_LOWER_BODY_TOKEN :
    [
        ANNOTATION_PEDESTRAIN_TOKEN
    ],

    ANNOTATION_HELMET_WIDGET_TOKEN :
    [
        ANNOTATION_PERSONBIKE_TOKEN
    ],
    
    ANNOTATION_LICENSE_PLATE_OPTION_WIDGET_TOKEN :
    [
        ANNOTATION_PERSONBIKE_TOKEN
    ],

    ANNOTATION_BILLBOARD_OPTION_WIDGET_TOKEN :
    [
        ANNOTATION_PERSONBIKE_TOKEN
    ],

    ANNOTATION_HEAD_TOKEN :
    [
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],

    ANNOTATION_FACE_TOKEN :
    [
        ANNOTATION_HEAD_TOKEN,
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],
    
    ANNOTATION_FACE5POINTS_TOKEN :
    [
        ANNOTATION_FACE_TOKEN,
        ANNOTATION_HEAD_TOKEN,
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],
    
    ANNOTATION_LEFT_EYE_TOKEN :
    [
        ANNOTATION_FACE_TOKEN,
        ANNOTATION_HEAD_TOKEN,
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],
    
    ANNOTATION_RIGHT_EYE_TOKEN :
    [
        ANNOTATION_FACE_TOKEN,
        ANNOTATION_HEAD_TOKEN,
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],
    
    ANNOTATION_LEFT_MOUTH_TOKEN :
    [
        ANNOTATION_FACE_TOKEN,
        ANNOTATION_HEAD_TOKEN,
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],
    
    ANNOTATION_RIGHT_MOUTH_TOKEN :
    [
        ANNOTATION_FACE_TOKEN,
        ANNOTATION_HEAD_TOKEN,
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],
    
    ANNOTATION_NOSE_TOKEN :
    [
        ANNOTATION_FACE_TOKEN,
        ANNOTATION_HEAD_TOKEN,
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],
    
    ANNOTATION_UMBRELLA_TOKEN :
    [
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],
    
    ANNOTATION_VEHICLE_LICENSE_PLATE_TOKEN :
    [
        ANNOTATION_VEHICLE_TOKEN
    ],

    ANNOTATION_BACKPACK_WIDGET_TOKEN :
    [
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],
           
    ANNOTATION_LUGGAGE_WIDGET_TOKEN :
    [
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],
    
    ANNOTATION_CARRINGBAG_WIDGET_TOKEN :
    [
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],

    ANNOTATION_HAT_WIDGET_TOKEN :
    [
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],

    ANNOTATION_MASK_WIDGET_TOKEN :
    [
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],

    ANNOTATION_GLASSES_WIDGET_TOKEN :
    [
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN
    ],
}
   
ATTRIBUTE_RELATE_TO_OBJECT_KEYVALUE_RELATIONSHIP = {
    ANNOTATION_HELMET_COLOR_TOKEN  :
    (
        ANNOTATION_HELMET_WIDGET_TOKEN,
    ),
    ANNOTATION_VEHICLE_COLOR_TOKEN :  
    (
        ANNOTATION_VEHICLE_TOKEN   ,
    ),    
    ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN :
    (
        ANNOTATION_VEHICLE_TOKEN   ,
    ),    
    ANNOTATION_VEHICLE_ANGLE_TOKEN :
    (
        ANNOTATION_VEHICLE_TOKEN   ,
    ),    
    ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN: 
    ( 
        ANNOTATION_PERSONBIKE_TOKEN,
    ),    
    ANNOTATION_GENDER_TOKEN        : 
    ( 
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN,
    ),    
    ANNOTATION_AGE_TOKEN           :  
    ( 
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN,
    ),    
    ANNOTATION_ANGLE_TOKEN         :  
    ( 
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN,
    ),    
    ANNOTATION_HAIR_STYLE_TOKEN    : 
    ( 
        ANNOTATION_PEDESTRAIN_TOKEN,
        ANNOTATION_PERSONBIKE_TOKEN,
    ),    
}


if BODY_COLOR_MUST_ATTACH_TO_BODY_PART:
    ATTRIBUTE_RELATE_TO_OBJECT_KEYVALUE_RELATIONSHIP.update({
        ANNOTATION_UPPER_COLOR_TOKEN   : 
        (
           ANNOTATION_UPPER_BODY_TOKEN,
        ),    
        ANNOTATION_LOWER_COLOR_TOKEN   : 
        (
            ANNOTATION_LOWER_BODY_TOKEN,
        ),  
        ANNOTATION_UPPER_CLOTH_TOKEN   :  
        (
            ANNOTATION_UPPER_BODY_TOKEN,
        ),    
        ANNOTATION_UPPER_TEXTURE_TOKEN :
        (
            ANNOTATION_UPPER_BODY_TOKEN,
        ),    
        
        ANNOTATION_LOWER_CLOTH_TOKEN   : 
        (
            ANNOTATION_LOWER_BODY_TOKEN,
        ),    
      }) 
else:
    ATTRIBUTE_RELATE_TO_OBJECT_KEYVALUE_RELATIONSHIP.update({
        ANNOTATION_UPPER_COLOR_TOKEN   : 
        (
            ANNOTATION_PEDESTRAIN_TOKEN,
            ANNOTATION_PERSONBIKE_TOKEN,
        ),    
        ANNOTATION_LOWER_COLOR_TOKEN   : 
        (
            ANNOTATION_PEDESTRAIN_TOKEN,
        ),  
        ANNOTATION_UPPER_CLOTH_TOKEN   :  
        (
            ANNOTATION_PEDESTRAIN_TOKEN,
            ANNOTATION_PERSONBIKE_TOKEN,
        ),    
        ANNOTATION_UPPER_TEXTURE_TOKEN :
        (
            ANNOTATION_PEDESTRAIN_TOKEN,
            ANNOTATION_PERSONBIKE_TOKEN,
        ),    
        
        ANNOTATION_LOWER_CLOTH_TOKEN   : 
        (
            ANNOTATION_PEDESTRAIN_TOKEN,
        ),    
      }) 
        

ATTRIBUTE_STICKER_DEFAULT_DISPLAY_POS_INFO_IN_OBJ = {
# ------------------------------------------------------------------------------------------------------
#    object                                     startX     startY  external_layout  internal_layout
#    Note that:
#     - for layout: 0 - vertical; 1 - horizontal;
# ------------------------------------------------------------------------------------------------------
   ANNOTATION_PEDESTRAIN_TOKEN                  : ( -1,      0,         0,            1 ), 
   ANNOTATION_PERSONBIKE_TOKEN                  : ( -1,      0,         0,            1 ), 
   ANNOTATION_VEHICLE_TOKEN                     : ( -1,      0,         0,            1 ), 
   ANNOTATION_UPPER_BODY_TOKEN                  : (  0,      0,         0,            1 ), 
   ANNOTATION_UPPER_COLOR_TOKEN                 : (  -1,      0,         0,            1 ), 
   ANNOTATION_LOWER_COLOR_TOKEN                 : (  -1,      0,         0,            1 ), 
   ANNOTATION_UPPER_CLOTH_TOKEN                 : (  -1,      0,         0,            1 ), 
   ANNOTATION_UPPER_TEXTURE_TOKEN               : (  -1,      0,         0,            1 ), 
   ANNOTATION_LOWER_CLOTH_TOKEN                 : (  -1,      0,         0,            1 ), 
   ANNOTATION_LOWER_BODY_TOKEN                  : (  0,      0,         0,            1 ), 
   ANNOTATION_HELMET_WIDGET_TOKEN               : (  0,      0,         0,            1 ),
   ANNOTATION_LICENSE_PLATE_OPTION_WIDGET_TOKEN : (  0,      0,         0,            1 ),
   ANNOTATION_BILLBOARD_OPTION_WIDGET_TOKEN     : (  0,      0,         0,            1 ),
   ANNOTATION_HEAD_TOKEN                        : (  0,      0,         0,            1 ), 
   ANNOTATION_FACE_TOKEN                        : (  0,      0,         0,            1 ), 
   ANNOTATION_LEFT_EYE_TOKEN                    : (  0,      0,         0,            1 ),  
   ANNOTATION_RIGHT_EYE_TOKEN                   : (  0,      0,         0,            1 ),  
   ANNOTATION_LEFT_MOUTH_TOKEN                  : (  0,      0,         0,            1 ),  
   ANNOTATION_RIGHT_MOUTH_TOKEN                 : (  0,      0,         0,            1 ),  
   ANNOTATION_FACE5POINTS_TOKEN                 : (  0,      0,         0,            1 ),     
   ANNOTATION_NOSE_TOKEN                        : (  0,      0,         0,            1 ),  
   ANNOTATION_UMBRELLA_TOKEN                    : (  0,      0,         0,            1 ), 
   ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN          : (  0,      0,         0,            1 ),   
   ANNOTATION_VEHICLE_ANGLE_TOKEN               : (  0,      0,         0,            1 ),  
   ANNOTATION_VEHICLE_COLOR_TOKEN               : (  0,      0,         0,            1 ),
   ANNOTATION_BACKPACK_WIDGET_TOKEN             : (  0,      0,         0,            1 ), 
   ANNOTATION_CARRINGBAG_WIDGET_TOKEN           : (  0,      0,         0,            1 ), 
   ANNOTATION_LUGGAGE_WIDGET_TOKEN              : (  0,      0,         0,            1 ), 
   ANNOTATION_HAT_WIDGET_TOKEN                  : (  0,      0,         0,            1 ), 
   ANNOTATION_MASK_WIDGET_TOKEN                 : (  0,      0,         0,            1 ), 
   ANNOTATION_GLASSES_WIDGET_TOKEN              : (  0,      0,         0,            1 ), 
}


ATTRIBUTE_STICKER_DISPLAY_ORDER = {
# ------------------------------------------------------------------------------------------------------
#    attribute labels                     order
# ------------------------------------------------------------------------------------------------------
    ANNOTATION_UPPER_COLOR_TOKEN      :    0, 
    ANNOTATION_UPPER_CLOTH_TOKEN      :    1, #4, #1, 
    ANNOTATION_UPPER_TEXTURE_TOKEN    :    2, 

    ANNOTATION_LOWER_COLOR_TOKEN      :    0, #0, 
    ANNOTATION_LOWER_CLOTH_TOKEN      :    1, #5, #1, 
    

    ANNOTATION_GENDER_TOKEN           :    0, 
    ANNOTATION_AGE_TOKEN              :    1, 
    ANNOTATION_ANGLE_TOKEN            :    2, 
    ANNOTATION_HAIR_STYLE_TOKEN       :    3,
     
    ANNOTATION_HELMET_COLOR_TOKEN     :    0,
    ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN : 4,

    ANNOTATION_VEHICLE_COLOR_TOKEN    :    0, 
    ANNOTATION_VEHICLE_ANGLE_TOKEN    :    1,
    ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN :  2,
}
 

ALLOWED_DISPLAY_OBJECTS_AND_ATTRIBUTE_STICKERS = {
# ------------------------------------------------------------------------------------------------------
#    object labels                           allowed_display_objects_and_attribute_stickers_labels
# ------------------------------------------------------------------------------------------------------
   ANNOTATION_PEDESTRAIN_TOKEN        :   [ANNOTATION_PEDESTRAIN_TOKEN, ANNOTATION_UPPER_BODY_TOKEN,  ANNOTATION_LOWER_BODY_TOKEN,            ANNOTATION_HAIR_STYLE_TOKEN, ANNOTATION_ANGLE_TOKEN, ANNOTATION_AGE_TOKEN, ANNOTATION_GENDER_TOKEN, ANNOTATION_HEAD_TOKEN],
   ANNOTATION_PERSONBIKE_TOKEN        :   [ANNOTATION_PERSONBIKE_TOKEN, ANNOTATION_UPPER_BODY_TOKEN,  ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN, ANNOTATION_HAIR_STYLE_TOKEN, ANNOTATION_ANGLE_TOKEN, ANNOTATION_AGE_TOKEN, ANNOTATION_GENDER_TOKEN, ANNOTATION_HELMET_WIDGET_TOKEN, ANNOTATION_LICENSE_PLATE_OPTION_WIDGET_TOKEN, ANNOTATION_BILLBOARD_OPTION_WIDGET_TOKEN, ANNOTATION_HEAD_TOKEN],
   ANNOTATION_VEHICLE_TOKEN           :   [ANNOTATION_VEHICLE_TOKEN,    ANNOTATION_UPPER_BODY_TOKEN,  ANNOTATION_VEHICLE_COLOR_TOKEN,ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN,    ANNOTATION_VEHICLE_LICENSE_PLATE_TOKEN, ANNOTATION_VEHICLE_ANGLE_TOKEN, ANNOTATION_HAIR_STYLE_TOKEN, ANNOTATION_ANGLE_TOKEN, ANNOTATION_AGE_TOKEN, ANNOTATION_GENDER_TOKEN],
   ANNOTATION_UPPER_BODY_TOKEN        :   [ANNOTATION_UPPER_BODY_TOKEN, ANNOTATION_UPPER_COLOR_TOKEN, ANNOTATION_UPPER_CLOTH_TOKEN, ANNOTATION_UPPER_TEXTURE_TOKEN, ANNOTATION_HAIR_STYLE_TOKEN, ANNOTATION_ANGLE_TOKEN, ANNOTATION_AGE_TOKEN, ANNOTATION_GENDER_TOKEN],
   ANNOTATION_LOWER_BODY_TOKEN        :   [ANNOTATION_LOWER_BODY_TOKEN, ANNOTATION_LOWER_COLOR_TOKEN, ANNOTATION_LOWER_CLOTH_TOKEN,                                 ANNOTATION_HAIR_STYLE_TOKEN, ANNOTATION_ANGLE_TOKEN, ANNOTATION_AGE_TOKEN, ANNOTATION_GENDER_TOKEN],
   ANNOTATION_HELMET_WIDGET_TOKEN     :   [ANNOTATION_HELMET_COLOR_TOKEN],
}


if not BODY_COLOR_MUST_ATTACH_TO_BODY_PART:
    ALLOWED_DISPLAY_OBJECTS_AND_ATTRIBUTE_STICKERS[ANNOTATION_PEDESTRAIN_TOKEN] += [ANNOTATION_UPPER_COLOR_TOKEN, ANNOTATION_LOWER_COLOR_TOKEN, ANNOTATION_UPPER_CLOTH_TOKEN,  ANNOTATION_UPPER_TEXTURE_TOKEN, ANNOTATION_LOWER_CLOTH_TOKEN]
    ALLOWED_DISPLAY_OBJECTS_AND_ATTRIBUTE_STICKERS[ANNOTATION_PERSONBIKE_TOKEN] += [ANNOTATION_UPPER_COLOR_TOKEN, ANNOTATION_LOWER_COLOR_TOKEN, ANNOTATION_UPPER_CLOTH_TOKEN,  ANNOTATION_UPPER_TEXTURE_TOKEN, ANNOTATION_LOWER_CLOTH_TOKEN]



ALLOWED_PARENTS_INDEX_IN_RELATIONSHIP                = 0
ALLOWED_CHILD_NUM_IN_RELATIONSHIP                    = 1
CHILD_POS_IS_BOUNDED_IN_PARENT_INDEX_IN_RELATIONSHIP = 2     
 
OBJ_ANNOTATION_POSTION_BOUND_RELLATIONSHIP = {
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# child object                       allowed parent objects                                                                  allowed_child_num_for_each_parent   child_postion_must_be_inside_of_parent_position  
#                                                                                                                                                                # - True: this annotation position must be                   
#                                                                                                                                                                          be inside of ts parent bbox position
# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ANNOTATION_PEDESTRAIN_TOKEN          : [[ANNOTATION_IMAGE_TOKEN, ANNOTATION_FRAME_TOKEN],                                        [-1, -1],                        False                                        ], 
ANNOTATION_PERSONBIKE_TOKEN          : [[ANNOTATION_IMAGE_TOKEN, ANNOTATION_FRAME_TOKEN],                                        [-1, -1],                        False                                        ], 
ANNOTATION_VEHICLE_TOKEN             : [[ANNOTATION_IMAGE_TOKEN, ANNOTATION_FRAME_TOKEN],                                        [-1, -1],                        False                                        ], 
ANNOTATION_UPPER_BODY_TOKEN          : [[ANNOTATION_PEDESTRAIN_TOKEN, ANNOTATION_PERSONBIKE_TOKEN, ANNOTATION_VEHICLE_TOKEN],    [ 1,  5, 10],                    True                                         ], 
ANNOTATION_LOWER_BODY_TOKEN          : [[ANNOTATION_PEDESTRAIN_TOKEN],                                                           [ 1],                            True                                         ], 
ANNOTATION_HELMET_WIDGET_TOKEN       : [[ANNOTATION_PERSONBIKE_TOKEN],                                                           [ 5],                            False                                        ], 
ANNOTATION_LICENSE_PLATE_OPTION_WIDGET_TOKEN: [[ANNOTATION_PERSONBIKE_TOKEN],                                                    [ 1],                            False                                        ],
ANNOTATION_BILLBOARD_OPTION_WIDGET_TOKEN:     [[ANNOTATION_PERSONBIKE_TOKEN],                                                    [ 5],                            False                                        ],
ANNOTATION_HEAD_TOKEN                : [[ANNOTATION_PEDESTRAIN_TOKEN, ANNOTATION_PERSONBIKE_TOKEN, ANNOTATION_VEHICLE_TOKEN],    [ 500,  500, 500],                    False                                        ], 
ANNOTATION_FACE_TOKEN                : [[ANNOTATION_HEAD_TOKEN],                                                                 [ 1],                            True                                         ], 
ANNOTATION_LEFT_EYE_TOKEN            : [[ANNOTATION_FACE_TOKEN],                                                                 [ 1],                            True                                         ], 
ANNOTATION_RIGHT_EYE_TOKEN           : [[ANNOTATION_FACE_TOKEN],                                                                 [ 1],                            True                                         ], 
ANNOTATION_LEFT_MOUTH_TOKEN          : [[ANNOTATION_FACE_TOKEN],                                                                 [ 1],                            True                                         ], 
ANNOTATION_RIGHT_MOUTH_TOKEN         : [[ANNOTATION_FACE_TOKEN],                                                                 [ 1],                            True                                         ], 
ANNOTATION_NOSE_TOKEN                : [[ANNOTATION_FACE_TOKEN],                                                                 [ 1],                            True                                         ], 
ANNOTATION_FACE5POINTS_TOKEN         : [[ANNOTATION_FACE_TOKEN],                                                                 [ 1],                            True                                         ], 
ANNOTATION_UMBRELLA_TOKEN            : [[ANNOTATION_PEDESTRAIN_TOKEN, ANNOTATION_PERSONBIKE_TOKEN],                              [ 50, 50],                         False                                        ], 
ANNOTATION_VEHICLE_LICENSE_PLATE_TOKEN  : [[ANNOTATION_VEHICLE_TOKEN],                                                              [ 2],                            False                                        ], 
ANNOTATION_BACKPACK_WIDGET_TOKEN     : [[ANNOTATION_PEDESTRAIN_TOKEN, ANNOTATION_PERSONBIKE_TOKEN],                              [ 50, 50],                         False                                        ], 
ANNOTATION_CARRINGBAG_WIDGET_TOKEN   : [[ANNOTATION_PEDESTRAIN_TOKEN, ANNOTATION_PERSONBIKE_TOKEN],                              [ 50, 50],                         False                                        ], 
ANNOTATION_HAT_WIDGET_TOKEN          : [[ANNOTATION_PEDESTRAIN_TOKEN, ANNOTATION_PERSONBIKE_TOKEN],                              [ 50, 50],                         False                                        ], 
ANNOTATION_MASK_WIDGET_TOKEN         : [[ANNOTATION_PEDESTRAIN_TOKEN, ANNOTATION_PERSONBIKE_TOKEN],                              [ 50, 50],                         True                                         ], 
ANNOTATION_GLASSES_WIDGET_TOKEN      : [[ANNOTATION_PEDESTRAIN_TOKEN, ANNOTATION_PERSONBIKE_TOKEN],                              [ 50, 50],                         True                                         ], 
ANNOTATION_LUGGAGE_WIDGET_TOKEN      : [[ANNOTATION_PEDESTRAIN_TOKEN, ANNOTATION_PERSONBIKE_TOKEN],                              [ 50, 50],                         False                                        ], 
} 



OBJ_VIEW_MODE_ALLOWED_TOP_LEVEL_OBJ_TYPE = (
    ANNOTATION_PEDESTRAIN_TOKEN        ,
    ANNOTATION_PERSONBIKE_TOKEN        ,
    ANNOTATION_VEHICLE_TOKEN           ,
)
        
COLOR_ATTRS_TUPLE = (
    ANNOTATION_UPPER_COLOR_TOKEN,
    ANNOTATION_LOWER_COLOR_TOKEN,
    ANNOTATION_VEHICLE_COLOR_TOKEN,
    ANNOTATION_HELMET_COLOR_TOKEN
    )
    
                                            
# ==================================================================================
# statistic plugin display elements setting
# ==================================================================================
STATISTICS_PLUGIN_DISPLAY_ELEMENTS_DICT = {
   0 : [ "ObjType"                      , [ ANNOTATION_PEDESTRAIN_TOKEN, ANNOTATION_PERSONBIKE_TOKEN, ANNOTATION_VEHICLE_TOKEN ] ],
   1 : [ "PersonBodyType"               , [ ANNOTATION_UPPER_BODY_TOKEN, ANNOTATION_LOWER_BODY_TOKEN ]                           ],
   2 : [ ANNOTATION_UPPER_COLOR_TOKEN   , [ ANNOTATION_UPPER_COLOR_TOKEN ]                                                       ],
   3 : [ ANNOTATION_LOWER_COLOR_TOKEN   , [ ANNOTATION_LOWER_COLOR_TOKEN ]                                                       ],
   4 : [ ANNOTATION_VEHICLE_COLOR_TOKEN , [ ANNOTATION_VEHICLE_COLOR_TOKEN ]                                                     ],
#   5 : [ ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN, [ TAG_PERSONBIKE_TYPE_OF_THREE_WHEEL_TOKEN, TAG_PERSONBIKE_TYPE_OF_BICYCLE_TOKEN,  TAG_PERSONBIKE_TYPE_OF_LIGHTMOTOR_TOKEN, TAG_PERSONBIKE_TYPE_OF_MOTOR_TOKEN, TAG_PERSONBIKE_TYPE_OF_UNKNOWN_TOKEN]   ],
}


# ==================================================================================
# LOG INFO LEVEL setting     
# ==================================================================================
import logging
LOG_INFO_LEVEL_MAPPING = {
"DEBUG"    : logging.DEBUG,
"WARNING"  : logging.WARNING,
"CRITICAL" : logging.CRITICAL,
}
                                        
# ==================================================================================
# Language-related configuration
# ==================================================================================
if CHINESE_VERSION == 0:

    GUI_PEDESTRAIN_WIDGET_DISPLAYTEXT             = 'Pedestrain'
    GUI_PERSONBIKE_WIDGET_DISPLAYTEXT             = 'PersonBike'
    GUI_VEHICLE_WIDGET_DISPLAYTEXT                = 'Vehicle'
    GUI_IGNORE_WIDGET_DISPLAYTEXT                 = 'Ignore'
    GUI_HEAD_WIDGET_DISPLAYTEXT                   = 'Head'
                                                  
    GUI_UPPERBODY_WIDGET_DISPLAYTEXT              = 'Upper' 
    GUI_LOWERBODY_WIDGET_DISPLAYTEXT              = 'Lower'      
    GUI_HELMET_WIDGET_DISPLAYTEXT                 = 'Helmet'
    GUI_LICENSE_PLATE_WIDGET_DISPLAYTEXT          = 'LicensePlate'
    GUI_PLATE_WIDGET_DISPLAYTEXT                  = 'Plate'
    GUI_OBJTYPE_WIDGET_DISPLAYTEXT                = 'Object'
    GUI_LICENSE_PLATE_WIDGET_DISPLAYTEXT          = 'licenseplate'
    GUI_BILLBOARD_WIDGET_DISPLAYTEXT              = 'billboard'
    GUI_PLATE_TYPE_GROUP_WIDGET_DISPLAYTEXT       = 'platetype'
    GUI_OBJTYPE_GROUP_WIDGET_DISPLAYTEXT          = 'ObjType'
    GUI_UMBRELLA_WIDGET_DISPLAYTEXT               = 'Umbrella'
    GUI_BACKPACK_WIDGET_DISPLAYTEXT               = 'Backpack' 
    GUI_CARRYINGBAG_WIDGET_DISPLAYTEXT            = 'CarryingBag'
    GUI_HAT_WIDGET_DISPLAYTEXT                    = 'Hat' 
    GUI_GLASSES_WIDGET_DISPLAYTEXT                = 'Glasses' 
    GUI_MASK_WIDGET_DISPLAYTEXT                   = 'Mask' 
    GUI_LUGGAGE_WIDGET_DISPLAYTEXT                = 'Luggage'
    GUI_FACE_WIDGET_DISPLAYTEXT                   = 'Face'
    GUI_HEAD_WIDGET_DISPLAYTEXT                   = 'Head'
    GUI_LEFT_EYE_CENTER_WIDGET_DISPLAYTEXT        = 'LeftEyeCenter'
    GUI_RIGHT_EYE_CENTER_WIDGET_DISPLAYTEXT       = 'RightEyeCener'
    GUI_NOSE_TIP_WIDGET_DISPLAYTEXT               = 'NoseTip'
    GUI_LEFT_MOUTH_CORNER_WIDGET_DISPLAYTEXT      = 'LeftMouthCorner'
    GUI_RIGHT_MOUTH_CORNER_WIDGET_DISPLAYTEXT     = 'RightMouthCorner'
    GUI_FACE5POINTS_WIDGET_DISPLAYTEXT             = 'Face5Points'

    GUI_GENDER_WIDGET_DISPLAYTEXT                 = u'Gender'
    GUI_AGE_WIDGET_DISPLAYTEXT                    = u'Age'
    GUI_ANGLE_WIDGET_DISPLAYTEXT                  = u'Angle'
    GUI_VEHICLE_ANGLE_WIDGET_DISPLAYTEXT          = u'Vehicle Angle'
    GUI_HAIR_STYLE_WIDGET_DISPLAYTEXT             = u'HairStyle'
 
    GUI_VEHICLE_COLOR_WIDGET_DISPLAYTEXT          = u'Vehicle Color'
    GUI_PERSONBIKE_TYPE_WIDGET_DISPLAYTEXT        = u'Personbike Type'
    TAG_PERSONBIKE_TYPE_OF_THREE_WHEEL_DISPLAYTEXT= u'ThreeWheel'
    TAG_PERSONBIKE_TYPE_OF_UNKNOWN_DISPLAYTEXT    = u'UnknownTypeOfTwoWheel'
    GUI_PERSONBIKE_TYPE_GROUP_WIDGET_DISPLAYTEXT  = u'Personbike Type'
    TAG_PERSONBIKE_TYPE_OF_BICYCLE_DISPLAYTEXT    = u'bicycle'    
    TAG_PERSONBIKE_TYPE_OF_LIGHTMOTOR_DISPLAYTEXT = u'lightmotor'  
    TAG_PERSONBIKE_TYPE_OF_MOTOR_DISPLAYTEXT      = u'motor'  
    
    GUI_VEHICLE_LICENSE_PLATE_WIDGET_DISPLAYTEXT  = u'LicensePlate'

    TAG_VEHICLE_TYPE_OF_SEDAN_DISPLAYTEXT            = u'sedan'
    TAG_VEHICLE_TYPE_OF_SUV_DISPLAYTEXT              = u'suv'
    TAG_VEHICLE_TYPE_OF_MINIBUS_DISPLAYTEXT          = u'minibus'
    TAG_VEHICLE_TYPE_OF_LARGE_COACH_DISPLAYTEXT      = u'largecoach'
    TAG_VEHICLE_TYPE_OF_MEDIUM_COACH_DISPLAYTEXT     = u'mediumcoach'
    TAG_VEHICLE_TYPE_OF_HEAVY_VAN_DISPLAYTEXT        = u'heavyvan'
    TAG_VEHICLE_TYPE_OF_LIGHT_VAN_DISPLAYTEXT        = u'lightvan'
    TAG_VEHICLE_TYPE_OF_TRUCK_DISPLAYTEXT            = u'truck'
    TAG_VEHICLE_TYPE_OF_ENGINEERING_TRUCK_DISPLAYTEXT= u'engineeringTruck'
    GUI_PERSONBIKE_TYPE_GROUP_WIDGET_DISPLAYTEXT     = u'vehicletype'
    
    
    TAG_UNSET_DISPLAYTEXT                         = u'Unset'  
    TAG_VEHICLE_TYPE_OF_UNKNOWN_DISPLAYTEXT       = u'Unknown'     
    TAG_VEHICLE_COLOR_OF_UNKNOWN_DISPLAYTEXT      = u'Unknown'  
                                                      
    GUI_ANNOTATION_MODEL_HEAD_COL0_DISPLAYTEXT    = "File/Type/Key"
    GUI_ANNOTATION_MODEL_HEAD_COL1_DISPLAYTEXT    = "Value"
                                                  
    GUI_SET_VIDEO_FRME_INTERVAL_DIALOG_TITLE      = "Set video frame interval"
    GUI_SET_VIDEO_FRME_INTERVAL_DIALOG_TEXT       = "Please set frame interval for added video. i.e.: one frame from every N frames will be showed and annotated further"
                                                  
    GUI_OK_DISPLAYTEXT                            = "OK"
    GUI_SPECIFY_VIDEO_FILE_TIP                    = u"Please specify valid video file!"    
                                                  
    GUI_BUTTONGROUP1_DISPLAYTEXT                  = "Object Type"              
    GUI_BUTTONGROUP2_DISPLAYTEXT                  = "Person Body Parts"
    GUI_BUTTONGROUP3_DISPLAYTEXT                  = "Person Accessories"
    GUI_BUTTONGROUP4_DISPLAYTEXT                  = "Person Clothes"
    GUI_BUTTONGROUP5_DISPLAYTEXT                  = "Person Details"
    GUI_BUTTONGROUP6_DISPLAYTEXT                  = "Vehicle Info"
    GUI_PERSONBIKE_PANEL_DISPLAYTEXT              = "Personbike Info"    
    GUI_PERSONBIKE_BBOXS_DISPLAYTEXT              = "Attachment bbox"
    GUI_OBJTYPE_GROUP_DISPLAYTEXT                 = "ObjType options"
    GUI_VEHICLE_BBOXS_DISPLAYTEXT                 = "bbox"
    GUI_OBJINFO_PANNEL_DISPLAYTEXT                = "Object Info"
                                                  
    GUI_ANNOTATION_DISPLAYTEXT                    = "Annotations"
    GUI_MORE_WIDGET_DISPLAYTEXT                   = "More"
                                                  
    GUI_MENU_PLUGIN_DISPLAYTEXT                   = "Plugins"
    GUI_MENU_SHORTCUT_DISPLAYTEXT                 = "Shortcuts"
    GUI_MENU_OPTION_DISPLAYTEXT                   = "Options"
    GUI_MENU_FILE_DISPLAYTEXT                     = "File"
    GUI_MENU_EDIT_DISPLAYTEXT                     = "Edit"
    GUI_MENU_VIEW_DISPLAYTEXT                     = "View"
    GUI_MENU_HELP_DISPLAYTEXT                     = "Help"
    GUI_MENU_NET_DISPLAYTEXT                      = "Net"
                                                  
    GUI_MENU_EDIT_ACTION_ADD_IMG_DISPLAYTEXT      = "Add Image"
    GUI_MENU_EDIT_ACTION_ADD_VIDEO_DISPLAYTEXT    = "Add Video"
    GUI_MENU_FILE_ACTION_NEW_DISPLAYTEXT          = "New"
    GUI_MENU_FILE_ACTION_OPEN_DISPLAYTEXT         = "Open annotation file"
    GUI_MENU_FILE_ACTION_SAVE_DISPLAYTEXT         = "Save annotation file"
    GUI_MENU_FILE_ACTION_SAVEAS_DISPLAYTEXT       = "Save annotation file as"
    GUI_MENU_FILE_ACTION_EXIT_DISPLAYTEXT         = "Exit"
    GUI_MENU_VIEW_ACTION_LOCKED                   = "Locked"
    GUI_MENU_OPTION_ACTION_FITTOWIN_DISPLAYTEXT   = "Fit-to-window mode"
    GUI_MENU_HELP_ACTION_ABOUT_DISPLAYTEXT        = "About"
    GUI_MENU_HELP_ACTION_IMPORTNET_DISPLAYTEXT    = "ImportNet"

    GUI_ABOUT_DIALOG_TITLE                        = "About %s"
    GUI_ABOUT_DIALOG_TEXT                         = """<b>%s</b><p>version %s<p>
                <p>This labeling application for computer vision research
                was developed at the CVHCI research group at KIT.
                <p>For more details, visit our homepage: <a href="%s">%s</a>"""

    GUI_SAVE_CHANGE_MSGBOX_TITLE_TEXT             = "%s - Unsaved Changes"      
    GUI_SAVE_CHANGE_MSGBOX_QUESTION_TEXT          = "Save unsaved changes?"       
    GUI_SAVE_ANNOTATIONS_DIALOG_TITLE_TEXT        = "%s - Save Annotations"
    GUI_SAVE_ANNOTATIONS_DIALOG_SAVETYPE_TEXT     = "annotation files (%s)"
    GUI_OPEN_ANNOTATIONS_DIALOG_TITLE_TEXT        = "%s - Load Annotations"
    GUI_OPEN_ANNOTATIONS_DIALOG_OPENTYPE_TEXT     = "annotation files (%s)"
                                                  
    GUI_UNAMED_ANNOTATION_TEXT                    = u"Unamed Annotation File"
                                                  
    GUI_CONFIRMALL_N_GOTONEXT_TIP                 = 'Mark image as labeled/confirmed and go to next'
    GUI_PREV_IMG_TIP                              = 'Previous image/frame/object'
    GUI_NEXT_IMG_TIP                              = 'Next image/frame/object'
    GUI_GOTO_BEGIN_TIP                            = 'First image/frame/object'
    GUI_GOTO_END_TIP                              = 'Last image/frame/object'
    GUI_TOGGLE_DISPLAY_VIEW_TIP                   = 'Toggle display view'
    GUI_AUTO_CONNECT_LABELS_TIP                   = 'Auto connect labels'
    GUI_NEXT_ANNOTATION_TIP                       = 'Select next annotation'
    GUI_PREV_ANNOTATION_TIP                       = 'Select previous annotation'
    GUI_FIT_CUR_IMG_INTO_WIN_TIP                  = 'Fit current image/frame into window'
    GUI_DEL_SELECTED_ANNOTATIONS_TIP              = 'Delete selected annotations'
    GUI_EXIT_INSERT_MODE                          = 'Exit insert mode'
    GUI_SAVE_CUR_VIEW_IMG_CONTENT_TO_FILE_TIP     = 'Save current viewing image cotent to BMP file'
    GUI_SAVE_ALL_IMGS_VIEW_CONTENT_TO_FILES_TIP   = "Save all images' view contents to BMP files"
    GUI_MARK_CUR_IMG_AS_LABELED_TIP               = 'Mark current image as valid'
    GUI_MARK_CUR_IMG_AS_UNLABELED_TIP             = 'Mark current image as invalid'
    GUI_FILP_CUR_IMG_LABELED_TIP                  = 'Mark current image as valid/invalid'
    GUI_INVALID_PIC_TIP                           = 'Invalid picture'
    GUI_MARK_ALL_ANNOTATIONS_AS_CONFIRMED_TIP     = 'Mark all annotations in image as confirmed'
    GUI_CRITIAL_ERROR_TEXT                        = "Critical Error"
    GUI_ERROR_TEXT                                = "Error"   
    GUI_TIP_TEXT                                  = "Tip"
    GUI_INVALID_PATH_TEXT                         = "{} is not a valid path! Please check it beforing using this tool!"
    GUI_CREATE_JSON_FILE_SUCCESS_TEXT             = "Number of Images in {}: {}\nJSON File is saved to {}\nPlease open this file via this GUI or run below command later to start annotating:\npython slothx.py '{}' \n"
    GUI_SUCCESS_TEXT                              = "Congratulation"
    GUI_MERGE_JSON_FILE_DIALOG_MERGE_SUCCESS_TEXT = "{} Json files have been merged successfully!\nPlease check merged json file: {}!\n"
    GUI_CLEAN_DUPLICATE_DATA_IN_JSON_FILE_DIALOG_SUCCESS_TEXT = "{} Json file has been cleaned successfully!\nPlease check cleaned json file: {}!\n"
    GUI_CLEAR_OBJ_VIEW_FILTER_TIP                 = 'Clear objViewFilter'
    GUI_LOAD_JSON_FILE_FAIL_MESSAGE               = "Error: Loading annotation file failed ({})"
    

    GUI_SAVE_IMAGE_SUCCESS_TEXT                   = "Current view content has been saved to {} file succesfully!"
    GUI_BEGIN_PROCESS_IMAGES_TEXT                 = "Now begin to process for {} images! \nIt maybe takes a while, \nPlease wait a moment ..."
    GUI_END_PROCESS_IMAGES_TEXT                   = "{} images have been processed succesfully! \nPlease check {} folder for result!"

    GUI_IMAGE_TEXT                                = u'Image'
                                                      
    GUI_EDIT_MODE_DISPLAY_TEXT                    = 'EditMode'
    GUI_INSERT_MODE_DISPLAY_TEXT                  = 'InsertMode'

    GUI_AUTO_CONNECT_MODE_DISPLAY_TEXT            = 'AutoConnectMode'
    GUI_MANNUAL_CONNECT_MODE_DISPLAY_TEXT         = 'ManualConnectMode'
                                                  
    GUI_MERGE_JSON_FILE_DIALOG_SRC_FILE_TITLE     = "{} - Please specify multiple JSON Files for merging (more than one json files)"
    GUI_MERGE_JSON_FILE_DIALOG_DST_FILE_TITLE     = "{} - Please specify JSON file name after merging to save"
    GUI_CLEAN_DUPLICATE_DATA_IN_JSON_FILE_DIALOG_DST_FILE_TITLE     = "{} - Please specify JSON file name after processing to save"
    GUI_CLEAN_DUPLICATE_DATA_IN_JSON_FILE_DIALOG_TITLE     = "{} - Please specify JSON file to clean"
    GUI_OPEN_IMG_FILE_DIALOG_TITLE                = "{} - Add Image Files"
    GUI_JSON_FILE_TYPE_TEXT                       = "json file ({})"
    GUI_OPEN_IMG_FILE_DIALOG_FILE_TYPE_TEXT       = "Image files ({})"
    GUI_OPEN_VIDEO_FILE_DIALOG_TITLE              = "{} - Add Video File"
    GUI_OPEN_VIDEO_FILE_DIALOG_FILE_TYPE_TEXT     = "Video files ({})"
    GUI_IMPORT_VIDEO_TIP                          = u"Importing frames from video '{}'. This may take a while... frmInterval = {}"
    GUI_IMPORT_VIDEO_SUCCESS_TIP                  = u"Importing frames from video '{}' succeed!"
    GUI_IMPORT_VIDEO_FAILURE_TIP                  = u"Importing frames from video '{}' fail!"
    GUI_VIDEO_GET_IMAGE_FAILURE_TIP               = u"Reading frame {} from video '{}' fail!"
    GUI_IMPORT_VIDEO_FAILURE_FOR_HAS_ALREADY_ADDED_TIP = u"Media file '{}' has already been added ever!"
    GUI_LOAD_ANNOTATON_FILE_SUCCESS_TIP           = u"Successfully loaded {} ({} files, {} annotations)"
    GUI_SAVE_ANNOTATON_FILE_SUCCESS_TIP           = u"Successfully saved {} ({} files, {} annotations)" 
    GUI_AUTOSAVE_ANNOTATON_FILE_SUCCESS_TIP       = u"Successfully auto saved {} ({} files, {} annotations) @ {}" 
    GUI_BACKGROUND_LOADING_ANNOTATION_MODEL_TIP   = u"Background loading finished"

    GUI_SAVE_ANNOTATION_FILE_FAIL_TIP             = u"Error: Saving {} failed ({})"
    GUI_AUTO_SAVE_ANNOTATION_FILE_FAILE_TIP       = u"Error: Automatically Saving {} failed ({})"

    GUI_PEDESTRAIN_BUTTON_TIP                     = ("Press '" +  GUI_PEDESTRAIN_BUTTON_HOTKEY + u"' to start Pedestrain Annotation")
    GUI_UPPER_BODY_BUTTON_TIP                     = ("Press '" +  GUI_UPPER_BODY_BUTTON_HOTKEY + u"' to start UpperBody Annotation" )
    GUI_LOWER_BODY_BUTTON_TIP                     = ("Press '" +  GUI_LOWER_BODY_BUTTON_HOTKEY + u"' to start LowerBody Annotation" )
    GUI_PERSONBIKE_BUTTON_TIP                     = ("Press '" +  GUI_PERSONBIKE_BUTTON_HOTKEY + u"' to start PersonBike Annotation")
    GUI_INSERT_PERSONBIKE_TYPE_OF_LIGHT_MOTOR_TIP = (u"Begin to insert personbike - lightMotor annotation      ") 
    GUI_INSERT_PERSONBIKE_TYPE_OF_MOTOR_TIP       = (u"Begin to insert personbike - motor annotation           ")
    GUI_INSERT_PERSONBIKE_TYPE_OF_BICYCLE_TIP     = (u"Begin to insert personbike - bicycle annotation         ")
    GUI_INSERT_PERSONBIKE_TYPE_OF_THREE_WHEEL_TIP = (u"Begin to insert personbike - threeWheel annotation      ") 
    GUI_INSERT_PERSONBIKE_TYPE_OF_UNKNOWN_TIP     = (u"Begin to insert personbike - unknown annotation         ")
    GUI_VEHICLE_BUTTON_TIP                        = ("Press '" +  GUI_VEHICLE_BUTTON_HOTKEY    + u"' to start Vehicle Annotation"   )
    GUI_IGNORE_BUTTON_TIP                         = ("Press '" +  GUI_IGNORE_BUTTON_HOTKEY     + u"' to start Pedestrain Annotation")
    GUI_HEAD_BUTTON_TIP                           = ("Press '" +  GUI_HEAD_BUTTON_HOTKEY       + u"' to start Head Annotation"      )
    GUI_FACE_BUTTON_TIP                           = ("Press '" +  GUI_FACE_BUTTON_HOTKEY       + u"' to start FAce Annotation"      )
    GUI_HELMET_BUTTON_TIP                         = ("Press '" +  GUI_HELMET_BUTTON_HOTKEY     + u"' to start helmet Annotation"    )  
    GUI_PERSONBIKE_LICENSE_PLATE_BUTTON_TIP       = ("Press '" +  GUI_PERSONBIKE_LICENSE_PLATE_HOTKEY     + u"' to start personbike's licenseplate Annotation"    )  
    GUI_VEHICLE_LICENSE_PLATE_BUTTON_TIP          = ("Press '" +  GUI_VEHICLE_LICENSE_PLATE_HOTKEY     + u"' to start vehicle's licenseplate Annotation"    )  
    GUI_UMBRELLA_BUTTON_TIP                       = (u"Begin to insert umbrella annotation                     Shortcut" + GUI_UMBRELLA_BUTTON_HOTKEY      ) 
    GUI_BACKPACK_BUTTON_TIP                       = (u"Begin to insert backpack annotation                     Shortcut" + GUI_BACKPACK_BUTTON_HOTKEY      ) 
    GUI_CARRYINGBAG_BUTTON_TIP                    = (u"Begin to insert carryingbag annotation                  Shortcut" + GUI_CARRYINGBAG_BUTTON_HOTKEY      ) 
    GUI_GLASSES_BUTTON_TIP                        = (u"Begin to insert glasses annotation                      Shortcut" + GUI_GLASSES_BUTTON_HOTKEY      ) 
    GUI_HAT_BUTTON_TIP                            = (u"Begin to insert hat annotation                          Shortcut" + GUI_HAT_BUTTON_HOTKEY      ) 
    GUI_MASK_BUTTON_TIP                           = (u"Begin to insert mask annotation                         Shortcut" + GUI_MASK_BUTTON_HOTKEY      ) 
    GUI_LUGGAGE_BUTTON_TIP                        = (u"Begin to insert luggage annotation                      Shortcut" + GUI_LUGGAGE_BUTTON_HOTKEY      ) 


    GUI_SELECTED_TIP                              = "Selected"
    GUI_INSERT_ANNOTATION_NOT_ALLOWED_TIP         = "Error: {} cannot be attched to {} annotation!"
    GUI_INSERT_ANNOTATION_NOT_ALLOWED_TIP2        = "Error: {} must be attched to {} annotation! But current annotation is a {}!"
    GUI_INSERT_ANNOTATION_NOT_IN_BOUNDARY_TIP     = "Error: {} must be in boundary of {} annotation!"
    GUI_INSERT_ANNOTATION_EXCEED_ALLOWED_NUM_TIP  = "Error: {} annotation can have only {} {} child annotations! Now there are already {} {} child annotations!"
    GUI_INSERT_ANNOTATION_NO_PARENT_TIP           = "Error: cannot find appropriate parent annotation for {} annotation to insert!"
                                          
    GUI_OBJ_TEXT                                  = "Object"
    GUI_CONCATINATION_TEXT                        = u" or "
    LAST_OR_FIRST_IMAGE_TIP                       = u"Current image has been json file 's {} image!"
    LAST_OR_FIRST_FRAME_TIP                       = u"Current frame has been video {} 's {} frame!"
    LAST_OR_FIRST_FRAME_OR_IMAGE_TIP              = u"Current image has been the {} image!"
    
    NO_MORE_OBJ_TIP                               = u"No more object!"
    LAST_OR_FIRST_OBJ_IN_IMAGE_TIP                = u"Current object has been the {} object in all images in current json file!"
    LAST_OR_FIRST_OBJ_IN_FRAME_TIP                = u"Current object has been the {} object in all frames in current video {}!"
    LAST_TIP                                      = u"last"
    FIRST_TIP                                     = u"first"
    MANNUAL_CONNECT_COMMAND_NOT_ALLOWED_IN_OBJ_VIEW_MODE_TIP = "MannualConnectMode is not allowed in object view mode!"  
    IMG_VIEW_MODE_DISPLAY_TEXT                    = u"ImgViewMode"
    OBJ_VIEW_MODE_DISPLAY_TEXT                    = u"ObjViewMode"
    GUI_CANNOT_ADD_MORE_THAN_ONE_VIDEO_FILES_TEXT = u'Only one video file is allowed in current json file!'
    GUI_ONE_VIDEO_FILE_OR_MULTIPLE_IMG_FILES_IS_ALLOWED_TEXT = u'json file can have only one video file or multiple image files!'
    GUI_MEDIA_FILE_DONT_EXIST_TEXT                = u'This file {} does not exist!'
    GUI_PLS_SPECIFY_MORE_THAN_ONE_JSON_FILES_TEXT = u'Please specify more than one json file to merge!'
    GUI_INVALID_FOLDER_PATH_TEXT                  = u'Invalid folder path'
                                   
    APP_NAME                                      = "Video Structureing Annotation Tool"
    ORGANIZATION_NAME                             = "HongKong JiuLing"
    
    LEFT_EYE_OUTER_CORNER_DISPLAYTEXT             = "left eye outer corner"
    LEFT_EYE_INNER_CORNER_DISPLAYTEXT             = "left eye inner corner"
    RIGHT_EYE_INNER_CORNER_DISPLAYTEXT            = "right eye inner corner"
    RIGHT_EYE_OUTER_CORNER_DISPLAYTEXT            = "right eye outer corner"
    NOSE_TIP_DISPLAYTEXT                          = "nose tip"
    UPPER_LIP_CENTER_DISPLAYTEXT                  = "upper lip center"
    LEFT_EYE_CENTER_DISPLAYTEXT                   = "left eye center"
    RIGHT_EYE_CENTER_DISPLAYTEXT                  = "right eye center"
    LEFT_MOUTH_CORNER_DISPLAYTEXT                 = "left mouth corner"
    RIGHT_MOUTH_DISPLAYTEXT                       = "right mouth corner"
    
    STATISTIC_OR_APPLY_OBJVIEWFILTER_FOR_CUR_JSON_FILE_PLUGIN_DISPLAYTEXT       = "Statistic for current JSON file/Apply objViewFilter for current JSON file"
    STATISTIC_FOR_MULTIPLE_JSON_FILES_PLUGIN_DISPLAYTEXT = "Statistic for specific folder"
    CREATE_JSON_FILE_FOR_SPECIFIC_IMG_FOLDER_PLUGIN_DISPLAYTEXT = "Create annotation file for specific image folder"
    MERGE_MULTIPLE_JSON_FILES_PLUGIN_DISPLAYTEXT         = "Merge multiple JSON files"
    CLEAN_DUPLICATE_DATA_IN_JSON_FILE_PLUGIN_DISPLAYTEXT = "Clean duplicate data in JSON file"
    SPLIT_TO_MULTIPLE_JSON_FILES_PLUGIN_DISPLAYTEXT      = "Split one json file to multiple json files per which contains at most 100 image files"
    
    STARTUP_TIPS_DIALOG_DISPLAYTEXT               = "Tips:\n\n1. Vehicle color has been updated from this version!\n     - Silver has been renamed with Gray(Silver)\n     - Golden and Orange have been removed!\n\n2. Pedestrain/HumanRiding's angle has been updated from this version!\n     - Now only Front, back(also named as rear), side and undecided are supported!\n"
    STARTUP_TIPS_DIALOG_TITLE                     = "Startup Tips"
    
    
    GUI_ADD_ONE_MORE_VERTEX_MESSAGE               = u"Move and press mouse left button to add one more vertex."
                                             
else:                                             
                                                  
    GUI_PEDESTRAIN_WIDGET_DISPLAYTEXT             = u'行人'
    GUI_PERSONBIKE_WIDGET_DISPLAYTEXT             = u'人骑车'
    GUI_VEHICLE_WIDGET_DISPLAYTEXT                = u'车'
    GUI_IGNORE_WIDGET_DISPLAYTEXT                 = u'忽略区域'
    GUI_HEAD_WIDGET_DISPLAYTEXT                   = u'头'
                                                          
    GUI_UPPERBODY_WIDGET_DISPLAYTEXT              = u'上身' 
    GUI_LOWERBODY_WIDGET_DISPLAYTEXT              = u'下身'
    GUI_HELMET_WIDGET_DISPLAYTEXT                 = u'头盔'
    GUI_LICENSE_PLATE_WIDGET_DISPLAYTEXT          = u'车牌'
    GUI_PLATE_WIDGET_DISPLAYTEXT                  = u'牌子'
    GUI_OBJTYPE_WIDGET_DISPLAYTEXT                = u'物体'
    GUI_PLATE_TYPE_GROUP_WIDGET_DISPLAYTEXT       = u'牌子类型'
    GUI_OBJTYPE_GROUP_WIDGET_DISPLAYTEXT          = u'物体类别'
    GUI_LICENSE_PLATE_WIDGET_DISPLAYTEXT          = u'车牌'
    GUI_BILLBOARD_WIDGET_DISPLAYTEXT              = u'广告牌'    
    GUI_UMBRELLA_WIDGET_DISPLAYTEXT               = u'伞' 
    GUI_BACKPACK_WIDGET_DISPLAYTEXT               = u'背包' 
    GUI_CARRYINGBAG_WIDGET_DISPLAYTEXT            = u'手拎物'
    GUI_HAT_WIDGET_DISPLAYTEXT                    = u'帽' 
    GUI_GLASSES_WIDGET_DISPLAYTEXT                = u'眼镜' 
    GUI_MASK_WIDGET_DISPLAYTEXT                   = u'口罩' 
    GUI_LUGGAGE_WIDGET_DISPLAYTEXT                = u'拉杆箱'
    GUI_FACE_WIDGET_DISPLAYTEXT                   = u'脸'
    GUI_HEAD_WIDGET_DISPLAYTEXT                   = u'头'
    GUI_LEFT_EYE_CENTER_WIDGET_DISPLAYTEXT        = u'左眼中心'
    GUI_RIGHT_EYE_CENTER_WIDGET_DISPLAYTEXT       = u'右眼中心'
    GUI_NOSE_TIP_WIDGET_DISPLAYTEXT               = u'鼻尖'
    GUI_LEFT_MOUTH_CORNER_WIDGET_DISPLAYTEXT      = u'左嘴角'
    GUI_RIGHT_MOUTH_CORNER_WIDGET_DISPLAYTEXT     = u'右嘴角'
    GUI_FACE5POINTS_WIDGET_DISPLAYTEXT             = u'脸部5点'
     
    GUI_GENDER_WIDGET_DISPLAYTEXT                 = u'性别'
    GUI_AGE_WIDGET_DISPLAYTEXT                    = u'年龄'
    GUI_ANGLE_WIDGET_DISPLAYTEXT                  = u'角度'
    GUI_VEHICLE_ANGLE_WIDGET_DISPLAYTEXT          = u'车辆角度'
    GUI_HAIR_STYLE_WIDGET_DISPLAYTEXT             = u'发型'                                                 

    GUI_VEHICLE_COLOR_WIDGET_DISPLAYTEXT          = u'车辆颜色'
    GUI_PERSONBIKE_TYPE_WIDGET_DISPLAYTEXT        = u'人骑车类型'
    TAG_PERSONBIKE_TYPE_OF_THREE_WHEEL_DISPLAYTEXT= u'三轮'
    TAG_PERSONBIKE_TYPE_OF_UNKNOWN_DISPLAYTEXT    = u'未知二轮'
    GUI_PERSONBIKE_TYPE_GROUP_WIDGET_DISPLAYTEXT  = u'人骑车类型'
    TAG_PERSONBIKE_TYPE_OF_BICYCLE_DISPLAYTEXT    = u'自行车'    
    TAG_PERSONBIKE_TYPE_OF_LIGHTMOTOR_DISPLAYTEXT = u'轻便摩托'  
    TAG_PERSONBIKE_TYPE_OF_MOTOR_DISPLAYTEXT      = u'摩托'  
    
    GUI_VEHICLE_LICENSE_PLATE_WIDGET_DISPLAYTEXT  = u'车牌'
     
    TAG_VEHICLE_TYPE_OF_SEDAN_DISPLAYTEXT         = u'小轿车'
    TAG_VEHICLE_TYPE_OF_SUV_DISPLAYTEXT           = u'SUV/MPV/越野'
    TAG_VEHICLE_TYPE_OF_MINIBUS_DISPLAYTEXT       = u'面包车'
    TAG_VEHICLE_TYPE_OF_LARGE_COACH_DISPLAYTEXT      = u'大型客车'
    TAG_VEHICLE_TYPE_OF_MEDIUM_COACH_DISPLAYTEXT     = u'中型客车'
    TAG_VEHICLE_TYPE_OF_HEAVY_VAN_DISPLAYTEXT        = u'中重型货车'
    TAG_VEHICLE_TYPE_OF_LIGHT_VAN_DISPLAYTEXT        = u'轻型货车'
    TAG_VEHICLE_TYPE_OF_TRUCK_DISPLAYTEXT            = u'卡车'
    TAG_VEHICLE_TYPE_OF_ENGINEERING_TRUCK_DISPLAYTEXT= u'工程车'
    GUI_VEHICLE_TYPE_GROUP_WIDGET_DISPLAYTEXT        = u'车辆类型'

     
    TAG_UNSET_DISPLAYTEXT                         = u'未设置' 
    TAG_VEHICLE_TYPE_OF_UNKNOWN_DISPLAYTEXT       = u'未知'     
    TAG_VEHICLE_COLOR_OF_UNKNOWN_DISPLAYTEXT      = u'未知'     

                                                  
    GUI_ANNOTATION_MODEL_HEAD_COL0_DISPLAYTEXT    = u"文件/标签/键"
    GUI_ANNOTATION_MODEL_HEAD_COL1_DISPLAYTEXT    = u"值"
                                                  
    GUI_SET_VIDEO_FRME_INTERVAL_DIALOG_TITLE      = u"设置视频帧间隔"
    GUI_SET_VIDEO_FRME_INTERVAL_DIALOG_TEXT       = u"请设置视频帧间隔。如：设置为25, 表示每25帧取1帧以查看并标注"
                                                  
    GUI_OK_DISPLAYTEXT                            = u"确认"
    GUI_SPECIFY_VIDEO_FILE_TIP                    = u"请指定合法的视频文件!"  
                                                  
                                                  
    GUI_BUTTONGROUP1_DISPLAYTEXT                  = u"物体-类别标定面板"              
    GUI_BUTTONGROUP2_DISPLAYTEXT                  = u"人-躯体标定面板"
    GUI_BUTTONGROUP3_DISPLAYTEXT                  = u"人-携带物标面板"
    GUI_BUTTONGROUP4_DISPLAYTEXT                  = u"人-服饰标定面板"
    GUI_BUTTONGROUP5_DISPLAYTEXT                  = u"人-细节标定面板"
    GUI_BUTTONGROUP6_DISPLAYTEXT                  = u"车辆-细节标定面板"
    GUI_PERSONBIKE_PANEL_DISPLAYTEXT              = u"人骑车-细类标定面板" 
    GUI_PERSONBIKE_BBOXS_DISPLAYTEXT              = u"细类位置"
    GUI_OBJTYPE_GROUP_DISPLAYTEXT                 = u"物体位置"
    GUI_VEHICLE_BBOXS_DISPLAYTEXT                 = u"位置"
    GUI_OBJINFO_PANNEL_DISPLAYTEXT                = u"物体信息"
                                                  
    GUI_ANNOTATION_DISPLAYTEXT                    = u"标签信息面板"
    GUI_MORE_WIDGET_DISPLAYTEXT                   = u"更多"
                                                  
    GUI_MENU_PLUGIN_DISPLAYTEXT                   = u"插件"
    GUI_MENU_SHORTCUT_DISPLAYTEXT                 = u"快捷键"
    GUI_MENU_OPTION_DISPLAYTEXT                   = u"选项"
    GUI_MENU_FILE_DISPLAYTEXT                     = u"文件"
    GUI_MENU_EDIT_DISPLAYTEXT                     = u"编辑"
    GUI_MENU_VIEW_DISPLAYTEXT                     = u"视图"
    GUI_MENU_HELP_DISPLAYTEXT                     = u"帮助"
    GUI_MENU_NET_DISPLAYTEXT                     = u"联网"
                                                  
    GUI_MENU_EDIT_ACTION_ADD_IMG_DISPLAYTEXT      = u"增加图片"
    GUI_MENU_EDIT_ACTION_ADD_VIDEO_DISPLAYTEXT    = u"增加视频"
    GUI_MENU_FILE_ACTION_NEW_DISPLAYTEXT          = u"新建"
    GUI_MENU_FILE_ACTION_OPEN_DISPLAYTEXT         = u"打开标注文件"
    GUI_MENU_FILE_ACTION_SAVE_DISPLAYTEXT         = u"保存标注文件"
    GUI_MENU_FILE_ACTION_SAVEAS_DISPLAYTEXT       = u"另存标注文件为..."
    GUI_MENU_FILE_ACTION_EXIT_DISPLAYTEXT         = u"退出"
    GUI_MENU_VIEW_ACTION_LOCKED                   = u"锁定标定面板"
    GUI_MENU_OPTION_ACTION_FITTOWIN_DISPLAYTEXT   = u"图片缩放为窗口区域"
    GUI_MENU_HELP_ACTION_ABOUT_DISPLAYTEXT        = u"关于"
    GUI_MENU_HELP_ACTION_IMPORTNET_DISPLAYTEXT    = u"导入标注平台"
                                                  
    GUI_ABOUT_DIALOG_TITLE                        = u"关于%s"                          
    GUI_ABOUT_DIALOG_TEXT                         = u"""<b>%s</b><p>版本 %s<p>              
                 <p>本工具原型由KIT的CVHCI研究小组开发.
                 香港久凌基于此针对视频结构化的标注需求做特别开发.                    
                 <p>如对视频结构化产品感兴趣, 请戳这里: <a href="%s">%s</a>"""

    GUI_SAVE_CHANGE_MSGBOX_TITLE_TEXT             = u"%s - 未存的改变"      
    GUI_SAVE_CHANGE_MSGBOX_QUESTION_TEXT          = u"保存改变？"      
    GUI_SAVE_ANNOTATIONS_DIALOG_TITLE_TEXT        = u"%s - 保存标签文件"
    GUI_SAVE_ANNOTATIONS_DIALOG_SAVETYPE_TEXT     = u"标签文件 (%s)"
    GUI_OPEN_ANNOTATIONS_DIALOG_TITLE_TEXT        = u"%s - 打开标签文件"
    GUI_OPEN_ANNOTATIONS_DIALOG_OPENTYPE_TEXT     = u"标签文件 (%s)"
    
    GUI_UNAMED_ANNOTATION_TEXT                    = u"未命名的标签文件"
    
    GUI_CONFIRMALL_N_GOTONEXT_TIP                 = u'确认当前图片标注并打开下一个图片'
    GUI_PREV_IMG_TIP                              = u'上一个图片/帧/物体' 
    GUI_NEXT_IMG_TIP                              = u'下一个图片/帧/物体'
    GUI_GOTO_BEGIN_TIP                            = u'第一个图片/帧/物体' 
    GUI_GOTO_END_TIP                              = u'最后一个图片/帧/物体' 
    GUI_TOGGLE_DISPLAY_VIEW_TIP                   = u'切换显示视图'         
    GUI_ENABLE_AUTO_CONNECT_LABELS_TIP            = u'允许自动关联标签(上身/下身=>人/骑车人; 车=>/骑车人)'
    GUI_DISABLE_AUTO_CONNECT_LABELS_TIP           = u'禁止自动关联标签(上身/下身=>人/骑车人; 车=>/骑车人)'
    GUI_NEXT_ANNOTATION_TIP                       = u'下一个标注'                    
    GUI_PREV_ANNOTATION_TIP                       = u'上一个标注'
    GUI_FIT_CUR_IMG_INTO_WIN_TIP                  = u'缩放图片适应当前窗口大小'     
    GUI_DEL_SELECTED_ANNOTATIONS_TIP              = u'删除选中的所有标注'             
    GUI_EXIT_INSERT_MODE                          = u'退出插入模式'   
    GUI_SAVE_CUR_VIEW_IMG_CONTENT_TO_FILE_TIP     = u'保存当前画面内容到BMP文件'  
    GUI_SAVE_ALL_IMGS_VIEW_CONTENT_TO_FILES_TIP   = u'保存当前标注文件中所有画面内容到系列BMP文件中'              
    GUI_MARK_CUR_IMG_AS_LABELED_TIP               = u'设置当前图片为有效样本' 
    GUI_MARK_CUR_IMG_AS_UNLABELED_TIP             = u'设置当前图片为无效样本' 
    GUI_FILP_CUR_IMG_LABELED_TIP                  = u'设置当前图片为无效/有效样本' 
    GUI_INVALID_PIC_TIP                           = u'无效样本'
    GUI_MARK_ALL_ANNOTATIONS_AS_CONFIRMED_TIP     = u'确认当前图片标注'
    GUI_CRITIAL_ERROR_TEXT                        = u"致命错误"
    GUI_ERROR_TEXT                                = u"错误"
    GUI_TIP_TEXT                                  = u"提示"
    GUI_INVALID_PATH_TEXT                         = u"{} 不是一个合法路径! 程序拒绝继续执行!"
    GUI_CREATE_JSON_FILE_SUCCESS_TEXT             = u"在{}目录下共找到{}个图片文件! \n标签文件保存为{}!\n请在该工具界面中打开这个标注文件以开始标注!\n或者也可以透过过以下命令以开始标注:\npython slothx.py '{}'\n"
    GUI_SUCCESS_TEXT                              = u"恭喜!"
    GUI_MERGE_JSON_FILE_DIALOG_MERGE_SUCCESS_TEXT = u"已成功合并{}个Json文件!\n合并后的json文件存放在{}!\n"
    GUI_CLEAN_DUPLICATE_DATA_IN_JSON_FILE_DIALOG_SUCCESS_TEXT = u"{} Json file已被成功处理!\n处理后的json文件存放在{}!\n"
    GUI_CLEAR_OBJ_VIEW_FILTER_TIP                 = u'清除对象查看filter'
    GUI_LOAD_JSON_FILE_FAIL_MESSAGE               = u"打开json文件失败! 请检查文件格式或者文件保存格式是否正确! ({})"

    GUI_BEGIN_PROCESS_IMAGES_TEXT                 = u"准备开始处理{}张图片/帧!\n这将花费一定时间，请耐心等待..."
    GUI_END_PROCESS_IMAGES_TEXT                   = u"谢谢您的耐心等待！\n共{}张图片/帧已成功处理!\n请检查{}目录以查看结果!"
    GUI_SAVE_IMAGE_SUCCESS_TEXT                   = u"当前画面已经被截图保存到{}文件!"
    
    GUI_IMAGE_TEXT                                = u'图像'

    GUI_EDIT_MODE_DISPLAY_TEXT                    = u'编辑模式'
    GUI_INSERT_MODE_DISPLAY_TEXT                  = u'插入模式'
 
    GUI_AUTO_CONNECT_MODE_DISPLAY_TEXT            = u'自动关联模式'
    GUI_MANNUAL_CONNECT_MODE_DISPLAY_TEXT         = u'手工关联模式'

    GUI_MERGE_JSON_FILE_DIALOG_SRC_FILE_TITLE     = u"{} - 请指定待合并的JSON文件(两个或两个以上)"
    GUI_MERGE_JSON_FILE_DIALOG_DST_FILE_TITLE     = u"{} - 请指定合并后的JSON文件"
    GUI_CLEAN_DUPLICATE_DATA_IN_JSON_FILE_DIALOG_DST_FILE_TITLE     = u"{} - 请指定处理后的JSON文件"
    GUI_CLEAN_DUPLICATE_DATA_IN_JSON_FILE_DIALOG_TITLE     = u"{} - 请指定需要处理的JSON文件"
    GUI_OPEN_IMG_FILE_DIALOG_TITLE                = u"{} - 增加图片文件"
    GUI_JSON_FILE_TYPE_TEXT                       = u"json文件({})"
    GUI_OPEN_IMG_FILE_DIALOG_FILE_TYPE_TEXT       = u"图片({})"
    GUI_OPEN_VIDEO_FILE_DIALOG_TITLE              = u"{} - 增加视频文件"
    GUI_OPEN_VIDEO_FILE_DIALOG_FILE_TYPE_TEXT     = u"视频({})"
    GUI_IMPORT_VIDEO_TIP                          = u"正在载入视频 '{}'. 请耐心等待！载入帧间隔 = {}"
    GUI_IMPORT_VIDEO_SUCCESS_TIP                  = u"载入视频/图片 '{}'成功!"
    GUI_IMPORT_VIDEO_FAILURE_FOR_HAS_ALREADY_ADDED_TIP = u"视频/图片 '{}'之前已经被载入过!"
    GUI_IMPORT_VIDEO_FAILURE_TIP                  = u"载入视频/图片 '{}'失败!"
    GUI_VIDEO_GET_IMAGE_FAILURE_TIP               = u"读取第{}帧(视频'{}')失败!"
    GUI_LOAD_ANNOTATON_FILE_SUCCESS_TIP           = u"成功载入 {} ({} files, {} 标签)"
    GUI_SAVE_ANNOTATON_FILE_SUCCESS_TIP           = u"成功保存 {} ({} files, {} 标签)" 
    GUI_AUTOSAVE_ANNOTATON_FILE_SUCCESS_TIP       = u"成功自动保存 {} ({} files, {} 标签) @ {}" 
    GUI_BACKGROUND_LOADING_ANNOTATION_MODEL_TIP   = u"模型后台载入完成"


    GUI_SAVE_ANNOTATION_FILE_FAIL_TIP             = u"错误：保存 {} 失败! ({})"
    GUI_AUTO_SAVE_ANNOTATION_FILE_FAILE_TIP       = u"错误：自动保存 {} 失败! ({})"

    GUI_PEDESTRAIN_BUTTON_TIP                     = (u"进入'行人'标签插入模式                                    快捷键" + GUI_PEDESTRAIN_BUTTON_HOTKEY)
    GUI_UPPER_BODY_BUTTON_TIP                     = (u"进入'人-上身'标签插入模式                               快捷键" + GUI_UPPER_BODY_BUTTON_HOTKEY)
    GUI_LOWER_BODY_BUTTON_TIP                     = (u"进入'人-下身'标签插入模式                               快捷键" + GUI_LOWER_BODY_BUTTON_HOTKEY)
    GUI_PERSONBIKE_BUTTON_TIP                     = (u"进入'骑车人'标签插入模式                                快捷键" + GUI_PERSONBIKE_BUTTON_HOTKEY)
    GUI_INSERT_PERSONBIKE_TYPE_OF_LIGHT_MOTOR_TIP = (u"进入'骑车人-电动/轻便摩托'标签插入模式                              快捷键" + GUI_INSERT_PERSONBIKE_TYPE_OF_LIGHT_MOTOR_HOTKEY) 
    GUI_INSERT_PERSONBIKE_TYPE_OF_MOTOR_TIP       = (u"进入'骑车人-摩托'标签插入模式                           快捷键" + GUI_INSERT_PERSONBIKE_TYPE_OF_MOTOR_HOTKEY) 
    GUI_INSERT_PERSONBIKE_TYPE_OF_THREE_WHEEL_TIP = (u"进入'骑车人-三轮'标签插入模式                           快捷键" + GUI_INSERT_PERSONBIKE_TYPE_OF_THREE_WHEEL_HOTKEY) 
    GUI_INSERT_PERSONBIKE_TYPE_OF_UNKNOWN_TIP     = (u"进入'骑车人-未知二轮'标签插入模式                           快捷键" + GUI_INSERT_PERSONBIKE_TYPE_OF_UNKNOWN_HOTKEY) 
    GUI_INSERT_PERSONBIKE_TYPE_OF_BICYCLE_TIP     = (u"进入'骑车人-自行车'标签插入模式                           快捷键" + GUI_INSERT_PERSONBIKE_TYPE_OF_BICYCLE_HOTKEY)
    GUI_VEHICLE_BUTTON_TIP                        = (u"进入'车'标签插入模式                                      快捷键" + GUI_VEHICLE_BUTTON_HOTKEY   )
    GUI_IGNORE_BUTTON_TIP                         = (u"进入'忽略区域'标签插入模式                           快捷键" + GUI_IGNORE_BUTTON_HOTKEY    )
    GUI_HEAD_BUTTON_TIP                           = (u"进入'人-头'标签插入模式                                 快捷键 " + GUI_HEAD_BUTTON_HOTKEY      ) 

    GUI_FACE_BUTTON_TIP                           = (u"进入'人脸'标签插入模式                                  快捷键 " + GUI_FACE_BUTTON_HOTKEY      ) 
    GUI_HELMET_BUTTON_TIP                         = (u"进入'骑车人-头盔'标签插入模式                          快捷键 " + GUI_HELMET_BUTTON_HOTKEY      ) 
    GUI_PERSONBIKE_LICENSE_PLATE_BUTTON_TIP       = (u"进入'骑车人-车牌'标签插入模式                          快捷键 " + GUI_PERSONBIKE_LICENSE_PLATE_HOTKEY      )
    GUI_VEHICLE_LICENSE_PLATE_BUTTON_TIP          = (u"进入'车-车牌'标签插入模式                          快捷键 " + GUI_VEHICLE_LICENSE_PLATE_HOTKEY      )
    GUI_UMBRELLA_BUTTON_TIP                       = (u"进入'雨伞'标签插入模式                                 快捷键 " + GUI_UMBRELLA_BUTTON_HOTKEY      ) 
    GUI_BACKPACK_BUTTON_TIP                       = (u"进入'双肩背包'标签插入模式                           快捷键 " + GUI_BACKPACK_BUTTON_HOTKEY      ) 
    GUI_CARRYINGBAG_BUTTON_TIP                    = (u"进入'手拎物'标签插入模式                              快捷键 " + GUI_CARRYINGBAG_BUTTON_HOTKEY      ) 
    GUI_GLASSES_BUTTON_TIP                        = (u"进入'眼镜'标签插入模式                                 快捷键 " + GUI_GLASSES_BUTTON_HOTKEY      ) 
    GUI_HAT_BUTTON_TIP                            = (u"进入'帽子'标签插入模式                                 快捷键 " + GUI_HAT_BUTTON_HOTKEY      ) 
    GUI_MASK_BUTTON_TIP                           = (u"进入'口罩'标签插入模式                                 快捷键 " + GUI_MASK_BUTTON_HOTKEY      ) 
    GUI_LUGGAGE_BUTTON_TIP                        = (u"进入'行李'标签插入模式                                 快捷键 " + GUI_LUGGAGE_BUTTON_HOTKEY      ) 
    
        
    GUI_SELECTED_TIP                              = u"选中"
    GUI_INSERT_ANNOTATION_NOT_ALLOWED_TIP         = u"错误: \n'{}'不允许被添加到'{}'标注下! \n你无法添加这个标注!\n"
    GUI_INSERT_ANNOTATION_NOT_ALLOWED_TIP2        = u"错误: \n'{}'必须添加到{}标注下!\n但你当前添加的对象是一个'{}'标注!"
    GUI_INSERT_ANNOTATION_NOT_IN_BOUNDARY_TIP     = u"错误: \n'{}'位置必须落在'{}'位置以内!\n你无法添加这个标注！\n"
    GUI_INSERT_ANNOTATION_EXCEED_ALLOWED_NUM_TIP  = u"错误: \n'{}'下最多只允许有{}个{}标注!\n而现在已经有{}个{}标注了！\n"
    GUI_INSERT_ANNOTATION_NO_PARENT_TIP           = u"错误: \n无法为当前待插入的{}标注找到合适的父节点! \n你无法添加这个标注!"
    
    GUI_OBJ_TEXT                                  = u"物体"
    GUI_CONCATINATION_TEXT                        = u" 或 "
    LAST_OR_FIRST_IMAGE_TIP                       = u"当前图片已是标注文件的{}图片了!"
    LAST_OR_FIRST_FRAME_TIP                       = u"当前帧已是视频文件{}的{}帧了!"
    LAST_OR_FIRST_FRAME_OR_IMAGE_TIP              = u"当前帧已是{}帧了!"
        
    NO_MORE_OBJ_TIP                               = u"没有更多的物体可显示!"
    LAST_OR_FIRST_OBJ_IN_IMAGE_TIP                = u"Current object has been the {} object in all images in current json file!"
    LAST_OR_FIRST_OBJ_IN_FRAME_TIP                = u"Current object has been the {} object in all frames in current video {}!"
    LAST_TIP                                      = u"最后"
    FIRST_TIP                                     = u"最前"
    MANNUAL_CONNECT_COMMAND_NOT_ALLOWED_IN_OBJ_VIEW_MODE_TIP =  u"对象查看方式只支持自动关联, 不支持手工关联!!"          
    IMG_VIEW_MODE_DISPLAY_TEXT                    = u"图像查看方式"
    OBJ_VIEW_MODE_DISPLAY_TEXT                    = u"对象查看方式"
    GUI_CANNOT_ADD_MORE_THAN_ONE_VIDEO_FILES_TEXT = u'一个json文件最多只允许增加一个视频文件!'
    GUI_ONE_VIDEO_FILE_OR_MULTIPLE_IMG_FILES_IS_ALLOWED_TEXT = u'一个json文件只允许包含一个视频文件，或者多个图片文件!'
    GUI_MEDIA_FILE_DONT_EXIST_TEXT                = u'该文件{}不存在!'
    GUI_PLS_SPECIFY_MORE_THAN_ONE_JSON_FILES_TEXT = u'请指定两个或两个以上JSON文件以参与合并!'
    GUI_INVALID_FOLDER_PATH_TEXT                  = u'无效文件夹路径'
            
    APP_NAME                                      = u"视频结构化标注工具"           
    ORGANIZATION_NAME                             = u"香港久凌"                

    LEFT_EYE_OUTER_CORNER_DISPLAYTEXT             = u"左外眼角"              
    LEFT_EYE_INNER_CORNER_DISPLAYTEXT             = u"左内眼角"              
    RIGHT_EYE_INNER_CORNER_DISPLAYTEXT            = u"右内眼角"              
    RIGHT_EYE_OUTER_CORNER_DISPLAYTEXT            = u"右外眼角"              
    NOSE_TIP_DISPLAYTEXT                          = u"鼻尖"               
    UPPER_LIP_CENTER_DISPLAYTEXT                  = u"上唇中心"              
    LEFT_EYE_CENTER_DISPLAYTEXT                   = u"左眼中心"              
    RIGHT_EYE_CENTER_DISPLAYTEXT                  = u"右眼中心"              
    LEFT_MOUTH_CORNER_DISPLAYTEXT                 = u"左嘴角"               
    RIGHT_MOUTH_CORNER_DISPLAYTEXT                = u"右嘴角"               

    STATISTIC_OR_APPLY_OBJVIEWFILTER_FOR_CUR_JSON_FILE_PLUGIN_DISPLAYTEXT   = u"统计当前json文件/为当前json文件应用对象查看filter"
    STATISTIC_FOR_MULTIPLE_JSON_FILES_PLUGIN_DISPLAYTEXT = u"统计指定目录下的所有json文件"
    CREATE_JSON_FILE_FOR_SPECIFIC_IMG_FOLDER_PLUGIN_DISPLAYTEXT = u"为指定目录下的所有图片文件创建标注文件"
    MERGE_MULTIPLE_JSON_FILES_PLUGIN_DISPLAYTEXT         = u"合并多个json文件"                                                                       
    CLEAN_DUPLICATE_DATA_IN_JSON_FILE_PLUGIN_DISPLAYTEXT = u"清除json文件重复图片"      
    SPLIT_TO_MULTIPLE_JSON_FILES_PLUGIN_DISPLAYTEXT      = u"将单个json文件分割为多个json文件(每个文件最多包含100个图片)"
    
    STARTUP_TIPS_DIALOG_DISPLAYTEXT               = u"自0.4.3版本开始:\n\n1. 车辆颜色标签种类已调整为11种颜色!\n     - 原银色更名为灰(银)\n     - 去掉金色和橙色\n\n2. 行人/骑车人的角度已调整为4个选项:\n     - 正面，背面，侧面，未知(即：不能确定)\n"
    STARTUP_TIPS_DIALOG_TITLE                     = u"特别提示"
    
    GUI_ADD_ONE_MORE_VERTEX_MESSAGE               = u"请移动然后点击鼠标左键以增加新顶点."
                                             

OVERIDE_ATTRS_DICT = {
ANNOTATION_PERSONBIKE_TOKEN : ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN,
ANNOTATION_VEHICLE_TOKEN    : ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN,
}

OBJ_LABEL_RECT_POS_DICT = {
# objClassName                : (xOffset, yOffset, xSize, ySize)
# e.g:'vehicle'               : (0,       0.5,     1,      0.1),
ANNOTATION_PERSONBIKE_TOKEN   : (0,       0.9,     1,      0.1),
}

                                                                           
# ==================================================================================
# DISPLAY CONTROL configuration.                                           
#
# This a simple python module with module-level variables. 
#
# In all cases in the configuration where a python callable (such as a
# function, class constructor, etc.) is expected, it is equally possible
# to specify a module path (as string) pointing to such a python callable.
# It will then be automatically imported.
# ==================================================================================
        
PANNELPROPERTY_LIST = []                   
def REGISTER_GROUP(pannelProperty, pannelName, pannelDisplayText, pannelCreatorName, pannelContainerName, extraArgs):      
    PANNELPROPERTY_LIST.append((pannelProperty, pannelName, pannelDisplayText, pannelCreatorName, pannelContainerName, extraArgs))


# BUTTONGROUP*
#
# List/tuple of dictionaries that defines the BUTTONGROUP* classes
# that are handled by sloth.  For each label, there should
# be one dictionary that contains the following keys:
#
#   - 'item' : Visualization item for this label. This can be
#              any python callable or a module path string 
#              implementing the visualization item interface.
#
#   - 'inserter' : (optional) Item inserter for this label.
#                  If the user selects to insert a new label of this class
#                  the inserter is responsible to actually 
#                  capture the users mouth actions and insert
#                  a new label into the annotation model.
#
#   - 'hotkey' : (optional) A keyboard shortcut starting 
#                the insertion of a new label of this class.
#
#   - 'attributes' : (optional) A dictionary that defines the
#                    keys and possible values of this label
#                    class.
#
#   - 'text' : (optional) A label for the item's GUI button.

# object type
BUTTONGROUP1 = (
    {
        'attributes': {
            'class':         'Ignore',
            'displaycolor':  '#ff969650',
            'fill':          True,
            'drawtext':      True,
            'displaytext':   GUI_IGNORE_WIDGET_DISPLAYTEXT,            
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_IGNORE_BUTTON_HOTKEY,
    },
    {
        'attributes': {
            'class':         ANNOTATION_OBJTYPE_WIDGET_TOKEN,
            'displaytext':   GUI_OBJTYPE_WIDGET_DISPLAYTEXT,
            'fill':          False,
            'drawtext':      True,
            'optioninfo' :
            {
                'option':  
                (
                     {
                         'tag':           ANNOTATION_PEDESTRAIN_TOKEN,
                         'fill':          False,
                         'drawtext':      True,
                         'displaycolor':  'blue',
                         'hotkey':        '',
                         'displaytext':   GUI_PEDESTRAIN_WIDGET_DISPLAYTEXT, 
                         'isDefault'  :   True
                     },
                     {
                         'tag':           ANNOTATION_PERSONBIKE_TOKEN,
                         'fill':          False,
                         'drawtext':      True,
                         'displaycolor':  '#ffff00',
                         'hotkey':        '',
                         'displaytext':   GUI_PERSONBIKE_WIDGET_DISPLAYTEXT, 
                     },
                     {
                         'tag':           ANNOTATION_VEHICLE_TOKEN,
                         'fill':          False,
                         'drawtext':      True,
                         'displaycolor':  'magenta',
                         'hotkey':        '',
                         'displaytext':   GUI_VEHICLE_WIDGET_DISPLAYTEXT, 
                     },
                ),   
                        
                'name':          ANNOTATION_OBJTYPE_WIDGET_TOKEN,
                'displaytext':   GUI_OBJTYPE_GROUP_WIDGET_DISPLAYTEXT,
                'annotatemode':  ANNOTATION_BBOX_ANNOMODE_TOKEN,      
                'drawtext':      'True',
            }           
            
        },                   
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_PEDESTRAIN_BUTTON_HOTKEY,
    }
)   
    
# personbike attributes
COMBOGROUP_PERSONBIKE = (
    {
        'attributes': {
            'class':         ANNOTATION_HELMET_WIDGET_TOKEN,
            'displaycolor':  'blue',
            'fill':          False,
            'drawtext':      False,
            'displaytext':   GUI_HELMET_WIDGET_DISPLAYTEXT,
        },                   
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_HELMET_BUTTON_HOTKEY,
    },                       
    {
        'attributes': {
            'class':         ANNOTATION_PLATE_WIDGET_TOKEN,
            'displaytext':   GUI_PLATE_WIDGET_DISPLAYTEXT,
            'fill':          False,
            'drawtext':      False,
            'optioninfo' :
            {
                'option':  
                (
                     {
                         'tag':           ANNOTATION_LICENSE_PLATE_OPTION_WIDGET_TOKEN,
                         'fill':          False,
                         'drawtext':      True,
                         'displaycolor':  '#ec534b',
                         'hotkey':        '',
                         'displaytext':   GUI_LICENSE_PLATE_WIDGET_DISPLAYTEXT, 
                         'isDefault'  :   True
                     },
                     {
                         'tag':           ANNOTATION_BILLBOARD_OPTION_WIDGET_TOKEN,
                         'fill':          False,
                         'drawtext':      True,
                         'displaycolor':  '#915aa4',
                         'hotkey':        '',
                         'displaytext':   GUI_BILLBOARD_WIDGET_DISPLAYTEXT, 
                     },
                ),   
                        
                'name':          ANNOTATION_PLATE_TYPE_GROUP_WIDGET_TOKEN,
                'displaytext':   GUI_PLATE_TYPE_GROUP_WIDGET_DISPLAYTEXT,
                'annotatemode':  ANNOTATION_BBOX_ANNOMODE_TOKEN,      
                'drawtext':      'True',
            }           
            
        },                   
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_PERSONBIKE_LICENSE_PLATE_HOTKEY,
    },                       

    { 'option':  
      (
           {
               'tag':          TAG_PERSONBIKE_TYPE_OF_BICYCLE_TOKEN,
               'displaycolor': '#ec534b',
               'hotkey':       '',
               'displaytext':  TAG_PERSONBIKE_TYPE_OF_BICYCLE_DISPLAYTEXT,
           },
           {
               'tag':          TAG_PERSONBIKE_TYPE_OF_LIGHTMOTOR_TOKEN,
               'displaycolor': '#915aa4',
               'hotkey':       '',
               'displaytext':  TAG_PERSONBIKE_TYPE_OF_LIGHTMOTOR_DISPLAYTEXT,
           },
           {
               'tag':          TAG_PERSONBIKE_TYPE_OF_MOTOR_TOKEN,
               'displaycolor': '#a1d2dd',
               'hotkey':       '',
               'displaytext':  TAG_PERSONBIKE_TYPE_OF_MOTOR_DISPLAYTEXT,
           },
           {
               'tag':          TAG_PERSONBIKE_TYPE_OF_THREE_WHEEL_TOKEN,
               'displaycolor': '#e0eab8',
               'hotkey':       '',
               'displaytext':  TAG_PERSONBIKE_TYPE_OF_THREE_WHEEL_DISPLAYTEXT,
           },
           {
               'tag'         : TAG_PERSONBIKE_TYPE_OF_UNKNOWN_TOKEN,
               'displaycolor': '#00B050',
               'hotkey'      : '',
               'displaytext' : TAG_PERSONBIKE_TYPE_OF_UNKNOWN_DISPLAYTEXT,  
           },
           {
               'tag'         : TAG_UNSET_TOKEN,
               'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           },           
      ),   
                    
      'name':         ANNOTATION_PERSONBIKE_TYPE_GROUP_TOKEN,
      'displaytext':  GUI_PERSONBIKE_TYPE_GROUP_WIDGET_DISPLAYTEXT,
      'annotatemode': ANNOTATION_BBOX_ANNOMODE_TOKEN,
      'drawtext':     'True',
   },
   
    { 'option':  
      (
           {
               'tag':       'White',
               'rgb':       '#FFFFFF',
               'hotkey':    '',
               'displaytext': u'白',  
           },
           {
               'tag':       'Gray',
               'rgb':       '#b4b4b4',
               'hotkey':    '',
               'displaytext': u'灰',  
           },
           {
               'tag':       'Yellow',
               'rgb':       '#FFFF00',
               'hotkey':    '',
               'displaytext': u'黄',  
           },
           {
               'tag':       'Pink',
               'rgb':       '#FF7AFF',
               'hotkey':    '',
               'displaytext': u'粉',  
           },
           {
               'tag':       'Red',
               'rgb':       '#FF2600',
               'hotkey':    '',
               'displaytext': u'红',  
           },
           {
               'tag':       'Purple',
               'rgb':       '#942092',
               'hotkey':    '',
               'displaytext': u'紫',  
           },
           {
               'tag':       'Green',
               'rgb':       '#00B050',
               'hotkey':    '',
               'displaytext': u'绿',  
           },
           {
               'tag':       'Blue',
               'rgb':       '#0432FF',
               'hotkey':    '',
               'displaytext': u'蓝',  
           },
           {
               'tag':       'Brown',
               'rgb':       '#523620',
               'hotkey':    '',
               'displaytext': u'棕',  
           },
           {
               'tag':       'Black',
               'rgb':       '#000000',
               'hotkey':    '',
               'displaytext': u'黑',  
           },
           {
               'tag':       'Blend',
               'rgb':       '#B2A27E',
               'hotkey':    '',
               'displaytext': u'混色',  
           },
           {
               'tag'         : TAG_UNSET_TOKEN,
               'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           },            
      ),              
      
      'name':          ANNOTATION_HELMET_COLOR_TOKEN,
      'annotatemode':  ANNOTATION_ATTR_ANNOMODE_TOKEN,
      'drawtext':     'True',
      'displaytext':   u'头盔颜色'
    }
   
   
)


# person parts
BUTTONGROUP2 = (
    {
        'attributes': {
            'class':         ANNOTATION_UPPER_BODY_TOKEN,
            'displaycolor':  'red',
            'fill':          False,
            'drawtext':      False,
            'displaytext':   GUI_UPPERBODY_WIDGET_DISPLAYTEXT,            
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_UPPER_BODY_BUTTON_HOTKEY,
    },
    {
        'attributes': {
            'class':         ANNOTATION_LOWER_BODY_TOKEN,
            'displaycolor':  'green',
            'fill':          False,
            'drawtext':      False,
            'displaytext':   GUI_LOWERBODY_WIDGET_DISPLAYTEXT,              
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_LOWER_BODY_BUTTON_HOTKEY,
    },
    {
        'attributes': {
            'class':         ANNOTATION_HEAD_TOKEN,
            'displaycolor':  '#FFA50080',
            'fill':          False,
            'drawtext':      False,
            'displaytext':   GUI_HEAD_WIDGET_DISPLAYTEXT,
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_HEAD_BUTTON_HOTKEY,
    },
    {
        'attributes': {
            'class':         ANNOTATION_FACE_TOKEN,
            'displaycolor':  '#0000FF80',
            'fill':          False,
            'drawtext':      False,
            'displaytext':   GUI_FACE_WIDGET_DISPLAYTEXT,
        },                   
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_FACE_BUTTON_HOTKEY,
    },    
#    {
#        'attributes': {
#            'class':         ANNOTATION_LEFT_EYE_TOKEN,
#            'displaycolor':  'blue',
#            'fill':          True,
#            'drawtext':      False,
#            'displaytext':   GUI_LEFT_EYE_CENTER_WIDGET_DISPLAYTEXT,
#        },                   
#        'inserter':          'sloth.items.PointItemInserter',
#        'item':              'sloth.items.PointItem',
#        'hotkey':            GUI_LEFT_EYE_BUTTON_HOTKEY,
#    },    
#    {
#        'attributes': {
#            'class':         ANNOTATION_RIGHT_EYE_TOKEN,
#            'displaycolor':  'yellow',
#            'fill':          True,
#            'drawtext':      False,
#            'displaytext':   GUI_RIGHT_EYE_CENTER_WIDGET_DISPLAYTEXT,
#        },                   
#        'inserter':          'sloth.items.PointItemInserter',
#        'item':              'sloth.items.PointItem',
#        'hotkey':            GUI_RIGHT_EYE_BUTTON_HOTKEY,
#    },    
#    {
#        'attributes': {
#            'class':         ANNOTATION_NOSE_TOKEN,
#            'displaycolor':  'green',
#            'fill':          True,
#            'drawtext':      False,
#            'displaytext':   GUI_NOSE_TIP_WIDGET_DISPLAYTEXT,
#        },                   
#        'inserter':          'sloth.items.PointItemInserter',
#        'item':              'sloth.items.PointItem',
#        'hotkey':            GUI_NOSE_BUTTON_HOTKEY,
#    },    
#    {
#        'attributes': {
#            'class':         ANNOTATION_LEFT_MOUTH_TOKEN,
#            'displaycolor':  'red',
#            'fill':          True,
#            'drawtext':      False,
#            'displaytext':   GUI_LEFT_MOUTH_CORNER_WIDGET_DISPLAYTEXT,
#        },                   
#        'inserter':          'sloth.items.PointItemInserter',
#        'item':              'sloth.items.PointItem',
#        'hotkey':            GUI_LEFT_MOUTH_BUTTON_HOTKEY,
#    },    
#    {
#        'attributes': {
#            'class':         ANNOTATION_RIGHT_MOUTH_TOKEN,
#            'displaycolor':  'pink',
#            'fill':          True,
#            'drawtext':      False,
#            'displaytext':   GUI_RIGHT_MOUTH_CORNER_WIDGET_DISPLAYTEXT,
#        },                   
#        'inserter':          'sloth.items.PointItemInserter',
#        'item':              'sloth.items.PointItem',
#        'hotkey':            GUI_RIGHT_MOUTH_BUTTON_HOTKEY,
#    },    

    {
        'attributes': {
            'class':         ANNOTATION_FACE5POINTS_TOKEN,
            'displaycolor':  '#00FF0000',
            'fill':          True,
            'drawtext':      False,
            'displaytext':   GUI_FACE5POINTS_WIDGET_DISPLAYTEXT,
        },                   
        'inserter':          'sloth.items.NPointFaceInserter',
        'item':              'sloth.items.NPointFaceItem',
        'hotkey':            GUI_FACE5POINTS_BUTTON_HOTKEY,
    }, 
)    




# person accessory
BUTTONGROUP3 = (
    {
        'attributes': {
            'class':         ANNOTATION_UMBRELLA_TOKEN,
            'displaycolor':  '#FF2600',
            'fill':          False,
            'drawtext':      True,
            'displaytext':   GUI_UMBRELLA_WIDGET_DISPLAYTEXT,            
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_UMBRELLA_BUTTON_HOTKEY,
    },
    {
        'attributes': {
            'class':         ANNOTATION_BACKPACK_WIDGET_TOKEN,
            'displaycolor':  '#00FF00',
            'fill':          False,
            'drawtext':      True,
            'displaytext':   GUI_BACKPACK_WIDGET_DISPLAYTEXT,              
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_BACKPACK_BUTTON_HOTKEY,
    },

    {
        'attributes': {
            'class':         ANNOTATION_CARRINGBAG_WIDGET_TOKEN,
            'displaycolor':  '#0000ff',
            'fill':          False,
            'drawtext':      True,
            'displaytext':   GUI_CARRYINGBAG_WIDGET_DISPLAYTEXT,               
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_CARRYINGBAG_BUTTON_HOTKEY,
    },
    {
        'attributes': {
            'class':         ANNOTATION_GLASSES_WIDGET_TOKEN,
            'displaycolor':  '#FF8040',
            'fill':          False,
            'drawtext':      True,
            'displaytext':   GUI_GLASSES_WIDGET_DISPLAYTEXT,              
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_GLASSES_BUTTON_HOTKEY,
    },
    {
        'attributes': {
            'class':         ANNOTATION_HAT_WIDGET_TOKEN,
            'displaycolor':  '#FF0040',
            'fill':          False,
            'drawtext':      False,
            'displaytext':   GUI_HAT_WIDGET_DISPLAYTEXT,             
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_HAT_BUTTON_HOTKEY,
    },
    {
        'attributes': {
            'class':         ANNOTATION_MASK_WIDGET_TOKEN,
            'displaycolor':  '#228B22',
            'fill':          False,
            'drawtext':      True,
            'displaytext':   GUI_MASK_WIDGET_DISPLAYTEXT,            
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_MASK_BUTTON_HOTKEY,
    },
    {
        'attributes': {
            'class':         ANNOTATION_LUGGAGE_WIDGET_TOKEN,
            'displaycolor':  '#0000A0',
            'fill':          False,
            'drawtext':      True,
            'displaytext':   GUI_LUGGAGE_WIDGET_DISPLAYTEXT,            
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_LUGGAGE_BUTTON_HOTKEY,
    },
)    

JL_17COLOR_OPTIONS = (
    {
        'tag':       'Red',
        'rgb':       '#FF2600',
        'hotkey':    '',
        'displaytext': u'红',  
    },
    {     
        'tag':       'Orange',
        'rgb':       '#FF9300',
        'hotkey':    '',
        'displaytext': u'橙',  
    },     
    {     
        'tag':       'Yellow',
        'rgb':       '#FFFF00',
        'hotkey':    '',
        'displaytext': u'黄',  
    },     
    {     
        'tag':       'Green',
        'rgb':       '#00B050',
        'hotkey':    '',
        'displaytext': u'绿',  
    },     
    {     
        'tag':       'Cyan',
        'rgb':       '#00FDFF',
        'hotkey':    '',
        'displaytext': u'青',  
    },     
    {     
        'tag':       'Blue',
        'rgb':       '#0432FF',
        'hotkey':    '',
        'displaytext': u'蓝',  
    },     
    {     
        'tag':       'Purple',
        'rgb':       '#942092',
        'hotkey':    '',
        'displaytext': u'紫',  
    },     
    {     
        'tag':       'Black',
        'rgb':       '#000000',
        'hotkey':    '',
        'displaytext': u'黑',  
    },     
    {     
        'tag':       'White',
        'rgb':       '#FFFFFF',
        'hotkey':    '',
        'displaytext': u'白',  
    },     
    {     
        'tag':       'Gray',
        'rgb':       '#b4b4b4',
        'hotkey':    '',
        'displaytext': u'浅灰',  
    },     
    {     
        'tag':       'DarkGray',
        'rgb':       '#505050',
        'hotkey':    '',
        'displaytext': u'深灰',  
    },           
    {     
        'tag':       'Pink',
        'rgb':       '#FF7AFF',
        'hotkey':    '',
        'displaytext': u'粉红',  
    },     
    {     
        'tag':       'Khaki',
        'rgb':       '#C4AE85',
        'hotkey':    '',
        'displaytext': u'卡其',  
    },     
    {     
        'tag':       'Brown',
        'rgb':       '#863C05',
        'hotkey':    '',
        'displaytext': u'褐',  
    },     
    {     
        'tag':       'SapphireBlue',
        'rgb':       '#02107F',
        'hotkey':    '',
        'displaytext': u'宝蓝',  
    },     
    {     
        'tag':       'PowderBlue',
        'rgb':       '#7192BD',
        'hotkey':    '',
        'displaytext': u'灰蓝',  
    },     
    {     
        'tag':       'LightBlue',
        'rgb':       '#28A3E9',
        'hotkey':    '',
        'displaytext': u'浅蓝',  
    },     
)     
     
# person clothes
BUTTONGROUP4 = (
    { 
      # -----------------------------------------------------------------------------------
      # Dear guy, please configure here for your preferred color classification tags
      # -----------------------------------------------------------------------------------
      # 'option':  JL_17COLOR_OPTIONS,
      # 'option': HISENSE_9COLOR_OPTIONS,
      'option': HISENSE_9COLOR_OPTIONS,
      # -----------------------------------------------------------------------------------
      
      'name'  :  ANNOTATION_UPPER_COLOR_TOKEN,
      'displaytext':  u'上衣颜色'
    },
    
    { 
      # -----------------------------------------------------------------------------------
      # Dear guy, please configure here for your preferred color classification tags
      # -----------------------------------------------------------------------------------
      # 'option':  JL_17COLOR_OPTIONS,
      # 'option': HISENSE_9COLOR_OPTIONS,
      'option': HISENSE_9COLOR_OPTIONS,
      # -----------------------------------------------------------------------------------
      
      'name'  :  ANNOTATION_LOWER_COLOR_TOKEN,
      'displaytext':  u'下衣颜色'
    },
    { 'option':  
      (
           {
               'tag':           TAG_LONG_SLEEVE_TOKEN,
               'displaycolor':  '#FF2600',
               'hotkey':        '',
               'displaytext':   u'长袖',
           },
           {
               'tag':           TAG_SHORT_SLEEVE_TOKEN,
               'displaycolor':  '#32CD32',
               'hotkey':        '',
               'displaytext':   u'短袖',
           },
           {
               'tag':           TAG_SLEEVELESS_TOKEN,
               'displaycolor':  '#FFFF00',
               'hotkey':        '',
               'displaytext':   u'无袖',
           },
           {
               'tag':           TAG_UPPER_BARE_TOKEN,
               'displaycolor':  '#00FDFF',
               'hotkey':        '',
               'displaytext':   u'赤裸',
           },
           
           {
               'tag':           TAG_OTHER_CASE_TOKEN,
               'displaycolor':  '#0432FF',
               'hotkey':        '',
               'displaytext':   u'其它',
           },           
           {
               'tag'         : TAG_UNSET_TOKEN,
               'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           },  
      ),              
      'name':  ANNOTATION_UPPER_CLOTH_TOKEN,
      'displaytext':  u'上衣'
    },    
    { 'option':  
      (

           {
               'tag':          TAG_LONG_PANTS_TOKEN,
               'displaycolor': '#FF2600',
               'hotkey':       '',
               'displaytext':  u'长裤',
           },
           {
               'tag':          TAG_SHORT_PANTS_TOKEN,
               'displaycolor': '#32CD32',
               'hotkey':       '',
               'displaytext':  u'短裤',
           },
           {
               'tag':          TAG_SKIRT_TOKEN,
               'displaycolor': '#FFFF00',
               'hotkey':       '',
               'displaytext':  u'裙',
           },  
           {
               'tag':           TAG_OTHER_CASE_TOKEN,
               'displaycolor':  '#0432FF',
               'hotkey':        '',
               'displaytext':   u'其它',
           },             
           {
               'tag'         : TAG_UNSET_TOKEN,
               'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           },                    
      ),              
      'name':  ANNOTATION_LOWER_CLOTH_TOKEN,
      'displaytext':  u'下装'
    },
    { 'option':  
      (
           {
               'tag':           TAG_UPPER_NO_TEXTURE_TOKEN,
               'displaycolor':  '#FF2600',
               'hotkey':        '',
               'displaytext':   u'无纹理',
           },
           {
               'tag':           TAG_UPPER_STRIPE_TEXTURE_TOKEN,
               'displaycolor':  '#32CD32',
               'hotkey':        '',
               'displaytext':   u'条纹',
           },
           {
               'tag':           TAG_UPPER_GRID_TEXTURE_TOKEN,
               'displaycolor':  '#FFFF00',
               'hotkey':        '',
               'displaytext':   u'格子',
           },
           {
               'tag':           TAG_OTHER_CASE_TOKEN,
               'displaycolor':  '#0432FF',
               'hotkey':        '',
               'displaytext':   u'其它',
           },           
           {
               'tag'         : TAG_UNSET_TOKEN,
               'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           },  
      ),              
      'name':  ANNOTATION_UPPER_TEXTURE_TOKEN,
      'displaytext':  u'上衣纹理'
    },    
)


# person details
BUTTONGROUP5 = (
    { 'option':  
      (
           {
               'tag':       'male',
               'displaycolor': '#6a5acd',
               'hotkey':    '',
               'displaytext': u'男',
           },
           {
               'tag':       'female',
               'displaycolor': '#C71585',
               'hotkey':    '',
               'displaytext': u'女',
           },
           {
               'tag':       'genderunknown',
               'displaycolor': '#C71585',
               'hotkey':    '',
               'displaytext': u'未知',
           },
           {
               'tag'         : TAG_UNSET_TOKEN,
               'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           },           
      ),              
      'name':  ANNOTATION_GENDER_TOKEN,
      'displaytext':  GUI_GENDER_WIDGET_DISPLAYTEXT
    },
    { 'option':  
      (
           {
               'tag':       'child',
               'displaycolor': '#1E90FF',
               'hotkey':    '',
               'displaytext': u'童',
           },
           {
               'tag':       'young',
               'displaycolor': '#48D1CC',
               'hotkey':    '',
               'displaytext': u'青',
           },
           {
               'tag':       'middle',
               'displaycolor': '#7CFC00',
               'hotkey':    '',
               'displaytext': u'中',
           },
           {
               'tag':       'elder',
               'displaycolor': '#4B0082',
               'hotkey':    '',
               'displaytext': u'老',
           },
           {
               'tag':       'ageunknown',
               'displaycolor': '#C71585',
               'hotkey':    '',
               'displaytext': u'未知',
           }, 
           {
               'tag'         : TAG_UNSET_TOKEN,
               'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           },                      
      ),              
      'name':  ANNOTATION_AGE_TOKEN,
      'displaytext':  GUI_AGE_WIDGET_DISPLAYTEXT
    },
    { 'option':  
      (

           {
               'tag':       'front',
               'displaycolor': '#DDA0DD',
               'hotkey':    '',
               'displaytext': u'正',
           },
           {
               'tag':       'back',
               'displaycolor': '#4169E1',
               'hotkey':    '',
               'displaytext': u'背',
           },
           {
               'tag':       'side',
               'displaycolor': '#90EE90',
               'hotkey':    '',
               'displaytext': u'侧',
           },
           {
               'tag':       'angleunknown',
               'displaycolor': '#C71585',
               'hotkey':    '',
               'displaytext': u'未知',
           },       
           {
               'tag'         : TAG_UNSET_TOKEN,
               'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           },                 
      ),              
      'name':  ANNOTATION_ANGLE_TOKEN,
      'displaytext':  GUI_ANGLE_WIDGET_DISPLAYTEXT
    },
    { 'option':  
      (

           {
               'tag':       'longHair',
               'displaycolor': '#90EE90',
               'hotkey':    '',
               'displaytext': u'长发',
           },
           {
               'tag':       'shortHair',
               'displaycolor': '#EE82EE',
               'hotkey':    '',
               'displaytext': u'短发',
           },
           {
               'tag':       'hairstyleunknown',
               'displaycolor': '#C71585',
               'hotkey':    '',
               'displaytext': u'未知',
           },    
           {
               'tag'         : TAG_UNSET_TOKEN,
               'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           },                     
      ),              
      'name':  ANNOTATION_HAIR_STYLE_TOKEN,
      'displaytext':  GUI_HAIR_STYLE_WIDGET_DISPLAYTEXT
    },    
)    
 
# --------------------------------------------------------------    
# vehicle/personbike info
# --------------------------------------------------------------    
BUTTONGROUP6 = (
    {
        'attributes': {
            'class':         ANNOTATION_VEHICLE_TOKEN,
            'displaycolor':  'magenta',
            'fill':          False,
            'drawtext':      False,
            'displaytext':   GUI_VEHICLE_WIDGET_DISPLAYTEXT,
        },
        'inserter':          'sloth.items.RectItemInserter',
        'item':              'sloth.items.RectItem',
        'hotkey':            GUI_VEHICLE_BUTTON_HOTKEY,
   },
   {
        'attributes': {
            'class':         ANNOTATION_VEHICLE_LICENSE_PLATE_TOKEN,
            'displaycolor':  '#00FF0000',
            'fill':          True,
            'drawtext':      False,
            'displaytext':   GUI_VEHICLE_LICENSE_PLATE_WIDGET_DISPLAYTEXT,
        },                   
        'inserter':          'sloth.items.QuadrangleItemInserter',
        'item':              'sloth.items.PolygonItem',
        'hotkey':            GUI_VEHICLE_LICENSE_PLATE_HOTKEY,
    },
    { 'option':  
      (
           { 
               'tag':          TAG_VEHICLE_TYPE_OF_SEDAN_TOKEN,
               'displaycolor': '#ec534b',
               'hotkey':       '',
               'displaytext':  TAG_VEHICLE_TYPE_OF_SEDAN_DISPLAYTEXT,
           },
           {
               'tag':          TAG_VEHICLE_TYPE_OF_SUV_TOKEN,
               'displaycolor': '#915aa4',
               'hotkey':       '',
               'displaytext':  TAG_VEHICLE_TYPE_OF_SUV_DISPLAYTEXT,
           },
           {
               'tag':          TAG_VEHICLE_TYPE_OF_MINIBUS_TOKEN,
               'displaycolor': '#F1d24D',
               'hotkey':       '',
               'displaytext':  TAG_VEHICLE_TYPE_OF_MINIBUS_DISPLAYTEXT,
           },
           {
               'tag':          TAG_VEHICLE_TYPE_OF_LARGE_COACH_TOKEN,
               'displaycolor': '#A080f0',
               'hotkey':       '',
               'displaytext':  TAG_VEHICLE_TYPE_OF_LARGE_COACH_DISPLAYTEXT,
           },
           {
               'tag'         : TAG_VEHICLE_TYPE_OF_MEDIUM_COACH_TOKEN,
               'displaycolor': '#20B050',
               'hotkey'      : '',
               'displaytext' : TAG_VEHICLE_TYPE_OF_MEDIUM_COACH_DISPLAYTEXT,  
           },
           {
               'tag'         : TAG_VEHICLE_TYPE_OF_HEAVY_VAN_TOKEN,
               'displaycolor': '#2000B0',
               'hotkey'      : '',
               'displaytext' : TAG_VEHICLE_TYPE_OF_HEAVY_VAN_DISPLAYTEXT,  
           },
           {
               'tag'         : TAG_VEHICLE_TYPE_OF_LIGHT_VAN_TOKEN,
               'displaycolor': '#f030B0',
               'hotkey'      : '',
               'displaytext' : TAG_VEHICLE_TYPE_OF_LIGHT_VAN_DISPLAYTEXT,  
           },           
           {
               'tag'         : TAG_VEHICLE_TYPE_OF_ENGINEERING_TRUCK_TOKEN,
               'displaycolor': '#805050',
               'hotkey'      : '',
               'displaytext' : TAG_VEHICLE_TYPE_OF_ENGINEERING_TRUCK_DISPLAYTEXT,
           },
           {
               'tag'         : TAG_VEHICLE_TYPE_OF_UNKNOWN_TOKEN,
               'displaycolor': '#00B050',
               'hotkey'      : '',
               'displaytext' : TAG_VEHICLE_TYPE_OF_UNKNOWN_DISPLAYTEXT,
           },           
           {
               'tag'         : TAG_UNSET_TOKEN,
               'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           },           
           
      ),   
                    
      'name':         ANNOTATION_VEHICLE_TYPE_GROUP_TOKEN,
      'displaytext':  GUI_VEHICLE_TYPE_GROUP_WIDGET_DISPLAYTEXT,
      'annotatemode': ANNOTATION_BBOX_ANNOMODE_TOKEN,
      'drawtext':     'True',
   },
   { 'option':  
      (

           {
               'tag':       'front',
               'displaycolor': '#DDA0DD',
               'hotkey':    '',
               'displaytext': u'正',
           },
           {
               'tag':       'back',
               'displaycolor': '#4169E1',
               'hotkey':    '',
               'displaytext': u'背',
           },
           {
               'tag':       'side',
               'displaycolor': '#90EE90',
               'hotkey':    '',
               'displaytext': u'侧',
           },
           {
               'tag':       'angleunknown',
               'displaycolor': '#C71585',
               'hotkey':    '',
               'displaytext': u'未知',
           },       
           {
               'tag'         : TAG_UNSET_TOKEN,
               'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           },                 
      ),              
      'name':  ANNOTATION_VEHICLE_ANGLE_TOKEN,
      'displaytext':  GUI_VEHICLE_ANGLE_WIDGET_DISPLAYTEXT,
      'annotatemode': ANNOTATION_ATTR_ANNOMODE_TOKEN,
      'drawtext':     'True',
    },
    { 'option':  
      (
           {
               'tag':       'Red',
               'rgb':       '#FF2600',
               'hotkey':    '',
               'displaytext': u'红',  
           },
           {
               'tag':       'Yellow',
               'rgb':       '#FFFF00',
               'hotkey':    '',
               'displaytext': u'黄',  
           },
           {
               'tag':       'Green',
               'rgb':       '#00B050',
               'hotkey':    '',
               'displaytext': u'绿',  
           },
           {
               'tag':       'Blue',
               'rgb':       '#0432FF',
               'hotkey':    '',
               'displaytext': u'蓝',  
           },
           {
               'tag':       'Purple',
               'rgb':       '#942092',
               'hotkey':    '',
               'displaytext': u'紫',  
           },
           {
               'tag':       'Black',
               'rgb':       '#000000',
               'hotkey':    '',
               'displaytext': u'黑',  
           },
           {
               'tag':       'White',
               'rgb':       '#FFFFFF',
               'hotkey':    '',
               'displaytext': u'白',  
           },
           {
               'tag':       'Gray(Silver)',
               'rgb':       '#b2b2b2',
               'hotkey':    '',
               'displaytext': u'灰(银)',  
           },
           {
               'tag':       'Brown',
               'rgb':       '#523620',
               'hotkey':    '',
               'displaytext': u'棕',  
           },
           {
               'tag':       'Gray',
               'rgb':       '#646464',
               'hotkey':    '',
               'displaytext': u'灰',  
           },                      
           {
               'tag':       'Pink',
               'rgb':       '#EE84AC',
               'hotkey':    '',
               'displaytext': u'粉',  
           }, 
           {
               'tag'         : TAG_VEHICLE_COLOR_OF_UNKNOWN_TOKEN,
               'rgb'         : '#B2A27E40',
               'hotkey'      : '',
               'displaytext' : TAG_VEHICLE_COLOR_OF_UNKNOWN_DISPLAYTEXT,
           },           
           {
               'tag'         : TAG_UNSET_TOKEN,
               #'displaycolor': '#B0B0B0',
               'hotkey'      : '',
               'displaytext' : TAG_UNSET_DISPLAYTEXT,
           }, 
                     
      ),              
      'name':         ANNOTATION_VEHICLE_COLOR_TOKEN,
      'displaytext':  GUI_VEHICLE_COLOR_WIDGET_DISPLAYTEXT,
      'annotatemode': ANNOTATION_ATTR_ANNOMODE_TOKEN,
      'drawtext':     'False',
    },

    
)




REGISTER_GROUP(BUTTONGROUP1,          "BUTTONGROUP1",          GUI_BUTTONGROUP1_DISPLAYTEXT,     'ComboAreaWidget', 'dockProperties1',           [GUI_OBJTYPE_GROUP_DISPLAYTEXT] )   
REGISTER_GROUP(BUTTONGROUP2,          "BUTTONGROUP2",          GUI_BUTTONGROUP2_DISPLAYTEXT,     'PropertyEditor',  'dockProperties2',           [] ) 
REGISTER_GROUP(BUTTONGROUP3,          "BUTTONGROUP3",          GUI_BUTTONGROUP3_DISPLAYTEXT,     'PropertyEditor',  'dockProperties3',           [] ) 
REGISTER_GROUP(BUTTONGROUP4,          "BUTTONGROUP4",          GUI_BUTTONGROUP4_DISPLAYTEXT,     'AttrAreaWidget',  'dockProperties4',           [] ) 
REGISTER_GROUP(BUTTONGROUP5,          "BUTTONGROUP5",          GUI_BUTTONGROUP5_DISPLAYTEXT,     'AttrAreaWidget',  'dockProperties5',           [] ) 
REGISTER_GROUP(BUTTONGROUP6,          "BUTTONGROUP6",          GUI_BUTTONGROUP6_DISPLAYTEXT,     'ComboAreaWidget',  'dockProperties6',          [GUI_VEHICLE_BBOXS_DISPLAYTEXT] ) 
REGISTER_GROUP(COMBOGROUP_PERSONBIKE, "COMBOGROUP_PERSONBIKE", GUI_PERSONBIKE_PANEL_DISPLAYTEXT, 'ComboAreaWidget', 'dockProperties_personbike', [GUI_PERSONBIKE_BBOXS_DISPLAYTEXT] )
REGISTER_GROUP((),                    "OBJINFO",               GUI_OBJINFO_PANNEL_DISPLAYTEXT,   '',                'dockObjViewModeInfoWidget', [] )
REGISTER_GROUP((),                    "ANNOTATION",            GUI_ANNOTATION_DISPLAYTEXT,       '',                'dockAnnotations',           [] )


# ==============================================================================
# HOTKEYS
#
# Defines the keyboard shortcuts.  Each hotkey is defined by a tuple
# with at least 2 entries, where the first entry is the hotkey (sequence),
# and the second entry is the function that is called.  The function
# should expect a single parameter, the labeltool object.  The optional
# third entry -- if present -- is expected to be a string describing the 
# action.
# ==============================================================================
HOTKEYS = (
#    ('Backspace', lambda lt: lt.gotoPrevious(step = 1),              GUI_PREV_IMG_TIP                           ),
    ('T',         lambda lt: lt.toggleDisplayView(),                  GUI_TOGGLE_DISPLAY_VIEW_TIP                ),
    ('E',         lambda lt: lt.setConnectLabelMode(True),            GUI_ENABLE_AUTO_CONNECT_LABELS_TIP         ),
    ('R',         lambda lt: lt.setConnectLabelMode(False),           GUI_DISABLE_AUTO_CONNECT_LABELS_TIP        ),
    ('W',         lambda lt: lt.gotoNext(step = 1),                   GUI_NEXT_IMG_TIP                           ),
    ('Q',         lambda lt: lt.gotoPrevious(step = 1),               GUI_PREV_IMG_TIP                           ),
    ('Shift+W',   lambda lt: lt.gotoEnd(),                            GUI_GOTO_END_TIP                           ),
    ('Shift+Q',   lambda lt: lt.gotoBegin(),                          GUI_GOTO_BEGIN_TIP                         ),
    ('Tab',       lambda lt: lt.selectNextAnnotation(),               GUI_NEXT_ANNOTATION_TIP                    ), 
    ('Shift+Tab', lambda lt: lt.selectPreviousAnnotation(),           GUI_PREV_ANNOTATION_TIP                    ), 
    ('Ctrl+f',    lambda lt: lt.view().fitInView(),                   GUI_FIT_CUR_IMG_INTO_WIN_TIP               ), 
    ('Del',       lambda lt: lt.deleteSelectedAnnotations(),          GUI_DEL_SELECTED_ANNOTATIONS_TIP           ), 
    ('ESC',       lambda lt: lt.exitInsertMode(),                     GUI_EXIT_INSERT_MODE                       ), 
    ('S',         lambda lt: lt.saveCurViewContentToImgFile(),         GUI_SAVE_CUR_VIEW_IMG_CONTENT_TO_FILE_TIP  ),
    ('Shift+S',   lambda lt: lt.saveAllAnnotationViewContentToImgFiles(),   GUI_SAVE_ALL_IMGS_VIEW_CONTENT_TO_FILES_TIP  ),

    ('Shift+C',   lambda lt: lt.clearObjViewFilter(),                 GUI_CLEAR_OBJ_VIEW_FILTER_TIP  ),
    ('Ctrl+r',   
      [ lambda lt: lt.currentImage().flipUnlabeled(),  
        lambda lt: lt._mainwindow.scene.setCurrentImage(lt.currentImage(), flush = True, display = True)
      ],   GUI_FILP_CUR_IMG_LABELED_TIP            ), 
     
#    ('Shift+c',   lambda lt: lt.currentImage().confirmAll(),         GUI_MARK_ALL_ANNOTATIONS_AS_CONFIRMED_TIP  ), 

     (None,  
      [ lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.setChecked(ANNOTATION_PEDESTRAIN_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.onClassButtonPressed(ANNOTATION_PEDESTRAIN_TOKEN)
      ],  GUI_PEDESTRAIN_BUTTON_TIP ),
     (GUI_PERSONBIKE_BUTTON_HOTKEY,  
      [ 
        lambda lt: lt._mainwindow.setNewInsertingPersonBikeType(DEFAULT_PERSONBIKE_TYPE_TOKEN),
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.setChecked(ANNOTATION_PERSONBIKE_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.onClassButtonPressed(ANNOTATION_PERSONBIKE_TOKEN),
      ],  GUI_PERSONBIKE_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.setChecked(ANNOTATION_VEHICLE_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.onClassButtonPressed(ANNOTATION_VEHICLE_TOKEN)
      ],  GUI_VEHICLE_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.setChecked(ANNOTATION_IGNORE_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.onClassButtonPressed(ANNOTATION_IGNORE_TOKEN)
      ],  GUI_IGNORE_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.property_editor2.setChecked(ANNOTATION_UPPER_BODY_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor2.onClassButtonPressed(ANNOTATION_UPPER_BODY_TOKEN)
      ],  GUI_UPPER_BODY_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.property_editor2.setChecked(ANNOTATION_LOWER_BODY_TOKEN, True),
        lambda lt: lt._mainwindow.property_editor2.onClassButtonPressed(ANNOTATION_LOWER_BODY_TOKEN)
      ],  GUI_LOWER_BODY_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.property_editor2.setChecked(ANNOTATION_HEAD_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor2.onClassButtonPressed(ANNOTATION_HEAD_TOKEN)
      ],  GUI_HEAD_BUTTON_TIP ),
#     (None,
#      [ lambda lt: lt._mainwindow.property_editor2.setChecked(ANNOTATION_FACE_TOKEN, True),
#        lambda lt: lt._mainwindow.property_editor2.onClassButtonPressed(ANNOTATION_FACE_TOKEN)
#      ],  GUI_FACE_BUTTON_TIP )
     (None,  
      [ lambda lt: lt._mainwindow.property_editor3.setChecked(ANNOTATION_UMBRELLA_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor3.onClassButtonPressed(ANNOTATION_UMBRELLA_TOKEN)
      ],  GUI_UMBRELLA_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.property_editor3.setChecked(ANNOTATION_BACKPACK_WIDGET_TOKEN, True),
        lambda lt: lt._mainwindow.property_editor3.onClassButtonPressed(ANNOTATION_BACKPACK_WIDGET_TOKEN)
      ],  GUI_BACKPACK_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.property_editor3.setChecked(ANNOTATION_CARRINGBAG_WIDGET_TOKEN, True),
        lambda lt: lt._mainwindow.property_editor3.onClassButtonPressed(ANNOTATION_CARRINGBAG_WIDGET_TOKEN)
      ],  GUI_CARRYINGBAG_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.property_editor3.setChecked(ANNOTATION_GLASSES_WIDGET_TOKEN, True),
        lambda lt: lt._mainwindow.property_editor3.onClassButtonPressed(ANNOTATION_GLASSES_WIDGET_TOKEN)
      ],  GUI_GLASSES_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.property_editor3.setChecked(ANNOTATION_HAT_WIDGET_TOKEN, True),
        lambda lt: lt._mainwindow.property_editor3.onClassButtonPressed(ANNOTATION_HAT_WIDGET_TOKEN)
      ],  GUI_HAT_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.property_editor3.setChecked(ANNOTATION_MASK_WIDGET_TOKEN, True),
        lambda lt: lt._mainwindow.property_editor3.onClassButtonPressed(ANNOTATION_MASK_WIDGET_TOKEN)
      ],  GUI_MASK_BUTTON_TIP ),                                    
     (None,  
      [ lambda lt: lt._mainwindow.property_editor3.setChecked(ANNOTATION_LUGGAGE_WIDGET_TOKEN, True),
        lambda lt: lt._mainwindow.property_editor3.onClassButtonPressed(ANNOTATION_LUGGAGE_WIDGET_TOKEN)
      ],  GUI_LUGGAGE_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.personbike_pannel.propertyEditorWidget.setChecked(ANNOTATION_HELMET_WIDGET_TOKEN, True), 
        lambda lt: lt._mainwindow.personbike_pannel.propertyEditorWidget.onClassButtonPressed(ANNOTATION_HELMET_WIDGET_TOKEN)
      ],  GUI_HELMET_BUTTON_TIP ),

     (GUI_INSERT_PERSONBIKE_TYPE_OF_LIGHT_MOTOR_HOTKEY,  
      [ 
        lambda lt: lt._mainwindow.setNewInsertingPersonBikeType(TAG_PERSONBIKE_TYPE_OF_LIGHTMOTOR_TOKEN),
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.setChecked(ANNOTATION_PERSONBIKE_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.onClassButtonPressed(ANNOTATION_PERSONBIKE_TOKEN),
      ],  GUI_INSERT_PERSONBIKE_TYPE_OF_LIGHT_MOTOR_TIP ),
     (GUI_INSERT_PERSONBIKE_TYPE_OF_MOTOR_HOTKEY,  
      [ 
        lambda lt: lt._mainwindow.setNewInsertingPersonBikeType(TAG_PERSONBIKE_TYPE_OF_MOTOR_TOKEN),
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.setChecked(ANNOTATION_PERSONBIKE_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.onClassButtonPressed(ANNOTATION_PERSONBIKE_TOKEN),
      ],  GUI_INSERT_PERSONBIKE_TYPE_OF_MOTOR_TIP ),
     (GUI_INSERT_PERSONBIKE_TYPE_OF_BICYCLE_HOTKEY,  
      [ 
        lambda lt: lt._mainwindow.setNewInsertingPersonBikeType(TAG_PERSONBIKE_TYPE_OF_BICYCLE_TOKEN),
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.setChecked(ANNOTATION_PERSONBIKE_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.onClassButtonPressed(ANNOTATION_PERSONBIKE_TOKEN),
      ],  GUI_INSERT_PERSONBIKE_TYPE_OF_BICYCLE_TIP ),
     (GUI_INSERT_PERSONBIKE_TYPE_OF_THREE_WHEEL_HOTKEY,  
      [ 
        lambda lt: lt._mainwindow.setNewInsertingPersonBikeType(TAG_PERSONBIKE_TYPE_OF_THREE_WHEEL_TOKEN),
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.setChecked(ANNOTATION_PERSONBIKE_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.onClassButtonPressed(ANNOTATION_PERSONBIKE_TOKEN),
      ],  GUI_INSERT_PERSONBIKE_TYPE_OF_THREE_WHEEL_TIP ),
     (GUI_INSERT_PERSONBIKE_TYPE_OF_UNKNOWN_HOTKEY,  
      [ 
        lambda lt: lt._mainwindow.setNewInsertingPersonBikeType(TAG_PERSONBIKE_TYPE_OF_UNKNOWN_TOKEN),
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.setChecked(ANNOTATION_PERSONBIKE_TOKEN, True), 
        lambda lt: lt._mainwindow.property_editor1.propertyEditorWidget.onClassButtonPressed(ANNOTATION_PERSONBIKE_TOKEN),
      ],  GUI_INSERT_PERSONBIKE_TYPE_OF_UNKNOWN_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.personbike_pannel.propertyEditorWidget.setChecked(ANNOTATION_LICENSE_PLATE_OPTION_WIDGET_TOKEN, True),
        lambda lt: lt._mainwindow.personbike_pannel.propertyEditorWidget.onClassButtonPressed(ANNOTATION_LICENSE_PLATE_OPTION_WIDGET_TOKEN)
      ],  GUI_PERSONBIKE_LICENSE_PLATE_BUTTON_TIP ),
     (None,  
      [ lambda lt: lt._mainwindow.personbike_pannel.propertyEditorWidget.setChecked(ANNOTATION_VEHICLE_LICENSE_PLATE_TOKEN, True),
        lambda lt: lt._mainwindow.personbike_pannel.propertyEditorWidget.onClassButtonPressed(ANNOTATION_VEHICLE_LICENSE_PLATE_TOKEN)
      ],  GUI_VEHICLE_LICENSE_PLATE_BUTTON_TIP ),
      
)




# CONTAINERS
#
# A list/tuple of two-tuples defining the mapping between filename pattern and
# annotation container classes.  The filename pattern can contain wildcards
# such as * and ?.  The corresponding container is expected to either a python
# class implementing the sloth container interface, or a module path pointing
# to such a class.
CONTAINERS = (
    ('*.json',       'sloth.annotations.container.JsonContainer'),
)

# PLUGINS
#
# A list/tuple of classes implementing the sloth plugin interface.  The
# classes can either be given directly or their module path be specified 
# as string.
PLUGINS = (
#    'sloth.plugins.__init__.CopyAnnotationsPlugin',
#    'sloth.plugins.__init__.CopyAnnotationsToAllOtherFrmsPlugin',
#    'sloth.plugins.__init__.CopySelectedAnnotationsToAllOtherFrmsPlugin',
     'sloth.plugins.__init__.MergeMultipleJsonFilesPlugin',
     'sloth.plugins.__init__.CleanDuplicateDataInJsonFilePlugin',
     'sloth.plugins.__init__.StatisticForCurJsonFilePlugin',
     'sloth.plugins.__init__.StatisticForMultipleJsonFilesPlugin',
     'sloth.plugins.__init__.CreateJsonForSpecificImgFolderPlugin',
     'sloth.plugins.__init__.SplitToMultipleJsonFilesPlugin',
)

# Range: [1, 3]
MAX_UPPER_COLOR_NUMBER                            = 3
# Range: [1, 3]
MAX_LOWER_COLOR_NUMBER                            = 3
# Range: [1, 30]
MAX_OPTIONS_NUMBER                                = 16
# Range: [1, 3]
MAX_CHECKED_OPTIONS_NUMBER                        = 1
# Range: [1, 3]
MAX_VEHICLE_COLOR_NUMBER                          = 3

# Range: [1, 500]
GUI_VIDEO_FRME_INTERVAL_MIN_VALUE                 = 1
# Range: [1, 5000]
GUI_VIDEO_FRME_INTERVAL_MAX_VALUE                 = 500
# Range: [1, 500]
GUI_VIDEO_FRME_INTERVAL_DEFAULT_VALUE             = 25

# Range: [1, 10]
GUI_LINE_MIN_LENGTH                               = 3
# Range: [1, 10]
GUI_RECT_MIN_WIDTH                                = 2
# Range: [1, 10]                                  
GUI_RECT_MIN_HEIGHT                               = 2

LOG_FILE_NAME                                     = "tst.log"

GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_WIDTH          = 500
GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_HEIGHT         = 300
GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_SLIDER_WIDTH   = 300
GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_SLIDER_HEIGHT  = 50
GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_LINEEDIT_WIDTH = 50
GUI_SET_VIDEO_FRAME_INTERAL_DIALOG_BUTTON_WIDTH   = 50

# Range: [0, 100]
GUI_MAX_SEPERATE_UPPER_COLOR_WIDGET_NUMBER        = 30
# Range: [0, 100]
GUI_MAX_SEPERATE_LOWER_COLOR_WIDGET_NUMBER        = 30
# Range: [0, 255]
GUI_COLOR_TAG_TEXT_BLACKWHITE_TOGGLE_THRESHOLD    = 40 
# Range: [0, 255]
GUI_MAX_SEPERATE_VEHICLE_COLOR_WIDGET_NUMBER      = 30

# Range: [0, 120]
GUI_WIDGET_MIN_WIDTH                              = 64


GUI_STATUS_BAR_DISPLAY_TIME_IN_MS                 = 5000


OPTION_ACTION_FITTOWIN_TOKEN                      = "Fit-to-window mode"
                                                  
                                                  
ORGANIZATION_DOMAIN                               = "www.1000video.cn"
VERSION                                           = "0.6.3"
VERSIONDESC                                       = "zx dev @ 20171019"                       


